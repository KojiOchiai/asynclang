import logging

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings using pydantic-settings."""

    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")
    mcp_server_urls: list[str] = Field(
        default_factory=list, description="List of MCP server URLs"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance - will automatically load from environment variables
settings = Settings()
logger.info(f"Settings loaded: {settings.model_dump()}")
