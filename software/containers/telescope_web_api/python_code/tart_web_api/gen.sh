# Build container
docker build -f Dockerfile.generate -t tart-schema-generator .
mkdir -p tart_api/generated_models

# Generate models
docker run --rm \
  -v $(pwd)/schemas:/app/schemas:ro \
  -v $(pwd)/tart_api/generated_models:/app/tart_api/generated_models \
  tart-schema-generator
