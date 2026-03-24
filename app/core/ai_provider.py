from abc import ABC, abstractmethod

from google import genai
from google.genai import types

from app.core.config import settings

DEFAULT_MODEL = "gemini-2.0-flash"  # modelo padrão


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512, tipo: str = "geral") -> str:
        raise NotImplementedError


class GeminiProvider(AIProvider):
    def __init__(self, model: str = DEFAULT_MODEL):
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = model

    def generate(self, prompt: str, max_tokens: int = 512, tipo: str = "geral") -> str:
        config_params: dict = {"max_output_tokens": max_tokens}
        if "2.5" in self._model:
            config_params["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_params),
        )

        usage = response.usage_metadata
        print(f"[AI] modelo={self._model} tipo={tipo} input={usage.prompt_token_count} output={usage.candidates_token_count}")

        return response.text.strip()


class _StubProvider(AIProvider):
    def generate(self, prompt: str, max_tokens: int = 512, tipo: str = "geral") -> str:
        return "[IA não configurada — adicione GEMINI_API_KEY ao .env]"


def _get_modelo_from_db(db=None) -> str:
    """Lê o modelo de IA da tabela config_sistema. Retorna DEFAULT_MODEL se não configurado."""
    if db is None:
        return DEFAULT_MODEL
    try:
        from app.models.config_sistema import ConfigSistema
        cfg = db.query(ConfigSistema).filter(ConfigSistema.chave == "modelo_ia").first()
        if cfg and cfg.valor:
            return cfg.valor
    except Exception:
        pass
    return DEFAULT_MODEL


def get_ai_provider(db=None) -> AIProvider:
    if not settings.GEMINI_API_KEY:
        return _StubProvider()
    model = _get_modelo_from_db(db)
    return GeminiProvider(model=model)
