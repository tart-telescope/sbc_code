# Build container
docker build -f tart_codegen/Dockerfile.generate -t tart-pydanticv2-from-schema-generator .
mkdir -p tart_api/generated_models

# Generate models
docker run --rm \
  -v $(pwd)/schemas:/app/schemas:ro \
  -v $(pwd)/tart_api/generated_models:/app/tart_api/generated_models \
  tart-pydanticv2-from-schema-generator
