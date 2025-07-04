

import json
import os
from datetime import datetime, UTC

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

    log_file = os.path.join(LOGS_DIR, f"{session_id}.jsonl")
    with open(log_file, "a") as f:
        event["timestamp"] = datetime.now(UTC).isoformat()
        f.write(json.dumps(event) + "\n")
