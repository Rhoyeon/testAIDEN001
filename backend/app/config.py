"""Application configuration using pydantic-settings."""

from __future__ import annotations

import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str:
    """Find .env file in current dir or project root."""
    # Check current directory first
    if os.path.exists(".env"):
        return ".env"
    # Check project root (backend's parent directory)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        return env_path
    return ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AIDEN"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    api_v1_prefix: str = "/api/v1"

    # Dev mode: use SQLite + in-memory when Docker services are unavailable
    use_sqlite: bool = Field(default=False, description="Use SQLite instead of PostgreSQL for development")

    # Database
    database_url: str = "postgresql+asyncpg://aiden:aiden_dev_password@localhost:5432/aiden"
    database_sync_url: str = "postgresql://aiden:aiden_dev_password@localhost:5432/aiden"
    db_pool_size: int = 20
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8100

    # LLM Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-10-21"

    # LLM Defaults
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4.1"
    default_llm_temperature: float = 0.1

    # RAG
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Auth
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"])

    # File Storage
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def effective_database_url(self) -> str:
        """Return SQLite URL when use_sqlite is enabled, else PostgreSQL."""
        if self.use_sqlite:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            os.makedirs(db_dir, exist_ok=True)
            return f"sqlite+aiosqlite:///{db_dir}/aiden_dev.db"
        return self.database_url

    @property
    def effective_database_sync_url(self) -> str:
        """Return sync SQLite URL when use_sqlite is enabled, else PostgreSQL."""
        if self.use_sqlite:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
            os.makedirs(db_dir, exist_ok=True)
            return f"sqlite:///{db_dir}/aiden_dev.db"
        return self.database_sync_url


settings = Settings()
