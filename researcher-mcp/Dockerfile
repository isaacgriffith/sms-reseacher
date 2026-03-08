# syntax=docker/dockerfile:1
# Stage 1: build — install dependencies with UV
FROM python:3.14-slim AS builder

WORKDIR /workspace

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Copy workspace source
COPY pyproject.toml uv.lock ./
COPY researcher-mcp/ researcher-mcp/

# Sync only researcher-mcp package (no dev deps)
RUN uv sync --frozen --no-dev --package sms-researcher-mcp

# Stage 2: runtime
FROM python:3.14-slim AS runtime

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /workspace/.venv /app/.venv
COPY --from=builder /workspace/researcher-mcp/src /app/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8002

CMD ["researcher-mcp"]
