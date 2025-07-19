FROM python:3.13-slim

# Install curl for health checks and testing
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Copy test requirements
COPY test/requirements.txt .

# Install test dependencies
RUN --mount=type=cache,target=/root/.cache/uv uv pip install --system -r requirements.txt

COPY tart_api ./

# Copy test files
COPY test/ ./test/

# Default command to run tests
CMD ["python", "-m", "pytest", "test/", "-v", "--tb=short"]
