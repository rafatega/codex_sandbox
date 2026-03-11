from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Tech Stocks API"
    app_version: str = "0.1.0"
    environment: str = Field(default="development")
    api_prefix: str = "/api/v1"
    streamlit_default_days: int = 90

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
