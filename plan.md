# Chat Data MCP Tools UI - Project Plan

## Project Overview

A modern chatbot UI application built with FastAPI backend and responsive frontend. The application provides an intelligent chat interface that integrates with OpenAI-compatible APIs and supports tool calling and data source integration.

## Architecture

### Backend (FastAPI)

- **Framework**: FastAPI with modular router structure
- **LLM Integration**: OpenAI-compatible API using requests library (not OpenAI SDK)
- **Communication**: WebSocket connections for real-time chat
- **Authentication**: Reverse proxy authentication via X-EMAIL-USER header
- **Session Management**: In-memory storage with unique session IDs
- **Logging**: JSONL files per session with comprehensive error tracking

### Frontend

- **Design**: Dark theme, responsive design
- **Static Assets**: Served from static folder (no Jinja templates)
- **Real-time Updates**: WebSocket communication for status updates
- **User Feedback**: Toast notifications (no alerts), feedback collection

## Core Features

### 1. Authentication & Authorization

- **Authentication**: Reverse proxy sets X-EMAIL-USER header
- **Test Mode**: Configurable test email (`test@test.com`) via environment variable
- **Access Control**: Modular permission system for tools and data sources
- **Rate Limiting**: One active session per user maximum

### 2. Chat Interface

- **Regular Chat**: Streaming responses from LLM API
- **Tool Integration**: Users can select N tools and M data sources per chat
- **Status Updates**: Real-time progress indicators via WebSocket
- **Thinking Messages**: Periodic status updates for long-running tasks (every 5 seconds)

### 3. Tools System

Tools as configuration parameters that modify LLM behavior:

1. **Calculator Tool**: Demo tool that modifies system prompt for mathematical operations
2. **Future Tools**: Placeholder for additional tool configurations

**Tool Features**:

- Tool selection sent as extra arguments to backend
- Tool selection modifies system prompt and execution path
- Tool selections logged and streamed to frontend (e.g., "tool:selected calculator")
- No actual tool execution - future-proofing for custom workflows
- Modular design in `tools/` folder for tool definitions

### 4. Data Sources

- **Current**: Configuration parameters sent to backend
- **Future**: Custom RAG system integration
- **Behavior**: Data sources sent as extra arguments, streaming responses maintained
- **Future-Proofing**: Placeholder for advanced data source workflows

## Technical Requirements

### Configuration

- **Framework**: Pydantic settings with extra field support
- **Environment Variables**:
  - LLM API base URL, API key, model name
  - Test mode configuration
  - Feature toggles for testing

### Security

- **Input Sanitization**: Prevent injection attacks
- **Authentication Middleware**: All routes protected
- **SQL Safety**: Read-only database access
- **Tool Timeouts**: Prevent infinite execution

### Code Quality

- **File Size Limit**: Maximum 300 lines per file
- **Modularity**: Separation of concerns, reusable components
- **Clean Code**: Maintainable and scalable architecture

### Error Handling

- **Comprehensive Logging**: Session logs with tracebacks
- **Health Checks**: Startup LLM connectivity test ("hi" prompt, 3 max tokens)
- **Graceful Degradation**: UI notifications when LLM unavailable
- **User Feedback**: Error reporting and experience feedback

## Development Setup

### Docker & DevContainer

- **Production**: Docker container for deployment
- **Development**: DevContainer configuration for consistent environment

### Testing Strategy

- **Unit Tests**: pytest framework
- **API Testing**: httpx for FastAPI endpoint testing
- **Async Testing**: pytest-asyncio for asynchronous code
- **Test Configuration**: Environment variables to disable WebSocket/LLM features during testing

### Dependencies

- **Python Version**: Python 3.12 (as used in Dockerfile)
- **Package Manager**: uv (ultrafast Python package installer and resolver) Always use `uv pip install`
- **Virtual Environment**: uv-managed virtual environment
- **Backend**: FastAPI, requests, pydantic, pytest, httpx, pytest-asyncio
- **Database**: SQLite for sample data
- **WebSocket**: FastAPI WebSocket support
- **Markdown**: markdown library for LLM response formatting

### CI/CD & Containerization

- **Container Registry**: GitHub Container Registry (ghcr.io)
- **Build Strategy**: Multi-stage Docker builds for optimization
- **CI/CD Pipeline**: GitHub Actions with automated testing and deployment
- **Container Features**:
  - Non-root user for security
  - Health checks built into container
  - Optimized layer caching
  - Production-ready configuration

## Project Structure

