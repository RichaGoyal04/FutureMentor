# ── FutureMentor Dockerfile ────────────────────────────────────────
# Multi-stage: build → slim runtime image
# Build:   docker build -t futurementor .
# Run:     docker run -p 5001:5001 --env-file .env futurementor

FROM python:3.11-slim AS base

# System deps for requests / SSL
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/       ./app/
COPY run.py     .
COPY .env.example .env.example

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Environment
ENV FLASK_ENV=production
ENV PORT=5001
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')"

# Start gunicorn
CMD gunicorn "app:create_app('production')" \
    --workers 2 \
    --threads 2 \
    --bind "0.0.0.0:${PORT}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
