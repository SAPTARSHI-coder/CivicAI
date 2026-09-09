from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    @abstractmethod
    async def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Generates a JSON response matching the AnalyzeResponseSchema.
        """
        pass

    @abstractmethod
    async def chat(self, history: List[Dict[str, str]], new_message: str) -> str:
        """
        Processes a chat message given context history.
        """
        pass


def get_provider(provider_name: str) -> AIProvider:
    """Factory function to resolve the requested AI provider."""
    normalized = (provider_name or "").lower().strip()
    if normalized in ("gemini", "google-gemini", "gemini-api"):
        from app.services.gemini_provider import GeminiProvider
        return GeminiProvider()
    
    # Default to local Ollama (Gemma)
    from app.services.ollama_provider import OllamaProvider
    return OllamaProvider()

