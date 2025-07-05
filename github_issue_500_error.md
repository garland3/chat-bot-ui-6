# GitHub Issue: 500 Internal Server Error when sending chat messages to backend

## Bug Description
When attempting to send a chat message through the UI, the frontend receives a 500 Internal Server Error from the backend API.

## Error Details

### Frontend Console Error:
```
ApiService.js:10  POST http://localhost:8000/chat/dc4365c2-ae25-4afe-ba97-9657b4b9ea00/message 500 (Internal Server Error)
request @ ApiService.js:10
sendMessage @ ApiService.js:38
sendMessage @ Chat.js:100

ApiService.js:24 API request failed for /chat/dc4365c2-ae25-4afe-ba97-9657b4b9ea00/message: Error: HTTP error! status: 500
    at ApiService.request (ApiService.js:19:23)
    at async ChatManager.sendMessage (Chat.js:100:13)

Chat.js:112 Error sending message: Error: HTTP error! status: 500
    at ApiService.request (ApiService.js:19:23)
    at async ChatManager.sendMessage (Chat.js:100:13)
```

### Backend Server Log:
```
INFO:     127.0.0.1:54312 - "POST /chat/dc4365c2-ae25-4afe-ba97-9657b4b9ea00/message HTTP/1.1" 500 Internal Server Error
```

## Request Details
- **Method:** POST
- **URL:** `http://localhost:8000/chat/dc4365c2-ae25-4afe-ba97-9657b4b9ea00/message`
- **Status:** 500 Internal Server Error
- **Client IP:** 127.0.0.1:54312

## Code Context

### Error Flow:
1. **Chat.js:100** - `ChatManager.sendMessage()` calls `apiService.sendMessage()`
2. **ApiService.js:38** - `sendMessage()` method calls `this.request()`
3. **ApiService.js:19** - `request()` method throws error when `response.ok` is false
4. **Chat.js:112** - Error is caught and logged

### Request Payload Structure:
The frontend sends the following data structure:
```javascript
{
    message: content,
    tools: Array.from(tools),
    data_sources: Array.from(dataSources),
    llm_config: llmConfig
}
```

### Frontend Validation:
The frontend validates that:
- `appState.sessionId` exists
- `appState.selectedLLM` is selected
- Message content is not empty

## Expected Behavior
Chat messages should be successfully sent to the backend and processed without errors.

## Actual Behavior
The backend returns a 500 Internal Server Error, preventing chat messages from being sent.

## Environment
- **Frontend:** JavaScript/HTML
- **Backend:** FastAPI
- **Local development server:** http://localhost:8000
- **Session ID:** dc4365c2-ae25-4afe-ba97-9657b4b9ea00

## Investigation Needed
1. **Backend logs:** Check detailed backend logs for the specific error causing the 500 status
2. **Chat endpoint:** Verify the `/chat/{chat_id}/message` endpoint is properly handling POST requests
3. **Request validation:** Check if the request payload format matches expected schema
4. **Database operations:** Validate database connectivity and any database-related operations
5. **LLM integration:** Check if the error is related to LLM service calls
6. **Session validation:** Verify the session ID is valid and exists in the system

## Files Involved
- `static/js/services/ApiService.js` (lines 10, 19, 24, 38)
- `static/js/components/Chat.js` (lines 100, 112)
- Backend chat router (likely `app/routers/chat.py`)

## Priority
**High** - This prevents core chat functionality from working.

## Labels
- bug
- backend
- api
- high-priority
- 500-error

---

**Instructions:** Copy this content and create a new issue on GitHub at https://github.com/garland3/chat-bot-ui-6/issues/new
