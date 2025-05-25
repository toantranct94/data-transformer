from fastapi import APIRouter, status

from app.dtos.base import OkResponse

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse,
)
def health():
    """
    Check heath
    """
    return OkResponse()
