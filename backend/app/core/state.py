from typing import Dict, List, Any

# In-memory store for session histories.
# Format: { "uuid": [ {"role": "user"|"assistant", "content": "..."} ] }
session_store: Dict[str, List[Dict[str, str]]] = {}

# In-memory store for uploaded document info per session.
# Format: { "uuid": {"url": "...", "public_id": "..."} | None }
document_store: Dict[str, Dict[str, Any] | None] = {}

