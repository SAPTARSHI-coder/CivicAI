import json
import uuid

try:
    import snowflake.connector
    _SNOWFLAKE_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SNOWFLAKE_AVAILABLE = False

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

def get_connection():
    if not _SNOWFLAKE_AVAILABLE or not settings.snowflake_configured:
        return None
    return snowflake.connector.connect(
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        account=settings.SNOWFLAKE_ACCOUNT,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
        role=settings.SNOWFLAKE_ROLE if settings.SNOWFLAKE_ROLE else None
    )

def log_analysis_session(session_id: str, filename: str, language: str, provider: str, result: dict) -> None:
    """
    Logs an analysis session to Snowflake. Fail-soft if Snowflake is unreachable.
    """
    if not settings.snowflake_configured:
        return
        
    try:
        eligibility = result.get("eligibility", {})
        eligibility_status = eligibility.get("status", "")
        checklist_count = len(result.get("checklist", []))
        missing_count = len(result.get("missing_documents", []))
        
        # We store raw_result as stringified JSON which Snowflake can parse into VARIANT
        # if using parse_json or directly if bound correctly
        raw_result_str = json.dumps(result)
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ANALYSIS_SESSIONS 
                    (session_id, filename, language, ai_provider, eligibility_status, checklist_item_count, missing_document_count, raw_result)
                    SELECT %s, %s, %s, %s, %s, %s, %s, PARSE_JSON(%s)
                    """,
                    (session_id, filename, language, provider, eligibility_status, checklist_count, missing_count, raw_result_str)
                )
    except Exception as e:
        logger.warning(f"Failed to log analysis session to Snowflake: {e}")

def log_chat_message(session_id: str, role: str, message: str) -> None:
    """
    Logs a single chat message to Snowflake. Fail-soft if Snowflake is unreachable.
    """
    if not settings.snowflake_configured:
        return
        
    try:
        msg_id = str(uuid.uuid4())
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO CHAT_MESSAGES
                    (id, session_id, role, message)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (msg_id, session_id, role, message)
                )
    except Exception as e:
        logger.warning(f"Failed to log chat message to Snowflake: {e}")
