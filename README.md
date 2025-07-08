# Galaxy Chat

A modern AI chat application with streaming responses, multiple model support, and a ChatGPT-style interface.

## Overview

Galaxy Chat is a full-stack web application that provides an intuitive chat interface for interacting with various Large Language Models (LLMs). The application features real-time streaming responses, customizable tools, data source integration, and a responsive modern UI.

## Features

### Core Functionality
- **Multi-Model Support**: Choose from various LLM providers and models
- **Real-time Streaming**: Live streaming of AI responses with typing indicators
- **Session Management**: Persistent chat sessions with message history
- **WebSocket Integration**: Real-time bidirectional communication

### User Interface
- **Modern ChatGPT-style UI**: Full-screen responsive design with sidebar navigation
- **Chat Bubbles**: Distinct styling for user, assistant, and system messages
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new lines
- **Dark/Light Theme Support**: Automatic theme detection and switching

### Tools & Data Sources
- **Selectable Tools**: Calculator, code execution, user lookup, web search, file operations
- **Data Sources**: Employee data, product catalog, order history, analytics, documents
- **Checkbox Interface**: Modern selection UI instead of traditional dropdowns

## Architecture

### Backend (FastAPI)
```
app/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── models/                 # Database models
├── routers/               # API route handlers
│   ├── chat.py           # Chat session endpoints
│   ├── llm_configs.py    # Model configuration API
│   ├── tools.py          # Tools and data sources API
│   └── websocket.py      # WebSocket connections
├── services/             # Business logic
│   ├── llm_client.py     # LLM provider integration
│   ├── session_manager.py # Chat session management
│   └── tool_manager.py   # Tool execution logic
└── utils/                # Utility functions
    └── session_logger.py # Session logging
```

### Frontend (Alpine.js + Vite)
```
frontend/
├── index.html            # Main HTML template
├── src/
│   ├── main.js          # Alpine.js application logic
│   └── styles/
│       └── main.css     # Tailwind CSS styles
├── package.json         # Node.js dependencies
└── vite.config.js       # Vite build configuration
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- uv (Python package manager) - [Install from here](https://docs.astral.sh/uv/getting-started/installation/)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd galaxy-chat
   ```

2. **Set up Python environment**
   ```bash
   uv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uv pip install -r requirements.txt
   uv pip install -r requirements-dev.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # ANTHROPIC_API_KEY=your_anthropic_key_here
   # OPENAI_API_KEY=your_openai_key_here
   ```

4. **Install and build frontend**
   ```bash
   cd frontend
   npm install
   npm run build  # Important: Build is required for UI changes to appear
   cd ..
   ```

### Running the Application

#### Development Mode (Recommended)
```bash
# Terminal 1: Start backend server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend dev server (for live reloading)
cd frontend
npm run dev
```

**Important Notes:**
- The backend serves the built frontend from `/dist` folder at `http://localhost:8000`
- The frontend dev server runs at `http://localhost:3000` (or `http://localhost:3001` if 3000 is in use)
- For UI changes to appear, you must run `npm run build` in the frontend directory
- The frontend uses Vite for building and live reloading
- **For Docker/WSL users**: The dev server binds to `0.0.0.0` for port forwarding compatibility

#### Quick Development Workflow
When making frontend changes:
```bash
# Make your changes to frontend files
cd frontend
npm run build  # Build the changes
cd ..
# Refresh browser - changes should now be visible
```

#### Production Mode
```bash
# Build frontend
cd frontend && npm run build && cd ..

# Start production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Using Docker
```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.prod.yml up
```

## API Endpoints

### Core Endpoints
- `GET /` - Serve frontend application
- `GET /health` - Health check endpoint
- `GET /llms` - Get available LLM configurations

### Chat API
- `POST /chat` - Create new chat session
- `POST /chat/{session_id}/message` - Send message (streaming response)
- `GET /ws` - WebSocket connection for real-time updates

### Configuration API
- `GET /api/tools` - Get available tools
- `GET /api/data-sources` - Get available data sources

## Configuration

### LLM Configuration
Configure available models in `config/llms.yml`:

```yaml
llms:
  - name: "Claude 3.5 Sonnet"
    provider: "anthropic"
    model: "claude-3-5-sonnet-20241022"
    api_key_env: "ANTHROPIC_API_KEY"
  
  - name: "GPT-4"
    provider: "openai"
    model: "gpt-4"
    api_key_env: "OPENAI_API_KEY"
