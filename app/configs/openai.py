import os

from pydantic_settings import BaseSettings


class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_MAX_RETRY_ATTEMPTS: int = os.getenv("OPENAI_MAX_RETRY_ATTEMPTS", 3)
