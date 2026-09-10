import os
import json
import asyncio
import httpx
from typing import Dict, Any, List
from pydantic import ValidationError
from fastapi import HTTPException
from app.services.ai_provider import AIProvider
from app.services.gemma_client import AnalyzeResponseSchema, _repair_and_parse_json
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Interactions API: Google's current recommended endpoint. Unlike the older
# generateContent endpoint, this accepts newer "AQ."-prefixed auth keys
# (issued by AI Studio as of mid-2026) via the x-goog-api-key header.
# Passing an AQ. key as a ?key= query param on generateContent fails with
# "invalid authentication credentials" / random 500s, which is what this
# migration fixes.
GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_MODEL = "gemini-3.6-flash"

# Retry only on errors worth retrying: overload/rate-limit (429), and
# transient server-side failures (5xx). Auth/bad-request errors (4xx other
# than 429) are not retried since retrying won't fix them.
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3
_BASE_DELAY_SECONDS = 2.0

async def _post_with_retry(client: httpx.AsyncClient, url: str, payload: dict, headers: dict) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            res = await client.post(url, json=payload, headers=headers)
            if res.status_code in _RETRYABLE_STATUS_CODES and attempt < _MAX_RETRIES:
                delay = _BASE_DELAY_SECONDS * (2 ** attempt)
                logger.warning(
                    f"Gemini API returned {res.status_code}, retrying in {delay:.1f}s "
                    f"(attempt {attempt + 1}/{_MAX_RETRIES})"
                )
                await asyncio.sleep(delay)
                continue
            res.raise_for_status()
            return res
        except httpx.HTTPStatusError as e:
            last_exc = e
            break  # non-retryable status, raise_for_status already triggered
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            last_exc = e
            if attempt < _MAX_RETRIES:
                delay = _BASE_DELAY_SECONDS * (2 ** attempt)
                logger.warning(
                    f"Gemini API network error, retrying in {delay:.1f}s "
                    f"(attempt {attempt + 1}/{_MAX_RETRIES}): {e}"
                )
                await asyncio.sleep(delay)
                continue
            break
    raise last_exc

def _extract_text_from_steps(data: Dict[str, Any]) -> str:
    """Pull concatenated text out of an Interactions API response's steps list."""
    steps = data.get("steps", [])
    texts = []
    for step in steps:
        if step.get("type") != "model_output":
            continue
        for item in step.get("content", []):
            if item.get("type") == "text" and item.get("text"):
                texts.append(item["text"])
    return "".join(texts)

class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise HTTPException(
                status_code=400, 
                detail="Gemini API Key is missing. Please set GEMINI_API_KEY in .env to use the Gemini provider."
            )
        self._headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}

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
            "model": GEMINI_MODEL,
            "store": False,  # don't let Google retain uploaded-document content server-side
            "input": full_prompt,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                res = await _post_with_retry(client, GEMINI_INTERACTIONS_URL, payload, self._headers)
                data = res.json()

                result_text = _extract_text_from_steps(data)
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
        # Convert prior turns into Interactions API "input" steps.
        input_steps = []
        for msg in history:
            if msg["role"] == "system":
                continue
            elif msg["role"] == "user":
                input_steps.append({"type": "user_input", "content": msg["content"]})
            else:  # assistant/model
                input_steps.append({
                    "type": "model_output",
                    "content": [{"type": "text", "text": msg["content"]}]
                })

        input_steps.append({"type": "user_input", "content": new_message})

        payload = {
            "model": GEMINI_MODEL,
            "store": False,
            "input": input_steps,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                res = await _post_with_retry(client, GEMINI_INTERACTIONS_URL, payload, self._headers)
                data = res.json()
                reply = _extract_text_from_steps(data)
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
