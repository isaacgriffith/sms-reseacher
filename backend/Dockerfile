# syntax=docker/dockerfile:1
# Stage 1: build — install dependencies with UV
FROM python:3.14-slim AS builder

WORKDIR /workspace

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Copy workspace source
COPY pyproject.toml uv.lock ./
COPY backend/ backend/
COPY agents/ agents/
COPY db/ db/

# Sync only backend and its workspace deps (no dev deps)
RUN uv sync --frozen --no-dev --package sms-backend

# Stage 2: runtime — lean image with only what's needed
FROM python:3.14-slim AS runtime

WORKDIR /app

# Non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy virtual environment and source
COPY --from=builder /workspace/.venv /app/.venv
COPY --from=builder /workspace/backend/src /app/src
COPY --from=builder /workspace/agents/src /app/agents_src
COPY --from=builder /workspace/db/src /app/db_src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:/app/agents_src:/app/db_src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
