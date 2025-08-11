from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using pydantic-settings."""

    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance - will automatically load from environment variables
settings = Settings()
