FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Install datamodel-code-generator and ruff using uv
RUN uv pip install --system datamodel-code-generator ruff

# Copy generation script
COPY generate_models.py .

# Default command to generate models
CMD ["python", "generate_models.py"]