```text
/
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions CI/CD pipeline
├── .devcontainer/
│   └── devcontainer.json       # DevContainer configuration
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Pydantic configuration
│   ├── middleware/            # Authentication and other middleware
│   ├── routers/               # FastAPI routers (chat, data, websocket)
│   ├── models/                # Pydantic models
│   ├── services/              # Business logic services
│   └── utils/                 # Utility functions
├── tools/                     # Tool implementations
├── access_control/            # Permission system (replaceable)
├── static/                    # Frontend assets
├── logs/                      # Session logs (JSONL files)
├── tests/                     # Test suite
│   ├── test_health.py         # Basic health check tests
│   ├── test_config.py         # Configuration tests
│   └── conftest.py            # Pytest configuration
├── data/                      # SQLite database and sample data
├── docker/                    # Docker configuration files
├── Dockerfile                 # Production container image
├── docker-compose.yml         # Local development setup
├── .dockerignore              # Docker ignore file
├── pytest.ini                # Pytest configuration
├── pyproject.toml             # uv project configuration
├── uv.lock                    # uv lock file for reproducible builds
├── .python-version            # Python version specification (3.12) - optional
├── .env                       # Environment variables
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies (uv-generated)
├── requirements-dev.txt       # Development dependencies
├── system_prompt.md           # Default system prompt configuration
└── README.md                  # Project documentation
```

## Implementation Phases

**Development Guidelines**: Each phase should result in approximately 5 commits. Commit frequently to maintain clear development history and enable easy rollbacks if needed.

### Phase 1: Core Infrastructure & DevOps

1. **Python Environment Setup**:
   - Install uv (`pip install uv` or platform-specific installer)
   - Create `.python-version` file specifying Python 3.12 (optional - using Dockerfile)
   - Initialize uv project with `pyproject.toml` (optional - using requirements.txt)
   - Set up virtual environment with `uv venv`
2. FastAPI application setup with basic routers
3. Pydantic configuration system
4. **Docker Setup**:
   - Dockerfile for production container (using Python 3.12)
   - docker-compose.yml for local development
   - .dockerignore file
5. **Basic Testing**:
   - pytest configuration (pytest.ini)
   - Health check endpoint test
   - Configuration loading test
6. **CI/CD Pipeline**:
   - GitHub Actions workflow (with uv setup)
   - Automated testing on push/PR
   - Container build and push to GitHub Container Registry (ghcr.io)
   - Multi-stage builds for optimization
   - before committing make sure the tests pass. Add a time out when running the tests to prevent hanging:
   `uv run pytest -v tests --timeout=10`
   - After each phase of of the project, be sure that it is sufficiently tested. Add new tests as needed to cover new features and functionality.
7. **DevContainer Setup**:
   - .devcontainer/devcontainer.json (with uv and Python 3.12)
   - Development environment configuration

### Phase 2: Authentication & Session Management

1. Authentication middleware (X-EMAIL-USER header)
2. Session management system
3. Basic WebSocket connection
4. Rate limiting implementation
5. Access control foundation

### Phase 3: LLM Integration

1. OpenAI-compatible API client
2. Streaming response handling
3. Health check implementation
4. Error handling and fallbacks

### Phase 4: Tools & Data Sources

1. Tool configuration definitions
2. Calculator tool demo setup
3. System prompt modification for tools
4. Tool selection logging and streaming
5. Data source parameter handling

### Phase 5: Frontend & UX

1. Responsive chat interface
2. Dark theme implementation
3. Toast notification system
4. WebSocket status updates
5. Feedback collection

### Phase 6: Testing & Quality Assurance

1. Comprehensive test suite expansion
2. Integration tests
3. Performance testing
4. Security testing
5. Documentation updates

## Environment Variables

```env
# Application Configuration
APP_NAME=Galaxy Chat
SYSTEM_PROMPT_OVERRIDE=  # Optional override for system_prompt.md

# LLM Configuration (Legacy - for backward compatibility)
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL_NAME=gpt-3.5-turbo

# Multi-LLM Configuration
LLM_CONFIG_FILE=config/llms.yml  # Path to YAML configuration file

# Testing Configuration
DISABLE_WEBSOCKET=false
DISABLE_LLM_CALLS=false
TEST_MODE=false
TEST_EMAIL=test@test.com
```

## Future Enhancements

- Database-backed data sources
- Advanced access control system
- Persistent session storage
- Enhanced tool security (sandboxing)
- Analytics and monitoring
- Multi-model support
- Plugin system for tools


### Phase 7: Session Persistence & Conversation History

1. **Conversation History Management**:
   - Implement persistent conversation history within sessions
   - Each LLM call maintains full conversation context (not new conversations)
   - Store conversation state in session management system

2. **Session Logging**:
   - Create .jsonl files in logs folder for each session
   - Log all user messages, LLM responses, and tool interactions
   - Include timestamps and session metadata

