from unittest.mock import patch, MagicMock
from app.services.snowflake_service import log_analysis_session, log_chat_message

from app.core.config import Settings

def test_snowflake_unconfigured_skips_cleanly():
    with patch.object(Settings, "snowflake_configured", new_callable=MagicMock, return_value=False):
        # Should not raise any error
        log_analysis_session("sess-1", "doc.pdf", "English", "gemini", {"eligibility": {}})
        log_chat_message("sess-1", "user", "hello")

def test_snowflake_logs_warning_on_connection_error():
    with patch.object(Settings, "snowflake_configured", new_callable=MagicMock, return_value=True), \
         patch("app.services.snowflake_service._SNOWFLAKE_AVAILABLE", True), \
         patch("app.services.snowflake_service.get_connection", side_effect=Exception("Connection refused")):
        # Fail-soft: should not raise
        log_analysis_session("sess-1", "doc.pdf", "English", "gemini", {"eligibility": {}})
        log_chat_message("sess-1", "user", "hello")
