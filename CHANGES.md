# Changelog

## 2026-06-26

### docker-compose-telescope.yml

- **Align all services to `restart: unless-stopped`** — previously `tailscale`, `autoheal`, and `telescope-api` used `restart: always`, which would restart containers even after a deliberate `docker stop`. `unless-stopped` is more appropriate for an unattended telescope that occasionally needs intentional maintenance downtime.
- **Add healthcheck to `telescope-api`** — `ui` already depended on `telescope-api` with `condition: service_healthy`, but the API had no healthcheck defined. Added a wget-based healthcheck against `http://localhost:5000/`.
- **Add healthcheck to `ui`** — nginx sidecar now reports healthy once it serves the frontend at `/`.
- **Reformat indentation** — 4-space → 2-space for consistency with Docker Compose conventions.
