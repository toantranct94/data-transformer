from traceback import format_exception

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.configs import settings
from app.exception.errors import AppError


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except AppError as e:
            logger.warning(
                f"Application error: {e.error_code} - {e.message}",
                extra={
                    "error_code": e.error_code,
                    "status_code": e.status_code,
                    "details": e.details,
                },
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "code": e.error_code,
                        "message": e.message,
                        "details": e.details,
                    }
                },
            )
        except Exception as e:
            error_traceback = "".join(format_exception(type(e), e, e.__traceback__))
            logger.error(
                f"Unexpected error: {str(e)}\nTraceback: {error_traceback}",
                extra={"path": request.url.path},
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": (
                            {"traceback": error_traceback} if settings.DEBUG else {}
                        ),
                    }
                },
            )
