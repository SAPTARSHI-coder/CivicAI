import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.services.document_parser import parse_document
from app.services.cloudinary_service import upload_document
from app.services.snowflake_service import log_analysis_session
from app.services.ai_provider import get_provider
from app.core.state import session_store, document_store
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("")
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form("English"),
    provider: str = Form("gemma-local"),
):
    # 1. Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    # Generate session ID early so both Cloudinary and session storage share the exact same ID
    session_id = str(uuid.uuid4())
    filename = file.filename or "document"

    # Cloudinary upload (fail-soft)
    upload_result = upload_document(content, filename, session_id)

    # 2. Extract text (PyMuPDF with OCR fallback)
    try:
        extracted_text = await parse_document(content, filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to parse document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400, 
            detail="Could not extract any readable text from the document. Please provide a clear PDF or image."
        )

    # 3. Construct prompt
    prompt = f"""You are CivicAI, an intelligent public service assistant. Your job is to analyse official Indian government documents, citizen identity documents/certificates (e.g. Aadhaar Card, Ration Card, PAN Card, Voter ID, Income/Caste Certificate, Land Records), and government welfare schemes.

SCOPE INSTRUCTION:
- ACCEPT: Indian government schemes, official notices, and citizen identity documents/certificates (including Aadhaar Card, Ration Card, Voter ID, Income/Caste Certificate, Land Records).
- REJECT ONLY: Entirely non-governmental or off-topic content (such as election vote counts, political party campaigning, news articles, shopping invoices, entertainment, or spam).

Document Text:
---
{extracted_text}
---

Perform the following tasks based on the document text:
1. Explain what this document is and what it says in plain language (for citizen documents like an Aadhaar Card, identify the card holder, issuing authority, proof purpose, and key advisories printed on it).
2. Assess the citizen's eligibility: explain what government welfare schemes, public services, and entitlements this document connects to or qualifies them for (e.g., DBT subsidies, welfare schemes, Jan Dhan, Ration, scholarships).
3. Provide a step-by-step checklist of actionable steps the citizen needs to take (e.g. keeping contact details updated, biometric locking in mAadhaar, 10-year document re-validation, bank DBT linking, application procedures).
4. List any missing documents or supplementary paperwork needed to claim full welfare benefits.

IMPORTANT: Translate the ENTIRE response into {language}.
IMPORTANT: Base your analysis on the document text and authentic Indian public service procedures. Do NOT discuss politics or election results.
"""

    # 4. Call Provider
    ai_service = get_provider(provider)
    try:
        result = await ai_service.generate_json(prompt)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"JSON generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze document with {provider} AI: {str(e)}",
        )

    # 5. Store session history and uploaded document reference
    session_store[session_id] = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": str(result)},
    ]
    document_store[session_id] = upload_result

    # Snowflake Integration: Log the session fail-softly in background
    background_tasks.add_task(
        log_analysis_session,
        session_id,
        filename,
        language,
        provider,
        result,
    )

    # 6. Return exact expected schema + session_id + document_url
    result["session_id"] = session_id
    result["document_url"] = upload_result.get("url") if upload_result else None

    return result

