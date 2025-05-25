import os

from dotenv import load_dotenv
from pydantic_settings import SettingsConfigDict

from app.configs.file import UploadSettings
from app.configs.groq_ai import GroqAISettings


class Settings(GroqAISettings, UploadSettings):
    APP_NAME: str = "backend"
    API_PREFIX: str
    ENV: str
    ALLOWED_ORIGINS: str = "*"
    DESCRIPTION: str = ""
    DEBUG: bool = False

    SettingsConfigDict(case_sensitive=True, env_file=".env")

    def __init__(self):
        super().__init__()


env = os.getenv("ENV")
if not env or env == "development":
    load_dotenv(".env", override=True)

settings = Settings()
