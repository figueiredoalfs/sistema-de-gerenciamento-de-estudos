from abc import ABC, abstractmethod

from google import genai
from google.genai import types

from app.core.config import settings


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        raise NotImplementedError


class GeminiProvider(AIProvider):
    def __init__(self):
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        response = self._client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        return response.text.strip()


class _StubProvider(AIProvider):
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        return "[IA não configurada — adicione GEMINI_API_KEY ao .env]"


def get_ai_provider() -> AIProvider:
    if not settings.GEMINI_API_KEY:
        return _StubProvider()
    return GeminiProvider()
