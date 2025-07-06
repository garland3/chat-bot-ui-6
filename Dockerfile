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

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies in production image
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Create a non-root user with proper home directory for production
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser && \
    usermod -aG sudo appuser && \
    echo 'appuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Copy application code
COPY --chown=appuser:appuser . .

# For development, we'll override the user in docker-compose
# For production, we use the appuser
ARG DEV_MODE=false
RUN if [ "$DEV_MODE" = "true" ]; then \
        chown -R root:root /app; \
    fi

EXPOSE 8000

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

# Default to non-root user (can be overridden in docker-compose)
USER appuser

# Command to run the application with uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