3. **System Prompt Configuration**:
   - Create `system_prompt.md` file with default system prompt ("You are a helpful AI assistant...")
   - Use system prompt for every new session initialization
   - Add environment variable override capability for custom system prompts

### Phase 8: Tool Selection & Session Management

1. **Fixed Tool Selection**:
   - Lock tool selection after user chooses tools for a session
   - Prevent tool changes mid-session to simplify user experience
   - Display selected tools clearly in UI with locked state indicator

2. **Session State Management**:
   - Enhance session manager to track tool selections
   - Implement tool locking mechanism
   - Add session state validation

### Phase 9: UI/UX Improvements

1. **Application Branding**:
   - Add `APP_NAME` environment variable to .env file
   - Set default value to "Galaxy Chat"
   - Use APP_NAME throughout UI (title, headers, etc.)

2. **UI Component Enhancements**:
   - Remove record icon from interface
   - Expand chat input message area (wider and taller, most of screen width)
   - Make chat session history scrollable
   - Make chat input area scrollable for long inputs

3. **Markdown Rendering**:
   - Integrate markdown library for LLM output formatting
   - Render LLM responses as HTML from markdown
   - Support code blocks, lists, formatting, etc.

### Phase 10: Multi-LLM Support

1. **LLM Configuration System**:
   - Create YAML configuration file for multiple LLM providers
   - Define structure: name, base_url, api_key, model_name, provider
   - Support multiple LLM configurations simultaneously

2. **LLM Selection Interface**:
   - Add dropdown selector in UI for LLM choice
   - Display available LLMs from configuration
   - Allow users to switch LLMs per session

3. **Dynamic LLM Client**:
   - Modify LLM client to support multiple providers
   - Handle different API formats and authentication methods
   - Maintain backward compatibility with single LLM setup

### Phase 11: Export & Download Features

1. **Chat Session Export**:
   - Implement chat session download as .txt file
   - Format conversation history for readability
   - Include session metadata (timestamp, tools used, LLM selected)

2. **Export UI Components**:
   - Add download button to chat interface
   - Generate formatted text file from session data
   - Handle file download through browser

### Phase 12: Production Deployment & CI/CD

1. **GitHub Actions CI/CD Pipeline**:
   - Create comprehensive `.github/workflows/deploy.yml` workflow
   - Implement multi-stage pipeline: test → build → deploy
   - Add automated testing on pull requests and main branch pushes
   - Configure matrix testing across multiple Python versions (3.11, 3.12)

2. **Container Registry & Image Management**:
   - Set up automated Docker image builds on GitHub Actions
   - Push images to GitHub Container Registry (ghcr.io)
   - Implement semantic versioning for container tags
   - Create both `latest` and version-specific tags
   - Add image vulnerability scanning with Trivy or similar

3. **Production-Ready Container Configuration**:
   - Optimize Dockerfile for production (multi-stage builds, minimal base image)
   - Add health check endpoints for container orchestration
   - Configure proper logging for containerized environments
   - Set up non-root user execution for security
   - Add graceful shutdown handling

4. **Integration Testing Pipeline**:
   - Create end-to-end integration tests that run against deployed containers
   - Test full chat workflows including tool execution
   - Validate WebSocket connections and streaming responses
   - Test authentication middleware in containerized environment
   - Add database migration and initialization testing

5. **Deployment Automation**:
   - Set up automated deployment to staging environment on main branch
   - Implement blue-green deployment strategy for zero-downtime updates
   - Add rollback capabilities for failed deployments
   - Configure environment-specific configuration management
   - Set up monitoring and alerting for deployment health

6. **Infrastructure as Code**:
   - Create Docker Compose files for different environments (dev, staging, prod)
   - Add Kubernetes manifests for container orchestration
   - Configure ingress controllers and load balancers
   - Set up persistent volume claims for logs and data
   - Add horizontal pod autoscaling configuration

## Configuration Files

**system_prompt.md**:

```markdown
You are a helpful AI assistant. You provide accurate, helpful, and concise responses to user questions. You can use tools when available to enhance your responses with real-time data and functionality.
```

**config/llms.yml**:

```yaml
llms:
  - name: "Anthropic Claude"
    provider: "anthropic"
    base_url: "https://api.anthropic.com/v1"
    api_key: "${LLM_API_KEY}"
    model_name: "claude-3-5-sonnet-20241022"
    
  - name: "OpenAI GPT-3.5"
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
    model_name: "gpt-3.5-turbo"
    
  - name: "OpenAI GPT-4"
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
    model_name: "gpt-4"
    
  - name: "Local Ollama"
    provider: "ollama"
    base_url: "http://localhost:11434/v1"
    api_key: "not-required"
    model_name: "llama2"
```

