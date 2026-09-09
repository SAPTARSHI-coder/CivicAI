"""Aggregate router for API v1."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import health, analyze, chat, samples

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(samples.router)

