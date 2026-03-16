from functools import lru_cache
from pathlib import Path
from typing import Annotated, List

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Project root (parent of backend/) so DB path is correct whether server runs from backend/ or root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Load .env before initializing settings to ensure override of system env vars
load_dotenv(_PROJECT_ROOT / ".env", override=True)


def _default_database_url() -> str:
    db_path = _PROJECT_ROOT / "data" / "drug_ra.db"
    return f"sqlite+aiosqlite:///{db_path.as_posix()}"


class Settings(BaseSettings):
    APP_NAME: str = "NeuroNext Regulatory Intelligence"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Default: SQLite under project root data/ (so same DB is used regardless of cwd)
    DATABASE_URL: str = _default_database_url()

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def _resolve_database_url(cls, v: str) -> str:
        # If .env or default uses relative path, resolve to project root so server always uses same DB
        if v and "drug_ra.db" in v and ("/./data/" in v or v.rstrip("/").endswith("data/drug_ra.db")):
            return _default_database_url()
        return v

    # CORS - comma-separated string in .env (NoDecode disables JSON parsing)
    CORS_ORIGINS: Annotated[List[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Vector / embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "data/vector_store"

    # AI provider keys (optional, ignore if not used)
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_BASE_URL: str | None = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"

    GOOGLE_API_KEY: str | None = None
    GOOGLE_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
