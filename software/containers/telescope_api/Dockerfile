# Build stage
#
# Base images are pinned to an exact CPython patch release (issue #25).
# The floating python:3.13-*-trixie tags resolved on 2026-03-25 to a CPython
# 3.13.12 build whose libpython3.13.so and lib-dynload extensions execute
# instructions that are illegal on ARMv8.0 (Raspberry Pi 4 / Cortex-A72),
# crashing the API with SIGILL during garbage collection. The official
# python:3.13.12-trixie / python:3.13.12-slim-trixie builds were verified to
# work on ARMv8.0 hardware in the control experiments of issue #25.
# Keep the builder and runtime stages on the exact same version: the /opt/venv
# created here symlinks to the interpreter and is copied into the runtime stage,
# where it runs the runtime stage's CPython.
FROM python:3.13.12-trixie AS builder
RUN apt-get update && apt-get install -y libhdf5-dev && rm -rf /var/lib/apt/lists/*
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV=/opt/venv

# Copy lockfile, pyproject.toml, and hardware interface for dependency resolution
COPY tart_api/pyproject.toml tart_api/uv.lock ./
COPY ./hardware_interface /hardware_interface

# Install locked dependencies (frozen = no lockfile update, just install)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN find /opt/venv/lib -name 'tests' -type d -exec rm -rf {} + 2>/dev/null || true
RUN find /opt/venv/lib -name '*dist-info' -type d -exec rm -rf {} + 2>/dev/null || true

# Test builder stage - includes test extras
FROM builder AS test-builder
COPY ./permute.txt /permute/permute.txt
COPY tart_api/ /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --extra dev


# Runtime stage (pinned to the same exact release as the builder, see the
# issue #25 note at the top of this file)
FROM python:3.13.12-slim-trixie AS runtime

# Git commit hash passed in from CI
ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}

# Set environment variables
ENV PYTHONPATH=/app:/app/app
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV=/opt/venv

COPY ./permute.txt /permute/permute.txt
RUN mkdir -p /database

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y libhdf5-dev && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy the entire tart_api directory structure (includes generated_models now)
COPY tart_api/ ./

# Expose port
EXPOSE 5000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
