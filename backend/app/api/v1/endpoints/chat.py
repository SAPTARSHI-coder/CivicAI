from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.core.state import session_store
from app.services.snowflake_service import log_chat_message
from app.services.ai_provider import get_provider
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    provider: str = "gemma-local"


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    session_id = request.session_id

    if session_id not in session_store:
        raise HTTPException(
            status_code=404, 
            detail="Session not found or expired. Please upload and analyze a document first."
        )

    history = session_store[session_id]
    ai_service = get_provider(request.provider)

    try:
        # Call provider chat
        reply = await ai_service.chat(history, request.message)

        # Update history
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": reply})

        # Snowflake Integration: Log the chat exchange fail-softly in background
        background_tasks.add_task(log_chat_message, session_id, "user", request.message)
        background_tasks.add_task(log_chat_message, session_id, "assistant", reply)

        return ChatResponse(reply=reply)

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate chat response: {str(e)}"
        )

