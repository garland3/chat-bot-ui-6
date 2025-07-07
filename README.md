# Chat Data MCP Tools UI

## Project Overview

A modern chatbot UI application built with a FastAPI backend and a responsive frontend. The application provides an intelligent chat interface that integrates with OpenAI-compatible APIs and supports tool calling and data source integration.

## Features

-   **Authentication**: Reverse proxy authentication via `X-EMAIL-USER` header.
-   **Session Management**: In-memory session storage with unique session IDs and rate limiting.
-   **LLM Integration**: OpenAI-compatible API client with streaming responses and health checks.
-   **Tools System**: Modular tool implementations for various tasks:
    -   `BasicMathTool`: Performs arithmetic operations.
    -   `CodeExecutionTool`: Simulates safe code snippet execution.
    -   `UserLookupTool`: Looks up user information in a corporate directory.
    -   `SQLQueryTool`: Executes read-only SQLite database queries.
-   **Data Sources**: API endpoint for fetching hardcoded data (extensible).
-   **Frontend**: Responsive dark-themed chat interface with real-time updates and toast notifications.

## Architecture

### Backend (FastAPI)

-   FastAPI with a modular router structure.
-   LLM integration using the `requests` library (not OpenAI SDK).
-   WebSocket connections for real-time chat.
-   Authentication via `X-EMAIL-USER` header.
-   In-memory session storage.

### Frontend

-   HTML, CSS (dark theme, responsive design).
-   JavaScript for real-time updates via WebSockets and UI interactions.
-   Static assets served directly by FastAPI.

## Development Setup

### Prerequisites

-   Python 3.11 (or compatible version)
-   `uv` (install with `pip install uv` or follow [uv installation guide](https://github.com/astral-sh/uv#installation))

### 1. Clone the repository

```bash
git clone https://github.com/your-username/chat-data-mcp-tools-ui.git
cd chat-data-mcp-tools-ui
```

### 2. Set up the Python Environment

Create a virtual environment and install dependencies using `uv`:

```bash
# uv venv
 uv venv .venv --python=3.11
# On Windows, activate with: .venv\Scripts\activate
# On macOS/Linux, activate with: source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
```

### 3. Database Initialization

Initialize the SQLite database with sample data:

```bash
python data/init_db.py
```

### 4. Environment Variables

Create a `.env` file in the project root based on `.env.example` and fill in your LLM API key:

```ini
# .env
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-openai-api-key
LLM_MODEL_NAME=gpt-3.5-turbo

TEST_MODE=false
TEST_EMAIL=test@test.com

DISABLE_WEBSOCKET=false
DISABLE_LLM_CALLS=false
```

### 5. Running Tests

To run all unit and integration tests:

```bash
uv run pytest -v --timeout=10
```

To run the optional real LLM test (requires a valid `LLM_API_KEY` in `.env`):

```bash
uv run pytest -m real_llm -v --timeout=10
```

#### Frontend/Browser Tests with Playwright

For comprehensive frontend testing including JavaScript error detection and Alpine.js integration:

```bash
# Install Playwright browsers and system dependencies
playwright install chromium
playwright install-deps  # Install system dependencies (Linux)

# Run frontend browser tests
uv run pytest tests/test_frontend_playwright.py -v --timeout=10
```

**Note**: Playwright tests require Chromium browser and system dependencies. If you encounter import errors, ensure you've run the installation commands above.

### 6. Running the Application

To start the FastAPI application:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be accessible at `http://localhost:8000`.

## Docker Usage

### Build the Docker image

```bash
docker build -t chat-data-mcp-tools-ui .
```

### Run with Docker Compose

```bash
docker-compose up --build
```

## CI/CD

This project includes a GitHub Actions workflow (`.github/workflows/ci-cd.yml`) for automated testing and Docker image building/pushing to GitHub Container Registry on `main` branch pushes and pull requests.

## Project Structure

```
/
├── .github/
├── .devcontainer/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── middleware/
│   ├── routers/
│   ├── services/
│   └── utils/
├── tools/
├── access_control/
├── frontend/                  # NPM-based frontend (Alpine.js + Vite)
├── data/
├── docker/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── pytest.ini
├── .env
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Future Enhancements

-   Database-backed data sources
-   Advanced access control system
-   Persistent session storage
-   Enhanced tool security (sandboxing)
-   Analytics and monitoring
-   Multi-model support
-   Plugin system for tools
