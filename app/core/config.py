from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY: str = "troque-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 dias

    CELERY_TASK_ALWAYS_EAGER: bool = True

    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url_compat(self) -> str:
        # Fix obrigatório para Railway: postgres:// → postgresql://
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


settings = Settings()
