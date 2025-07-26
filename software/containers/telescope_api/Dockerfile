# Build stage
FROM python:3.13 AS builder
RUN apt-get update && apt-get install -y pkg-config libhdf5-dev && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/bin/" sh
WORKDIR /app
ENV UV_LINK_MODE=copy
# Copy pyproject.toml first for dependency caching
COPY tart_api/pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r pyproject.toml

# Install hardware interface using uv system-wide
COPY ./hardware_interface /hardware_interface
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system /hardware_interface

RUN find /usr/local/lib/python3.13/site-packages -name 'tests' -type d -exec rm -rf {} +
RUN find /usr/local/lib/python3.13/site-packages -name '*dist-info' -type d -exec rm -rf {} +

# Test builder stage - includes test extras
FROM builder AS test-builder
COPY ./permute.txt /permute/permute.txt
COPY tart_api/ /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system "/hardware_interface[test]"


# Runtime stage
FROM python:3.13-slim AS runtime

# Set environment variables
ENV PYTHONPATH=/app:/app/app

COPY ./permute.txt /permute/permute.txt
RUN mkdir -p /database

# Set working directory
WORKDIR /app

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the entire tart_api directory structure (includes generated_models now)
COPY tart_api/ ./

# Expose port
EXPOSE 5000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
