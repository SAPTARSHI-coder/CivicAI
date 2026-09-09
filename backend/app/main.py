"""Application factory and ASGI entrypoint.

Run locally with:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.middleware.request_context import RequestContextMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage startup and shutdown resources."""
    configure_logging()
    logger.info("application.startup", env=settings.ENVIRONMENT, version=settings.VERSION)
    yield
    logger.info("application.shutdown")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.ENABLE_DOCS else None,
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_DOCS else None,
        lifespan=lifespan,
    )

    # Middleware (order matters — outermost first).
    app.add_middleware(RequestContextMiddleware)
    
    # We allow the specific frontend ports plus whatever is in settings
    origins = settings.cors_origins + ["http://localhost:5173", "http://localhost:3000"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
