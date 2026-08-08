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

# Non-root user — UID/GID pinned so the identity is resolvable without /etc/passwd.
#
# pip is removed in the same layer. Nothing at runtime uses it: the application
# runs entirely from /app/.venv, which uv populated in the builder stage. Its
# vendored dependencies were the only two HIGH findings Trivy reported on this
# image — msgpack 1.1.2 (GHSA-6v7p-g79w-8964) and setuptools 70.3.0 via
# pkg_resources (CVE-2025-47273), both listed in pip/_vendor/vendor.txt.
#
# Deleting beats an ignore entry here: these are not unpatchable CVEs waiting on
# upstream, they are a dependency the runtime image never needed.
RUN addgroup --system --gid 10001 appgroup \
    && adduser --system --uid 10001 --ingroup appgroup appuser \
    && rm -rf /usr/local/lib/python3.14/site-packages/pip \
        /usr/local/lib/python3.14/site-packages/pip-*.dist-info \
    && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.14

# Copy virtual environment and source
COPY --from=builder /workspace/.venv /app/.venv
COPY --from=builder /workspace/backend/src /app/src
COPY --from=builder /workspace/agents/src /app/agents_src
COPY --from=builder /workspace/db/src /app/db_src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:/app/agents_src:/app/db_src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER 10001:10001

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
