import os
from typing import Optional

from pydantic_settings import BaseSettings


class GroqAISettings(BaseSettings):

    GROQ_AI_API_KEY: str = os.getenv("GROQ_AI_API_KEY", "")
    GROQ_AI_DEFAULT_MODEL: str = os.getenv(
        "GROQ_AI_DEFAULT_MODEL", "deepseek-r1-distill-llama-70b"
    )
    GROQ_AI_FALLBACK_MODEL: Optional[str] = os.getenv(
        "GROQ_AI_FALLBACK_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct"
    )
    GROQ_AI_MAX_RETRY_ATTEMPTS: int = int(os.getenv("GROQ_AI_MAX_RETRY_ATTEMPTS", "3"))
