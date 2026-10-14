"""HTTP middlewares for correlation tracking and exception handling."""

import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AgentBuilderError, ResourceNotFoundError
from app.infrastructure.logging.logger import logger


class CorrelactionIdMiddleware(BaseHTTPMiddleware):
    """Injects or propagates correlation IDs across request execution paths."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process incoming request and attach correlation identifier to context vars."""

        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id, path=request.url.path, method=request.method
        )

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Global middleware to translate domain exceptions into structured JSON errors."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Intercept unhandled exceptions and format standardized JSON errors."""
        try:
            return await call_next(request)

        except ResourceNotFoundError as exc:
            logger.warning("Resource not found", error=exc.message, details=exc.details)
            return JSONResponse(
                status_code=404,
                content={
                    "error": "ResourceNotFound",
                    "message": exc.message,
                    "details": exc.details,
                },
            )
        except AgentBuilderError as exc:
            logger.error("Domain exception encountered", error=exc.message, details=exc.details)
            return JSONResponse(
                status_code=400,
                content={
                    "error": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                },
            )
        except Exception as exc:
            logger.exception("Unhandled internal server error occurred", exc_info=exc)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "InternalServerError",
                    "message": "An unexpected error occurred.",
                },
            )
