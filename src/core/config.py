"""
Configuration management for MCP Code Analyzer
"""
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""

    app_name: str = "MCP Code Analyzer"
    debug: bool = Field(default=False, env="DEBUG")

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://mcp_user:mcp_password@localhost:5432/mcp_db",
        env="DATABASE_URL"
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_RESULT_BACKEND"
    )

    # AI/ML
    model_cache_dir: str = Field(
        default="/tmp/mcp_models",
        env="MODEL_CACHE_DIR"
    )
    embedding_model: str = Field(
        default="microsoft/codebert-base",
        env="EMBEDDING_MODEL"
    )

    # ChromaDB
    chroma_persist_dir: str = Field(
        default="/tmp/mcp_chroma",
        env="CHROMA_PERSIST_DIR"
    )

    # Analysis settings
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    analysis_timeout: int = Field(default=300, env="ANALYSIS_TIMEOUT")
    max_concurrent_analyses: int = Field(default=4, env="MAX_CONCURRENT_ANALYSES")

    # Security
    secret_key: str = Field(
        default="SECRET_KEY",
        env="SECRET_KEY"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()