from typing import Dict, Any, List
from app.services.ai_provider import AIProvider
from app.services.gemma_client import call_gemma_json, call_gemma_chat

class OllamaProvider(AIProvider):
    async def generate_json(self, prompt: str) -> Dict[str, Any]:
        return await call_gemma_json(prompt)
        
    async def chat(self, history: List[Dict[str, str]], new_message: str) -> str:
        return await call_gemma_chat(history, new_message)
