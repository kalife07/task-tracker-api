# config.py - loads environment variables from .env and exposes them
# as a typed Settings object used throughout the application.

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file into the process environment before Pydantic reads it.
load_dotenv()


class Settings(BaseSettings):
    """Application configuration derived from environment variables."""

    port: int = 8000
    app_env: str = "development"

    class Config:
        # Pydantic will also read from environment variables automatically.
        env_file = ".env"
        env_file_encoding = "utf-8"


# Single shared instance - import this anywhere you need config values.
settings = Settings()