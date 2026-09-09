"""Liveness probe."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
async def health() -> dict:
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "providers": {
            "gemini": settings.gemini_configured,
            "ollama_local": True,
        },
        "integrations": {
            "cloudinary": settings.cloudinary_configured,
            "snowflake": settings.snowflake_configured,
        },
    }



@router.get("/live", status_code=status.HTTP_204_NO_CONTENT, summary="Kubernetes liveness")
async def live() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
