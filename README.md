# Loci

Loci is a Telegram Mini App for pinning meaningful life moments to real places
on a shared world map. It is map-first, privacy-first, and built as a
production-grade FastAPI + Next.js monorepo.

The MVP supports map markers, categories, stories, photos, comments, reactions,
bookmarks, reports, search, user profiles, and Telegram authentication.

## What Makes It Different

- Server-validated Telegram `initData` with stale/replay protection
- Optional anonymous stories with author IDs removed from public responses
- Server-side approximate-location fuzzing before coordinates are stored
- Public/private visibility checks on every read path
- Presigned object-storage uploads with async WebP optimization
- PostGIS-backed nearby, viewport, trending, and search APIs
- Telegram-native light/dark theming and MapLibre clustered markers

## Stack

| Area | Technology |
|---|---|
| Frontend | Next.js App Router, TypeScript, Tailwind, TanStack Query, Zustand |
| Mini App | Telegram Web App SDK, aiogram bot launcher |
| Map | MapLibre GL JS, OpenFreeMap tiles |
| Backend | FastAPI, Pydantic v2, SQLAlchemy, Alembic |
| Data | PostgreSQL, PostGIS, Redis |
| Media | S3-compatible storage, Cloudflare R2 in production, MinIO locally |
| Workers | Celery for photo processing |
| Ops | Docker Compose, Caddy, GitHub Actions |

## Repository Layout

```text
backend/    FastAPI API, domain services, repositories, models, migrations
frontend/   Next.js Mini App, MapLibre UI, Telegram/i18n/client state
docker/     Dev and production Compose files plus Dockerfiles
deploy/     Server setup, deploy, backup, restore, verification scripts
docs/       Product, infrastructure, and design source-of-truth docs
```

Backend flow: router -> service -> repository -> model -> database.

Frontend flow: route -> manager component -> query hook -> API client.

## Quickstart

Requirements:

- Docker + Docker Compose
- Node.js 22, for frontend checks outside Docker
- Python 3.12 + `uv`, for backend checks outside Docker

Run the full local stack:

```sh
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

Local services:

```text
Web:           http://localhost:3000
API:           http://localhost:8000
Health:        http://localhost:8000/health
MinIO console: http://localhost:9001
Postgres:      localhost:5433
Redis:         localhost:6380
```

Run backend checks:

```sh
cd backend
uv sync --extra dev
uv run ruff check .
uv run pytest
```

Run frontend checks:

```sh
cd frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

## Production

Production uses Docker Compose, Caddy HTTPS, PostgreSQL/PostGIS, Redis, Celery,
Cloudflare R2-compatible storage, and daily verified PostgreSQL backups.

The deployment runbook is in [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md).
Do not deploy with development secrets from `.env.example`.

## Documentation

- [docs/PRODUCT.md](docs/PRODUCT.md) — product rules, privacy invariants, API contract
- [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) — environment, deployment, backups, recovery
- [docs/DESIGN.md](docs/DESIGN.md) — visual system, category colors, UI constraints
- [AGENTS.md](AGENTS.md) — coding-agent rules for this repository

## Status

The MVP is implemented and deployable. The current production instance is
served at `https://loci.anxchywl.dev`.

Before opening to real users, rotate launch credentials, verify Telegram
BotFather settings, and run the smoke tests listed in the infrastructure
runbook.
