"""Cloudinary document storage service for CivicAI."""

from __future__ import annotations

import io
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import cloudinary
    import cloudinary.uploader
    _CLOUDINARY_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CLOUDINARY_AVAILABLE = False

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def upload_document(
    content: bytes,
    filename: str,
    session_id: str,
) -> Optional[Dict[str, Any]]:
    """Upload an uploaded document to Cloudinary storage.

    Configures Cloudinary credentials from settings, organizes files by session ID
    (civicai/{session_id}), and sanitizes the original filename for use as the public_id.

    This function never raises an exception: if Cloudinary is unconfigured or if any
    network/SDK error occurs, it logs a warning via structlog and returns None.

    Args:
        content: Raw document bytes.
        filename: Original file name.
        session_id: The session UUID string.

    Returns:
        {"url": <secure_url>, "public_id": <public_id>} on success, or None on failure.
    """
    if not settings.cloudinary_configured:
        logger.warning(
            "cloudinary.skipped",
            reason="Cloudinary credentials are not configured",
            session_id=session_id,
        )
        return None

    if not _CLOUDINARY_AVAILABLE:
        logger.warning(
            "cloudinary.missing_dependency",
            reason="Cloudinary package is not available",
            session_id=session_id,
        )
        return None

    try:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )

        base_name = os.path.basename((filename or "document").replace("\\", "/"))
        clean_stem = Path(base_name).stem
        sanitized_stem = re.sub(r"[^\w\-.]", "_", clean_stem).strip("._") or "document"
        folder = f"civicai/{session_id}"

        response = cloudinary.uploader.upload(
            io.BytesIO(content),
            folder=folder,
            public_id=sanitized_stem,
            resource_type="auto",
        )

        secure_url = response.get("secure_url") or response.get("url")
        public_id = response.get("public_id")

        return {
            "url": secure_url,
            "public_id": public_id,
        }
    except Exception as e:
        logger.warning(
            "cloudinary.upload_error",
            error=str(e),
            filename=filename,
            session_id=session_id,
        )
        return None
