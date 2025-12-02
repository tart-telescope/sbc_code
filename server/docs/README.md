# TART API Documentation

Generates OpenAPI docs from the latest telescope-api container and serves via Swagger UI.

## Usage

```bash
# Generate schema and start Swagger UI
docker compose up --build

# View docs at http://localhost:8081
```

The schema is auto-generated from the live API and augmented with telescope locations from the map API.
