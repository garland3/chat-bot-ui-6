

import json
import os
from datetime import datetime, UTC
from app.config import settings

LOGS_DIR = "logs"

def log_session_event(session_id: str, event: dict):
    """
    Logs a session event to a .jsonl file.

    Args:
        session_id: The ID of the session.
        event: The event to log.
    """
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    # Prepend "test_" to log file name when running in test mode
    filename = f"test_{session_id}.jsonl" if settings.test_mode else f"{session_id}.jsonl"
    log_file = os.path.join(LOGS_DIR, filename)
    with open(log_file, "a") as f:
        event["timestamp"] = datetime.now(UTC).isoformat()
        f.write(json.dumps(event) + "\n")
