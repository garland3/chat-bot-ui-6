import os
import json
from app.utils.session_logger import log_session_event, LOGS_DIR
from app.config import settings


def test_log_session_event():
    session_id = "test_session_123"
    # In test mode, the log file should have "test_" prefix
    log_file = os.path.join(LOGS_DIR, f"test_{session_id}.jsonl")

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

def test_log_session_event_test_mode():
    """Test that log files are prefixed with 'test_' when in test mode"""
    session_id = "mode_test_123"
    
    # Ensure we're in test mode (should be set by conftest.py)
    assert settings.test_mode == True
    
    # Expected log file with test prefix
    expected_log_file = os.path.join(LOGS_DIR, f"test_{session_id}.jsonl")
    # File without test prefix should not be created
    normal_log_file = os.path.join(LOGS_DIR, f"{session_id}.jsonl")
    
    # Clean up any previous log files
    for file_path in [expected_log_file, normal_log_file]:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Log an event
    event = {"type": "test_mode", "message": "Testing test mode"}
    log_session_event(session_id, event)
    
    # Verify the correct file was created
    assert os.path.exists(expected_log_file), "Log file with test_ prefix should exist"
    assert not os.path.exists(normal_log_file), "Log file without test_ prefix should not exist"
    
    # Verify content
    with open(expected_log_file, "r") as f:
        log_entry = json.loads(f.read())
        assert log_entry["type"] == "test_mode"
        assert log_entry["message"] == "Testing test mode"
    
    # Clean up
    os.remove(expected_log_file)

def test_log_session_event_normal_mode():
    """Test that log files are not prefixed when not in test mode"""
    session_id = "normal_mode_test_123"
    
    # Temporarily disable test mode
    original_test_mode = settings.test_mode
    settings.test_mode = False
    
    try:
        # Expected log file without test prefix
        expected_log_file = os.path.join(LOGS_DIR, f"{session_id}.jsonl")
        # File with test prefix should not be created
        test_log_file = os.path.join(LOGS_DIR, f"test_{session_id}.jsonl")
        
        # Clean up any previous log files
        for file_path in [expected_log_file, test_log_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Log an event
        event = {"type": "normal_mode", "message": "Testing normal mode"}
        log_session_event(session_id, event)
        
        # Verify the correct file was created
        assert os.path.exists(expected_log_file), "Log file without test_ prefix should exist"
        assert not os.path.exists(test_log_file), "Log file with test_ prefix should not exist"
        
        # Verify content
        with open(expected_log_file, "r") as f:
            log_entry = json.loads(f.read())
            assert log_entry["type"] == "normal_mode"
            assert log_entry["message"] == "Testing normal mode"
        
        # Clean up
        os.remove(expected_log_file)
        
    finally:
        # Restore test mode
        settings.test_mode = original_test_mode