```

### Environment Variables
```bash
# API Keys
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Database
DATABASE_URL=sqlite:///./data/app.db

# Development
TEST_MODE=false
DISABLE_LLM_CALLS=false
```

## Testing

### Run All Tests
```bash
./run_all_tests.sh
```

### Test Categories
```bash
# Backend tests
python -m pytest tests/backend/ -v

# API tests
python -m pytest tests/api/ -v

# Frontend tests
python -m pytest tests/frontend/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Simple browser test
python test_browser_simple.py
```

### Fast Test Suite
```bash
./run_tests_fast.sh
```

## Development

### Frontend Development
The frontend uses Alpine.js for reactivity and Tailwind CSS for styling. Key files:

- `frontend/src/main.js` - Main application logic
- `frontend/index.html` - HTML template with Alpine.js directives
- `frontend/src/styles/main.css` - Custom styles and Tailwind imports

### Backend Development
The backend uses FastAPI with the following patterns:

- **Routers**: Organize endpoints by functionality
- **Services**: Business logic separated from route handlers
- **Models**: Database models and Pydantic schemas
- **Middleware**: Authentication, CORS, and request logging

### Adding New Tools
1. Create tool class in `tools/`
2. Register in `app/services/tool_manager.py`
3. Add to `AVAILABLE_TOOLS` in `app/routers/tools.py`

### Adding New Data Sources
1. Implement data source handler
2. Add to `AVAILABLE_DATA_SOURCES` in `app/routers/tools.py`
3. Update frontend to handle new data source

## Deployment

### Docker Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

### Manual Deployment
1. Build frontend: `cd frontend && npm run build`
2. Install Python dependencies: `uv pip install -r requirements.txt`
3. Set environment variables
4. Run: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Monitoring

### Logging
- Application logs: Structured JSON logging
- Session logs: Stored in `logs/` directory
- Test logs: Stored in `test_results/` directory

### Health Checks
- `GET /health` - Basic health check
- WebSocket connection monitoring
- Database connectivity checks

## Troubleshooting

### Common Issues

**Frontend changes not appearing**
- Run `npm run build` in the frontend directory
- The app serves from `/dist` folder, not source files
- Clear browser cache or try private browsing
- Check if `npm run dev` is running for live reload

**API Key errors (401 Unauthorized)**
- Verify API keys are set in `.env` file
- Check that `.env` file is in the root directory (`/app/.env`)
- Ensure `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` are correctly set
- Restart the backend server after changing `.env`

**Frontend not loading models**
- Check `/llms` endpoint is accessible
- Verify LLM configuration in `config/llms.yml`
- Check browser console for JavaScript errors

**Streaming responses not working**
- Verify WebSocket connection in browser dev tools
- Check for CORS issues
- Ensure proper content-type headers

**Tests failing**
- Run individual test suites to isolate issues
- Check test logs in `test_results/`
- Verify test database is properly initialized

### Debug Mode
Enable detailed logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run test suite: `./run_all_tests.sh`
5. Commit changes: `git commit -m "Add new feature"`
6. Push to branch: `git push origin feature/new-feature`
7. Create pull request

### Code Style
- Python: Follow PEP 8, use type hints
- JavaScript: Use modern ES6+ features
- CSS: Use Tailwind utility classes
- Tests: Descriptive test names and comprehensive coverage

## License

[Add your license information here]

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check existing documentation and troubleshooting guides
- Review test logs for detailed error information