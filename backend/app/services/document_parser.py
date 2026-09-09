import io
from typing import Any, Optional
import pymupdf as fitz
from PIL import Image
from fastapi import UploadFile, HTTPException
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    import pytesseract
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False


async def parse_document(file_or_content: Any, filename: Optional[str] = None) -> str:
    """
    Parse an uploaded document (PDF or Image) and extract text.
    Uses PyMuPDF for PDFs. If text is near-empty, falls back to OCR via PyMuPDF pixmap + pytesseract
    (without requiring external Poppler binaries).
    For images, uses pytesseract.
    """
    if isinstance(file_or_content, UploadFile):
        content = await file_or_content.read()
        fname = (file_or_content.filename or "document").lower()
    else:
        content = file_or_content
        fname = (filename or "document").lower()

    if fname.endswith(".pdf"):
        return _parse_pdf(content)
    elif fname.endswith((".png", ".jpg", ".jpeg")):
        return _parse_image(content)
    else:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Please upload a PDF, PNG, or JPEG file."
        )


def _parse_pdf(content: bytes) -> str:
    final_text = ""
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()

            # Check if page has readable alphanumeric text
            has_alnum = any(c.isalnum() for c in page_text)

            if has_alnum:
                final_text += page_text + "\n"
            else:
                # Fallback to OCR for this specific scanned page
                logger.info(f"Page {page_num} lacks alphanumeric text. Attempting OCR fallback.")
                ocr_text = _ocr_pdf_page(page, page_num)
                if ocr_text:
                    final_text += ocr_text + "\n"
        doc.close()
    except Exception as e:
        logger.error(f"Failed to read PDF: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to read PDF document: {str(e)}")

    return final_text


def _ocr_pdf_page(page: fitz.Page, page_num: int) -> str:
    """Render PDF page directly using PyMuPDF and perform OCR if Tesseract is available."""
    if not _TESSERACT_AVAILABLE:
        logger.warning("OCR skipped: pytesseract is not available.")
        return ""

    try:
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img)
    except Exception as e:
        logger.warning(f"OCR fallback failed for page {page_num}: {e}")
        return ""


def _parse_image(content: bytes) -> str:
    if not _TESSERACT_AVAILABLE:
        raise HTTPException(
            status_code=501, 
            detail="Image OCR requires pytesseract and Tesseract-OCR installed on the system."
        )

    try:
        img = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logger.error(f"Image OCR failed: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Image OCR failed. Ensure the image is valid: {str(e)}"
        )
