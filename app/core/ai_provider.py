from abc import ABC, abstractmethod

from google import genai
from google.genai import types

from app.core.config import settings


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiProvider(AIProvider):
    def __init__(self):
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=512),
        )
        return response.text.strip()


def get_ai_provider() -> AIProvider:
    return GeminiProvider()
