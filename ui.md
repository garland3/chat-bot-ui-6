# UI Functional Description

## Overview
This is a chat application interface that allows users to interact with AI assistants through a web-based chat interface with tool selection capabilities.

## Core Functionality

### HTML Structure (`index.html`)
- **Main Layout**: Single-page application with header, chat area, and input section
- **Header Components**:
  - Application title and connection status indicator
  - "New Chat" button for starting fresh conversations
  - Tool selector dropdown with checkboxes for various tools (Basic Math, Code Execution, User Lookup, SQL Query)
  - LLM/AI model selector dropdown
  - Download chat button
  - User info display
- **Chat Area**: 
  - Welcome message with suggested prompts when no conversation is active
  - Message display area for conversation history
  - Scrollable container for long conversations
- **Input Section**:
  - Multi-line text input with auto-resize capability
  - File attachment button (placeholder)
  - Send message button
- **UI Elements**:
  - Toast notification container for status messages
  - Loading overlay for processing states
  - Debug panel (hidden by default) for development

### JavaScript Functionality (`app.js`)
- **WebSocket Communication**:
  - Establishes real-time connection to backend server
  - Handles session management and message routing
  - Automatic reconnection on connection loss
  - Processes various message types (session_id, status, thinking, tool_call, error)

- **Session Management**:
  - Creates new chat sessions via POST to `/chat` endpoint
  - Maintains session state and ID
  - Handles session initialization through WebSocket

- **Message Handling**:
  - Sends user messages to backend via POST to `/chat/{session_id}/message`
  - Processes streaming responses from AI
  - Displays messages with proper formatting (Markdown support)
  - Manages typing indicators and streaming message updates

- **Tool Integration**:
  - Allows users to select which tools the AI can access
  - Sends tool selections with each message
  - Provides visual feedback when tools are being used

- **LLM Configuration**:
  - Fetches available AI models from `/api/llm_configs`
  - Allows users to select which AI model to use
  - Sends model preference with messages

- **UI Interactions**:
  - Auto-resizing text input
  - Keyboard shortcuts (Enter to send, Shift+Enter for new line)
  - Copy-to-clipboard functionality for code blocks
  - Toast notifications for user feedback
  - Chat history download functionality

- **State Management**:
  - Tracks connection status
  - Manages typing states
  - Handles loading states
  - Maintains current streaming message references

### CSS Styling (`styles.css`)
- **Design System**:
  - CSS custom properties for consistent theming
  - Light/dark mode support via media queries
  - Responsive design for mobile and desktop
  - Modern color palette and typography

- **Layout Management**:
  - Flexbox-based layout system
  - Fixed header with scrollable content area
  - Responsive grid for tool selection
  - Proper z-index layering for dropdowns and overlays

- **Interactive Elements**:
  - Hover states and transitions
  - Focus management for accessibility
  - Loading animations and spinners
  - Toast notification animations

- **Message Display**:
  - Distinct styling for user vs assistant messages
  - Code block highlighting with copy buttons
  - Markdown rendering support
  - Typing cursor animation for streaming responses

## Key Features

1. **Real-time Communication**: WebSocket-based chat with immediate response streaming
2. **Tool Selection**: Users can enable/disable AI tools per conversation
3. **Model Selection**: Choice of different AI models for responses
4. **Session Management**: Persistent chat sessions with download capability
5. **Responsive Design**: Works on desktop and mobile devices
6. **Accessibility**: Keyboard navigation and screen reader support
7. **Error Handling**: Graceful error recovery and user feedback
8. **Development Tools**: Debug panel for troubleshooting

## API Integration

- **Chat Session Creation**: `POST /chat`
- **Message Sending**: `POST /chat/{session_id}/message`
- **LLM Configuration**: `GET /api/llm_configs`
- **Chat Download**: `GET /chat/{session_id}/download`
- **WebSocket Connection**: `ws://host/ws`

## Data Flow

1. User loads page → Establishes WebSocket connection
2. User starts new chat → Creates session via API → Receives session ID
3. User selects tools/model → Preferences stored in UI state
4. User sends message → Posted to API with tool/model preferences
5. Backend processes → Streams response via WebSocket
6. UI displays streaming response → Handles completion and formatting
7. User can download conversation history or start new session

## Configuration

- Application name and settings configurable via `window.appConfig`
- LLM configurations loaded dynamically from backend
- Tool availability configured in HTML template
- Styling customizable through CSS custom properties
