# Build stage
FROM python:3.11 as builder

# Set working directory
WORKDIR /app

# Build tools already available in full Python image

# Install uv for fast Python package management
RUN pip install uv

# Copy pyproject.toml first for dependency caching
COPY tart_api/pyproject.toml ./

# Install Python dependencies
RUN uv pip install --system -r pyproject.toml

# Copy the generated models directly into the app
COPY generated_models/ ./models/

# Copy the entire app directory
COPY tart_api/app/ ./app/

# Copy database and other modules
COPY tart_api/database/ ./database/
COPY tart_api/middleware/ ./middleware/
COPY tart_api/services/ ./services/
COPY tart_api/tests/ ./tests/

# Copy the original Flask app for database compatibility
COPY tart_web_api/ ./tart_web_api/

# Copy and install local tart_hardware_interface
COPY tart_hardware_interface/ ./tart_hardware_interface/
RUN cd tart_hardware_interface && pip install -e .

# Set up PERMUTE_DIR and create mock permute file
ENV PERMUTE_DIR=/app/permute
RUN mkdir -p /app/permute && \
    echo "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23" > /app/permute/permute.txt

# Runtime stage
FROM python:3.11-slim as runtime

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code from builder
COPY --from=builder /app /app

# Set up PERMUTE_DIR for runtime
ENV PERMUTE_DIR=/app/permute

# Create necessary directories
RUN mkdir -p /telescope_data/raw /telescope_data/vis /config

# Set environment variables
ENV PYTHONPATH=/app
ENV CONFIG_DIR=/config
ENV DATA_ROOT=/telescope_data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
