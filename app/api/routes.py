from fastapi import APIRouter

from app.api.endpoints import file_router, health_router, transform_router

router = APIRouter()

router.include_router(
    health_router,
    tags=["health"],
)

router.include_router(
    transform_router,
    tags=["transformations"],
    prefix="/transformations",
)


router.include_router(
    file_router,
    tags=["files"],
    prefix="/files",
)
