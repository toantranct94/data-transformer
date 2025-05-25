from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if not await self._check_rate_limit(request):
            raise HTTPException(status_code=429, detail="Too many requests")

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

    async def _check_rate_limit(self, request: Request) -> bool:
        # TODO: Implement rate limiting
        return True