### Phase 13: WebSocket Connection & Configuration Fixes

1. **Immediate WebSocket Connection**:
   - Open WebSocket connection as soon as user loads the page
   - Remove "connecting..." red status indicator
   - Ensure seamless connection establishment on page load

2. **UI Configuration Integration**:
   - Propagate app_name and llm_config_file from backend config to frontend
   - Display available models from config in UI dropdown
   - Ensure configuration values reach the user interface properly

3. **Docker Configuration Fix**:
   - Update Dockerfile CMD to use `uvicorn` instead of `gunicorn` ✅ (Already implemented)
   - Set single worker configuration or remove worker specification ✅ (Already implemented)
   - Ensure proper ASGI server for WebSocket support ✅ (Already implemented)

### Phase 14: Alpine.js Integration (Updated for New Architecture)

1. **Reactive Component Architecture** ✅:
   - Alpine.js CDN integration for lightweight reactivity
   - Main container with `x-data="chatApp()"` directive
   - Reactive state management without virtual DOM overhead
   - HTML-attribute syntax with minimal learning curve

2. **State Management Implementation**:
   ```javascript
   // Alpine.js data structure
   {
     messages: [],
     currentMessage: '',
     selectedModel: '',
     selectedTools: [],
     selectedDataSources: [],
     availableModels: [],
     isStreaming: false
   }
   ```

3. **Streaming Integration**:
   - Fetch API with ReadableStream for streaming responses
   - `reader.read()` loop for chunk processing
   - Automatic DOM updates via Alpine reactivity
   - Real-time message updates without manual DOM manipulation

4. **Benefits of New Approach**:
   - Simplified state management with Alpine.js
   - Automatic UI updates when data changes
   - Clean separation between configuration and execution
   - Future-ready for custom workflows and RAG systems
   - No build step required - works directly in browser

### Phase 15: Architectural Redesign - Simplified Streaming Approach

#### **New Architecture Principles**:
1. **Single Streaming Pattern**: All interactions result in streaming LLM responses
2. **Configuration-Based Tools**: Tools and data sources are configuration parameters, not executable functions
3. **System Prompt Modification**: Tool selection modifies LLM behavior via system prompt
4. **Future-Proofing**: Prepared for custom RAG and workflow systems

#### **Implementation Strategy**:

**Backend Changes**:
- Remove tool execution logic entirely
- Implement system prompt modification based on selections
- Single LLM call with streaming response for all interactions
- Tool selection logging without execution

**Frontend Changes (Alpine.js Integration)**:
- Reactive component architecture with `x-data="chatApp()"`
- State management: `{messages: [], selectedModel: '', selectedTools: [], selectedDataSources: []}`
- Streaming via Fetch API with ReadableStream reader
- Automatic DOM updates through Alpine reactivity

**API Flow**:
```
POST /api/chat {
  message,
  model: selectedModel,
  tools: selectedTools,
  dataSources: selectedDataSources
}
→ System prompt modification
→ Single streaming LLM response
→ Real-time UI updates
```

### Implementation Priority

These new phases should be implemented after the original Phase 6 completion. Each phase builds upon the previous infrastructure while adding significant user experience improvements and advanced functionality.

**Development Guidelines**: Continue the pattern of approximately 5 commits per phase, maintaining clear development history and enabling easy rollbacks if needed.

## Testing Guidelines

- **Test Timeouts**: Use `pytest-timeout` plugin to prevent hanging tests. Run tests with timeout flags:
  - Chat tests: `uv run pytest -v tests/test_chat.py --timeout=10`
  - Full test suite: `uv run pytest -v --timeout=10`
  - This prevents tests from hanging indefinitely due to network issues or infinite loops


```

uv run pytest -v --timeout=10

```


NOTe:
when commiting there is some persistent issue that doesn't allow using the cli. Instead write the commit message in the file `commit_message.txt` and then git commit command.

NOTE: Phase 14-15 represent the architectural redesign to a simplified streaming approach where tools are configuration parameters rather than executable functions. This aligns with future-proofing for custom RAG and workflow systems. 


Status:
- Phases 1-13: ✅ COMPLETED
- Phase 14: 🔄 UPDATED for new architecture (Alpine.js integration)
- Phase 15: 🆕 NEW architectural redesign phase

### Current Implementation Status:
- **Planning**: ✅ Complete (Plan updated, tests reviewed)
- **Backend**: ❌ Requires tool execution removal
- **Frontend**: 🔄 Needs Alpine.js integration update
- **Tests**: 🔄 New approach tests added, conflicts need resolution

### Critical Path:
1. Remove tool execution logic from backend
2. Implement system prompt modification
3. Update Alpine.js integration for new architecture
4. Align tests with streaming-only approach


