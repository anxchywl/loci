# Loci

Telegram Mini App where people pin meaningful life moments to real places on
an interactive world map — a living, collective archive of human memories.

## Stack

FastAPI · SQLAlchemy · Alembic · PostgreSQL + PostGIS · Redis · Celery ·
Next.js (App Router) · TypeScript · Tailwind · MapLibre GL · TanStack Query ·
Zustand · aiogram · Docker Compose

## Docs

- [docs/PRODUCT.md](docs/PRODUCT.md) — business rules, domain invariants, edge cases
- [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) — env vars, setup, deploy, backups
- [docs/DESIGN.md](docs/DESIGN.md) — design tokens, palette, icon set, do/don't
- [AGENTS.md](AGENTS.md) — agent rules (mandatory for AI-assisted changes)

## Quickstart (dev)

```sh
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

- API: http://localhost:8000 (health: `/health`)
- Web: http://localhost:3000
- MinIO console: http://localhost:9001

Backend tests:

```sh
cd backend && uv sync --extra dev && uv run pytest
```

Frontend checks:

```sh
cd frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

Production deployment and recovery procedures are in
[docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md#production-runbook).

## Layout

```
backend/    FastAPI app — api/v1 (transport) → modules (services) → db/repositories
frontend/   Next.js app — app routes → features → lib
docker/     dev + prod compose, Dockerfiles
deploy/     server setup, deploy, backup/restore scripts
docs/       product, infrastructure, design
```

## Status

MVP phases 0–6 are implemented: data layer, Telegram authentication, core API,
photo processing, map-first Mini App frontend, bot launcher, CI, hardened
production Compose, HTTPS, and verified daily backups. A deployment is complete
only after the production checklist in `docs/INFRASTRUCTURE.md` passes.
