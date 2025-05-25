import os
import re
from urllib.parse import unquote

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.configs import settings
from app.middlewares.error import ErrorHandlerMiddleware
from app.middlewares.security import SecurityMiddleware


def init_services():
    os.environ["GROQ_API_KEY"] = settings.GROQ_AI_API_KEY


def get_application():
    init_services()
    _app = FastAPI(
        title=settings.APP_NAME,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
    )
    _app.include_router(router, prefix=settings.API_PREFIX)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "x-credit-remaining",
            "x-credit-quota",
        ],
    )
    _app.add_middleware(ErrorHandlerMiddleware)
    _app.add_middleware(SecurityMiddleware)

    @_app.middleware("http")
    async def validate_path_middleware(request: Request, call_next):
        try:
            decoded_path = unquote(request.url.path)
            if not re.match(r"^[a-zA-Z0-9/\-_.]*$", decoded_path):
                return JSONResponse(
                    status_code=404,
                    content={"detail": "Not Found"},
                )
        except Exception:
            raise HTTPException(status_code=404, detail="Not Found")
        return await call_next(request)

    _app.add_exception_handler(HTTPException, invalid_path_exception_handler)

    return _app


async def invalid_path_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app = get_application()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
