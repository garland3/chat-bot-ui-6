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

Built-in tools implementing abstract base class:

1. **BasicMathTool**: Arithmetic operations
2. **CodeExecutionTool**: Safe code snippet execution (placeholder)
3. **UserLookupTool**: Corporate directory lookup with sample users
4. **SQLQueryTool**: Read-only SQLite database queries (payments/customers data)

**Tool Features**:

- OpenAI-compatible tool calling format
- Timeout protection for all tool calls
- UI modification capabilities (buttons, plots, custom components)
- Modular design in `tools/` folder

### 4. Data Sources

- **Current**: Hardcoded placeholders
- **Future**: API/database integration
- **Access Control**: Permission-based access per user
- **API Endpoint**: `/data` endpoint for frontend queries

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

- **Backend**: FastAPI, requests, pydantic, pytest, httpx, pytest-asyncio
- **Database**: SQLite for sample data
- **WebSocket**: FastAPI WebSocket support

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
├── .env                       # Environment variables
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
├── requirements-dev.txt       # Development dependencies
└── README.md                  # Project documentation
```

## Implementation Phases

### Phase 1: Core Infrastructure & DevOps

1. FastAPI application setup with basic routers
2. Pydantic configuration system
3. **Docker Setup**:
   - Dockerfile for production container
   - docker-compose.yml for local development
   - .dockerignore file
4. **Basic Testing**:
   - pytest configuration (pytest.ini)
   - Health check endpoint test
   - Configuration loading test
5. **CI/CD Pipeline**:
   - GitHub Actions workflow
   - Automated testing on push/PR
   - Container build and push to GitHub Container Registry (ghcr.io)
   - Multi-stage builds for optimization
6. **DevContainer Setup**:
   - .devcontainer/devcontainer.json
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

1. Abstract tool base class
2. Basic tool implementations
3. SQLite database setup
4. Tool calling integration
5. Data source API endpoint

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
# LLM Configuration
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL_NAME=gpt-3.5-turbo

# Application Configuration
TEST_MODE=false
TEST_EMAIL=test@test.com

# Testing Configuration
DISABLE_WEBSOCKET=false
DISABLE_LLM_CALLS=false
```

## Future Enhancements

- Database-backed data sources
- Advanced access control system
- Persistent session storage
- Enhanced tool security (sandboxing)
- Analytics and monitoring
- Multi-model support
- Plugin system for tools
