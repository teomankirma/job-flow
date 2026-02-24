# Phase 0 — Repo + Setup

## Tasks

- [x] Create `services/api` scaffold (FastAPI with `/health` endpoint)
- [x] Create `services/worker` scaffold (async heartbeat loop)
- [x] Create root Dockerfile for Next.js (bun-based)
- [x] Create `docker-compose.yml` (postgres, redis, api, worker, web)
- [x] Create `.dockerignore` and `.env.example`
- [x] Update `.gitignore` (Python ignores, `.env.example` exception)
- [x] Update `tsconfig.json` and `eslint.config.mjs` (exclude `services/`)
- [x] Update docs (`PRD.md`, `ROADMAP.md`, `README.md`)
- [x] Verify all services start and respond correctly

## Review

Phase 0 complete. All services verified:
- API: `GET /health` → `{"status":"ok"}`
- Worker: heartbeat loop running, graceful shutdown works
- PostgreSQL: `jobflow` user/db created, queries work
- Redis: responds to `PING` with `PONG`
- Web (Next.js): builds and serves on port 3000

Note: Used `postgres:17-alpine` instead of 16 to match the latest stable.
