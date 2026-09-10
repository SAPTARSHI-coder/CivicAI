-- DDL for CivicAI Snowflake Integrations

CREATE TABLE IF NOT EXISTS ANALYSIS_SESSIONS (
    session_id VARCHAR PRIMARY KEY,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    filename VARCHAR,
    language VARCHAR,
    ai_provider VARCHAR,
    eligibility_status VARCHAR,
    checklist_item_count INT,
    missing_document_count INT,
    raw_result VARIANT
);

CREATE TABLE IF NOT EXISTS CHAT_MESSAGES (
    id VARCHAR PRIMARY KEY, -- Generate a UUID in Python
    session_id VARCHAR,
    role VARCHAR,
    message VARCHAR,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
