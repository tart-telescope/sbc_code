# Changelog

## 2026-09-28

### telescope_api Dockerfile / CI (issue #25)

- **Pin builder and runtime base images** to `python:3.13.12-trixie` / `python:3.13.12-slim-trixie`. The floating `python:3.13-*-trixie` tags resolved to a 2026-03-25 CPython build whose `libpython3.13.so` SIGILLs on ARMv8.0 (Raspberry Pi 4) during garbage collection; the pinned release is the one verified working on ARMv8.0 hardware in issue #25. Builder and runtime now share the exact same Python release to avoid venv/interpreter skew.
- **Add a pre-publish smoke test to CI**: the `linux/arm64` image is built and booted under QEMU (`python -X faulthandler` + forced-GC import of `app.main`, `pydantic.fields`, `fastapi`, `ensurepip`) before anything is pushed to ghcr.io.

## 2026-06-26

### docker-compose-telescope.yml

- **Align all services to `restart: unless-stopped`** — previously `tailscale`, `autoheal`, and `telescope-api` used `restart: always`, which would restart containers even after a deliberate `docker stop`. `unless-stopped` is more appropriate for an unattended telescope that occasionally needs intentional maintenance downtime.
- **Add healthcheck to `telescope-api`** — `ui` already depended on `telescope-api` with `condition: service_healthy`, but the API had no healthcheck defined. Added a wget-based healthcheck against `http://localhost:5000/`.
- **Add healthcheck to `ui`** — nginx sidecar now reports healthy once it serves the frontend at `/`.
- **Reformat indentation** — 4-space → 2-space for consistency with Docker Compose conventions.
