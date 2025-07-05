# GitHub Issue: Implement comprehensive error logging to session JSONL files

## Feature Description
Currently, the application logs various session events (user messages, assistant responses, tool calls, etc.) to session-specific JSONL files in the `logs/` directory. However, backend errors and exceptions are not being logged to these session files, making it difficult to debug issues and understand what went wrong during a specific chat session.

## Problem Statement
When backend errors occur (like the 500 Internal Server Error in issue #4), there's no record of these errors in the session's JSONL log file. This makes debugging difficult because:

1. **No error context in session logs** - The session JSONL files only contain successful events
2. **Difficult debugging** - Developers have to correlate server logs with session IDs manually
3. **Poor error tracking** - No historical record of errors for specific sessions
4. **Limited troubleshooting** - Users and developers can't see what went wrong in a session

## Proposed Solution
Implement comprehensive error logging that captures all backend errors and exceptions to the appropriate session JSONL files.

### Error Types to Log
1. **HTTP Exceptions** - 400, 404, 500 errors, etc.
2. **LLM Client Errors** - API failures, timeout errors, invalid responses
3. **Tool Execution Errors** - Tool failures, invalid arguments, execution exceptions
4. **Database/Session Errors** - Session not found, data corruption, etc.
5. **Validation Errors** - Invalid request data, missing required fields
6. **General Python Exceptions** - Any unhandled exceptions

### Implementation Requirements

#### 1. Error Event Structure
Add a new event type for errors in the session logs:
```json
{
  "event": "error",
  "timestamp": "2025-01-05T20:34:29.123456Z",
  "error_type": "http_exception|llm_error|tool_error|validation_error|general_exception",
  "error_code": "500|400|404|etc",
  "error_message": "Human readable error message",
  "error_details": {
    "exception_type": "HTTPException",
    "traceback": "Full stack trace",
    "request_data": "Sanitized request data that caused the error",
    "context": "Additional context about what was happening when error occurred"
  },
  "endpoint": "/chat/{session_id}/message",
  "user_message": "The user message that triggered the error (if applicable)"
}
```

#### 2. Error Logging Function
Extend `app/utils/session_logger.py` with a new function:
```python
def log_session_error(session_id: str, error: Exception, error_type: str, context: dict = None):
    """
    Logs an error event to the session's JSONL file.
    
    Args:
        session_id: The ID of the session where the error occurred
        error: The exception object
        error_type: Type of error (http_exception, llm_error, tool_error, etc.)
        context: Additional context about the error
    """
```

#### 3. Error Handling Integration
Update all routers and services to log errors:

**In `app/routers/chat.py`:**
- Wrap the main chat endpoint in comprehensive error handling
- Log errors before raising HTTPExceptions
- Capture the user message that caused the error

**In `app/services/llm_client.py`:**
- Log LLM API errors with request/response details
- Log timeout and connection errors

**In `app/services/tool_manager.py`:**
- Log tool execution failures
- Log invalid tool arguments

**In `app/services/session_manager.py`:**
- Log session-related errors

#### 4. Global Error Handler
Implement a FastAPI exception handler to catch any unhandled exceptions:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Extract session_id from request if available
    # Log the error to session JSONL
    # Return appropriate error response
```

### Benefits
1. **Complete session history** - All events (success and failure) in one place
2. **Better debugging** - Developers can see exactly what went wrong in a session
3. **Error analytics** - Can analyze error patterns across sessions
4. **User support** - Support team can review session logs to help users
5. **Monitoring** - Can track error rates and types over time

### Files to Modify
- `app/utils/session_logger.py` - Add error logging function
- `app/routers/chat.py` - Add error handling and logging
- `app/routers/data.py` - Add error handling and logging  
- `app/routers/llm_configs.py` - Add error handling and logging
- `app/routers/theme.py` - Add error handling and logging
- `app/services/llm_client.py` - Add error logging
- `app/services/tool_manager.py` - Add error logging
- `app/services/session_manager.py` - Add error logging
- `app/main.py` - Add global exception handler

### Example Error Log Entry
```json
{
  "event": "error",
  "timestamp": "2025-01-05T20:34:29.123456Z",
  "error_type": "http_exception",
  "error_code": "500",
  "error_message": "Internal Server Error",
  "error_details": {
    "exception_type": "HTTPException",
    "traceback": "Traceback (most recent call last):\n  File...",
    "request_data": {
      "message": "Hello, world!",
      "tools": ["basic_math_tool"],
      "data_sources": [],
      "llm_config": {"name": "gpt-4"}
    },
    "context": "Error occurred while processing chat message"
  },
  "endpoint": "/chat/dc4365c2-ae25-4afe-ba97-9657b4b9ea00/message",
  "user_message": "Hello, world!"
}
```

## Priority
**Medium-High** - This will significantly improve debugging capabilities and error tracking.

## Labels
- enhancement
- logging
- debugging
- backend

---

**Instructions:** This issue should be implemented to improve error tracking and debugging capabilities across the application.
