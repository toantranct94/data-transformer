from pydantic import BaseModel, Field


class OkResponse(BaseModel):
    status: str = Field("ok")
