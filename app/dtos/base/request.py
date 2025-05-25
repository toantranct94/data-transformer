from typing import Optional

from pydantic import BaseModel, Field


class PaginateQueryParams(BaseModel):
    page_no: int = Field(default=1, ge=1, le=10000000000)
    page_size: int = Field(default=10, ge=1, le=100)
    query_text: Optional[str] = Field(default=None)
    query_by: Optional[str] = Field(default=None)
    order_by: Optional[str] = Field(default=None)


class CommonQueryDateTimeParams(PaginateQueryParams):
    start_date: Optional[str] = Field(
        default=None, alias="start_date", description="'YYYY-MM-DD' format"
    )
    end_date: Optional[str] = Field(
        default=None, alias="end_date", description="'YYYY-MM-DD' format"
    )
