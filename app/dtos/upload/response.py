from typing import List

from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    filename: str
    status: str
    errors: List[str] = []
