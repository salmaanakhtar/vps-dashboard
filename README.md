# vps-dashboard

Unified overview dashboard for the salmaan.dev VPS, served at
`dashboard.salmaan.dev` (Tailscale-private).

Shows live host resources (load, memory, disk, swap, uptime), the running
container fleet with per-container CPU/memory/network stats, Docker storage
summary, and top processes. Links out to Grafana for detailed time-series
reporting at `grafana.salmaan.dev`.

## Architecture

- `app.py` — stdlib HTTP server that serves the static page and proxies the
  metrics API of the host agent (`AGENT_URL`, default
  `http://hermes-host-agent:9101`) with a short TTL cache.
- `index.html` — self-contained dark-themed dashboard UI (no build step),
  polls `/api/*` every 5 s.

## API

| Path       | Description                                  |
| ---------- | -------------------------------------------- |
| `/`        | Dashboard page                               |
| `/api/host`| Host load, memory, swap, disk, uptime, procs |
| `/api/containers` | Container list from the Docker API   |
| `/api/stats`      | Per-container live CPU/mem/net stats |
| `/api/system`     | Docker system df summary              |
| `/healthz` | Liveness probe                                |

## Deploy

Managed by the hermes-deployer (private visibility). No secrets required.
