import os
import json
import httpx
from typing import Dict, Any, List
from pydantic import ValidationError
from fastapi import HTTPException
from app.services.ai_provider import AIProvider
from app.services.gemma_client import AnalyzeResponseSchema, _repair_and_parse_json
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise HTTPException(
                status_code=400, 
                detail="Gemini API Key is missing. Please set GEMINI_API_KEY in .env to use the Gemini provider."
            )
            
    async def generate_json(self, prompt: str) -> Dict[str, Any]:
        full_prompt = (
            f"{prompt}\n\n"
            "You MUST output valid JSON. No markdown formatting block (like ```json), no preamble, no trailing text. "
            "Just the raw JSON object matching this schema:\n"
            "{\n"
            '  "explanation": "string",\n'
            '  "eligibility": {"status": "likely|action-needed|confirmed", "text": "string"},\n'
            '  "checklist": ["string", "string"],\n'
            '  "missing_documents": ["string", "string"]\n'
            "}\n"
        )
        
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}]
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                res = await client.post(f"{GEMINI_API_URL}?key={self.api_key}", json=payload)
                res.raise_for_status()
                data = res.json()
                
                # Extract text across all parts (handles thinking parts or split text)
                candidates = data.get("candidates", [])
                if not candidates:
                    raise ValueError("No candidates returned by Gemini API.")
                parts = candidates[0].get("content", {}).get("parts", [])
                result_text = "".join(p.get("text", "") for p in parts if p.get("text"))
                if not result_text:
                    raise ValueError("Empty response text from Gemini API.")
                
                # Attempt to parse and validate
                parsed = _repair_and_parse_json(result_text)
                AnalyzeResponseSchema(**parsed)
                return parsed
            except Exception as e:
                logger.error(f"Gemini API JSON generation failed: {e}")
                err_detail = "Failed to generate valid response from Gemini API."
                if hasattr(e, 'response') and e.response:
                    try:
                        err_json = e.response.json()
                        err_detail = err_json.get("error", {}).get("message", err_detail)
                    except Exception:
                        pass
                raise HTTPException(status_code=500, detail=err_detail)

    async def chat(self, history: List[Dict[str, str]], new_message: str) -> str:
        # Convert history format
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            if msg["role"] == "system":
                continue
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        contents.append({
            "role": "user",
            "parts": [{"text": new_message}]
        })
        
        payload = {"contents": contents}
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                res = await client.post(f"{GEMINI_API_URL}?key={self.api_key}", json=payload)
                res.raise_for_status()
                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise ValueError("No candidates returned by Gemini API.")
                parts = candidates[0].get("content", {}).get("parts", [])
                reply = "".join(p.get("text", "") for p in parts if p.get("text"))
                return reply
            except Exception as e:
                logger.error(f"Gemini API chat failed: {e}")
                err_detail = "Failed to get chat response from Gemini API."
                if hasattr(e, 'response') and e.response:
                    try:
                        err_json = e.response.json()
                        err_detail = err_json.get("error", {}).get("message", err_detail)
                    except Exception:
                        pass
                raise HTTPException(status_code=500, detail=err_detail)
