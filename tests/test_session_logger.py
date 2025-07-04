
import os
import json
from app.utils.session_logger import log_session_event, LOGS_DIR

def test_log_session_event():
    session_id = "test_session_123"
    log_file = os.path.join(LOGS_DIR, f"{session_id}.jsonl")

    # Clean up any previous log file
    if os.path.exists(log_file):
        os.remove(log_file)

    # Log a test event
    event = {"type": "test", "message": "Hello, world!"}
    log_session_event(session_id, event)

    # Verify the log file was created and contains the event
    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        log_entry = json.loads(f.read())
        assert log_entry["type"] == "test"
        assert log_entry["message"] == "Hello, world!"
        assert "timestamp" in log_entry

    # Clean up the log file
    os.remove(log_file)
