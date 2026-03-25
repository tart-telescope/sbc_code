# Build stage
FROM python:3.13-trixie AS builder
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


# Runtime stage
FROM python:3.13-slim-trixie AS runtime

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
