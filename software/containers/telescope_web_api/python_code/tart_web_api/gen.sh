# Build container
docker build -f Dockerfile.generate -t tart-schema-generator .
mkdir -p generated_models

# Generate models
docker run --rm \
  -v $(pwd)/schemas:/app/schemas:ro \
  -v $(pwd)/generated_models:/app/generated_models \
  tart-schema-generator
