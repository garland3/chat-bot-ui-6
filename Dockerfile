# Stage 1: Build the application
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy requirements and install dependencies
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY . .

# Stage 2: Create the production image
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install uv in production image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies in production image
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Create a non-root user
RUN adduser --system --group appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8000

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application with uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
