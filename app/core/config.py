import warnings

from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT = "troque-em-producao"


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY: str = _INSECURE_DEFAULT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60        # 1 hora
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30          # 30 dias

    CELERY_TASK_ALWAYS_EAGER: bool = True

    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    ADMIN_EMAIL: str = "admin@skolai.com"
    ADMIN_SENHA: str = "admin123"
    ADMIN_NOME: str = "Admin"

    # CORS: domínios permitidos separados por vírgula.
    # Em produção, defina apenas o domínio do frontend, ex:
    # ALLOWED_ORIGINS=https://skolai.railway.app
    ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url_compat(self) -> str:
        # Fix obrigatório para Railway: postgres:// → postgresql://
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        # Railway PostgreSQL exige SSL
        if url.startswith("postgresql://") and "sslmode" not in url:
            url += "?sslmode=require"
        return url


settings = Settings()

if settings.SECRET_KEY == _INSECURE_DEFAULT and not settings.DATABASE_URL.startswith("sqlite"):
    raise RuntimeError("SECRET_KEY não pode ser o valor padrão em produção. Defina SECRET_KEY no ambiente.")
