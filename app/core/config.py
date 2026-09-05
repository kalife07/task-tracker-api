# config.py - loads environment variables from .env and exposes them
# as a typed Settings object used throughout the application.

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file into the process environment before Pydantic reads it.
load_dotenv()

# Anchor the default storage locations to the package directory so they
# resolve the same way no matter which working directory the server was
# started from.
_APP_DIR = Path(__file__).resolve().parents[1]

DEFAULT_STORAGE_PATH = _APP_DIR / "storage" / "storage.json"
DEFAULT_TEST_STORAGE_PATH = _APP_DIR / "storage" / "storage.test.json"


class Settings(BaseSettings):
    """Application configuration derived from environment variables."""

    port: int = 8000
    app_env: str = "development"
    # Optional override for where tasks are persisted (env: STORAGE_FILE).
    # Relative paths are resolved against the current working directory.
    storage_file: Optional[str] = None

    class Config:
        # Pydantic will also read from environment variables automatically.
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def storage_path(self) -> Path:
        """The JSON file that task storage is persisted to.

        Returns:
            Path: ``storage_file`` when it is set, otherwise
            ``app/storage/storage.test.json`` under ``APP_ENV=test`` and
            ``app/storage/storage.json`` in every other environment. The
            separate test default keeps test runs from touching real data.
        """
        if self.storage_file:
            return Path(self.storage_file).expanduser()
        if self.app_env == "test":
            return DEFAULT_TEST_STORAGE_PATH
        return DEFAULT_STORAGE_PATH


# Single shared instance - import this anywhere you need config values.
settings = Settings()
