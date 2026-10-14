"""FastAPI application entrypoint with lifespan event handling."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import CorrelactionIdMiddleware, ExceptionHandlerMiddleware
from app.core.config import settings
from app.infrastructure.logging.logger import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle events for startup and shutdown procedures."""
    setup_logging()
    logger.info(
        "Application startup sequence initiated",
        project_name=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
    )
    yield
    logger.info("Application shutdown completed successfully")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(CorrelactionIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return runtime service health status."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
