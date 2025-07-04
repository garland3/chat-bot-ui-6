
# Stage 1: Build the application
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Create the production image
FROM python:3.12-slim

WORKDIR /app

# Create a non-root user
RUN adduser --system --group appuser
USER appuser

COPY --from=builder /app /app

EXPOSE 8000

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application with Gunicorn for production
# Gunicorn provides better process management and graceful shutdown than uvicorn directly
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--log-level", "info"]
