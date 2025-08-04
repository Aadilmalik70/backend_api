# Multi-stage production Dockerfile for SERP Strategist API with WebSocket Support
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-google-apis.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-google-apis.txt && \
    pip install --no-cache-dir gunicorn eventlet

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set work directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/backups /app/credentials && \
    chown -R appuser:appgroup /app

# Copy application code
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup migrations/ ./migrations/
COPY --chown=appuser:appgroup *.py ./

# Copy production configuration
COPY --chown=appuser:appgroup production_config.py ./config/

# Create gunicorn configuration
COPY --chown=appuser:appgroup gunicorn.conf.py ./

# Set environment variables
ENV PYTHONPATH=/app/src:/app
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check script
COPY --chown=appuser:appgroup healthcheck.py ./
RUN chmod +x /app/healthcheck.py

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python /app/healthcheck.py

# Start application with Gunicorn and eventlet for WebSocket support
CMD ["gunicorn", "--config", "gunicorn.conf.py", "src.main:create_full_app()"]