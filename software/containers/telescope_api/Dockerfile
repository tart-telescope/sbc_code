# syntax=docker/dockerfile:1
# Build stage
FROM python:3.13 AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

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

# Runtime stage
FROM python:3.13-slim AS runtime


# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

ARG LOGIN_PW
ENV LOGIN_PW=$LOGIN_PW

ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY
ARG LOGLEVEL=INFO
ENV LOGLEVEL=$LOGLEVEL


# Set environment variables
ENV PYTHONPATH=/app:/app/app

# Path shared with the nginx to serve static files
ENV DATA_ROOT=/telescope_data

# Default path for the configuration files
ENV CONFIG_DIR=/config_data

ENV PERMUTE_DIR=/permute
COPY ./permute.txt /permute/permute.txt


# Set working directory
WORKDIR /app

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the entire tart_api directory structure (includes generated_models now)
COPY tart_api/ ./

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
