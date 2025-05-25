import os
from typing import List

from pydantic_settings import BaseSettings


class UploadSettings(BaseSettings):
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "uploads")
    MAX_FILE_SIZE: int = os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024)
    MAX_READ_CHUNK_BYTES: int = os.getenv("MAX_READ_CHUNK_BYTES", 100 * 1024)
    ALLOWED_FILE_EXTENSIONS: List[str] = os.getenv(
        "ALLOWED_FILE_EXTENSIONS", ".csv"
    ).split(",")
