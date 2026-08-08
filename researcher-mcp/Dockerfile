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

# Non-root user — UID/GID pinned so the identity is resolvable without /etc/passwd.
#
# pip is removed in the same layer, for the reason given in backend/Dockerfile:
# nothing at runtime uses it, and its vendored msgpack and setuptools are the
# HIGH findings Trivy reports on a python:3.14-slim runtime image.
RUN addgroup --system --gid 10001 appgroup \
    && adduser --system --uid 10001 --ingroup appgroup appuser \
    && rm -rf /usr/local/lib/python3.14/site-packages/pip \
        /usr/local/lib/python3.14/site-packages/pip-*.dist-info \
    && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.14

COPY --from=builder /workspace/.venv /app/.venv
COPY --from=builder /workspace/researcher-mcp/src /app/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER 10001:10001

EXPOSE 8002

CMD ["researcher-mcp"]
