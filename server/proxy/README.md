# TART Telescope Proxy

A double-nginx reverse proxy that sits between the public internet and the TART telescope tailnet, forwarding requests to individual telescope hosts via MagicDNS.

## Architecture

```
Internet
  │
  │  :8881
  ▼
┌─────────────────────────────────────────┐
│  nginx-external                         │
│  (Docker bridge network)                │
│  proxy_pass → tailscale:80              │
└──────────────┬──────────────────────────┘
               │  Docker bridge network
               │  resolves "tailscale" hostname
               ▼
┌─────────────────────────────────────────┐
│  nginx-sidecar                          │
│  (shared network namespace with         │
│   tailscale — inside the tailnet)       │
│                                         │
│  resolver → 100.100.100.100             │
│  proxy_pass → $tartname.$tailnet:80     │
└──────────────┬──────────────────────────┘
               │  Tailscale MagicDNS
               │  telescopes.elec.ac.nz
               ▼
┌─────────────────────────────────────────┐
│  Telescope hosts on the tailnet         │
│  (e.g. nz-nelson, za-rhodes, bd-iub)   │
└─────────────────────────────────────────┘
```

## Services

| Service | Image | Role |
|---|---|---|
| `tailscale` | `tailscale/tailscale:latest` | Connects to the headscale tailnet (`cloud.elec.ac.nz`). Provides the tailnet network namespace and MagicDNS. |
| `dns-init` | `tailscale/tailscale:latest` | One-shot service that toggles tailscale DNS after startup to ensure the resolver loads its host database. |
| `nginx-sidecar` | `nginx:alpine` | Shares tailscale's network namespace. Resolves `*.telescopes.elec.ac.nz` via MagicDNS (`100.100.100.100`) and proxies to telescope hosts. |
| `nginx-external` | `nginx:alpine` | Receives external traffic on port `8881`. Proxies all requests to `tailscale:80` (which reaches nginx-sidecar via the shared network namespace). |
| `autoheal` | `willfarrell/autoheal` | Monitors unhealthy containers and restarts them. |

## How It Works

1. **`tailscale`** starts and joins the headscale tailnet at `cloud.elec.ac.nz`. It creates a `tailscale0` network interface and configures MagicDNS with the `telescopes.elec.ac.nz` base domain. The tailscaled socket is shared via the `tailscale-tmp` Docker volume.

2. **`dns-init`** runs once after tailscale is healthy. It toggles `--accept-dns` off and on to force the MagicDNS resolver to load its host configuration. This works around a Docker platform limitation where tailscale's `directManager` can't modify `/etc/resolv.conf` inside the container.

3. **`nginx-sidecar`** uses `network_mode: "service:tailscale"` to share the tailscale container's network namespace. It listens on port 80 within that namespace and uses the MagicDNS resolver at `100.100.100.100:53` to resolve telescope hostnames.

4. **`nginx-external`** listens on the host's port `8881` and proxies all traffic to `tailscale:80`. Since `tailscale` is on the Docker bridge network and `nginx-sidecar` shares tailscale's network namespace, this reaches the sidecar nginx.

5. The sidecar matches requests to `/tart/<telescope>/...`, resolves `<telescope>.telescopes.elec.ac.nz` to a tailnet IP, and proxies the request upstream.

### Request Flow Example

```
http://localhost:8881/tart/nz-nelson/api/v1/info
  → nginx-external proxies to tailscale:80
  → nginx-sidecar resolves nz-nelson.telescopes.elec.ac.nz → 100.64.0.19
  → proxies to http://100.64.0.19/api/v1/info
  → telescope responds
```

## Creating an Auth Key

The tailscale container needs a pre-authentication key to join the headscale tailnet. This key is provided via a `secrets.env` file containing `TS_AUTH_KEY`.

### Generate a key on the headscale server

```bash
ssh tart@cloud.elec.ac.nz \
  'cd headscale; docker compose exec headscale \
    headscale -o yaml --user tart preauthkeys create --reusable --expiration 24h | grep key'
```

### Create secrets.env

```bash
echo "TS_AUTH_KEY=<key-from-above>" > secrets.env
```

This file is read by the tailscale container at startup and is ignored by git (listed in `.gitignore`).

## File Overview

| File | Purpose |
|---|---|
| `compose.yml` | Docker Compose configuration for all services |
| `nginx/nginx-external.conf` | External-facing nginx — proxies all traffic to `tailscale:80` |
| `nginx/nginx-sidecar.conf` | Sidecar nginx — routes `/tart/<host>/...` to telescopes on the tailnet |
| `secrets.env` | Contains `TS_AUTH_KEY` (git-ignored) |
| `Makefile` | Helper commands (`make build`, `make auth`) |
| `.gitignore` | Git ignore rules |

## Running

```bash
# Start all services
docker compose -f compose.yml up -d

# View status
docker compose -f compose.yml ps

# View logs
docker compose -f compose.yml logs -f

# Stop all services
docker compose -f compose.yml down
```

## DNS Resolution

- **External nginx** uses Docker's embedded DNS (`127.0.0.11`) to resolve `tailscale` hostname
- **Sidecar nginx** uses Tailscale MagicDNS (`100.100.100.100`) to resolve `*.telescopes.elec.ac.nz`
- The MagicDNS resolver requires `TS_USERSPACE=false` so tailscale creates a real network interface
- The `dns-init` service ensures the resolver's host database is loaded on startup
