FROM python:3.13-bullseye

# Install curl for health checks and testing
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy test requirements
COPY test/requirements.txt .

# Install test dependencies
RUN uv pip install --system -r requirements.txt

# Copy test files
COPY test/ ./test/

# Default command to run tests
CMD ["python", "-m", "pytest", "test/", "-v", "--tb=short"]
