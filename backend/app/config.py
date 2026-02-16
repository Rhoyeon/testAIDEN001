"""Application configuration using pydantic-settings."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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

    # Database
    database_url: str = "postgresql+asyncpg://aiden:aiden_dev_password@localhost:5432/aiden"
    database_sync_url: str = "postgresql://aiden:aiden_dev_password@localhost:5432/aiden"
    db_pool_size: int = 20
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000

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
    cors_origins: List[str] = Field(default=["http://localhost:3000"])

    # File Storage
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
