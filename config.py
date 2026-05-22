import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings and environment variables.
    """
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "mock-api-key-for-testing")
    db_path: str = os.getenv("DB_PATH", "sqlite:///./audit.db")
    debug: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    class Config:
        env_file = ".env"

settings = Settings()
