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

---

# Phase 1 — Backend MVP

## Tasks

- [x] Add `alembic` to `services/api/requirements.txt`
- [x] Create `app/database.py` (async engine, session factory, `get_session` dependency)
- [x] Create `app/models.py` (SQLAlchemy `Job` model with UUID, JSONB, indexes)
- [x] Create `app/schemas.py` (Pydantic models: `JobCreateRequest`, `JobResponse`, `JobListResponse`, enums)
- [x] Create `app/redis_client.py` (Redis connection manager with `get_redis` dependency)
- [x] Create `app/routes/jobs.py` (3 endpoints: POST, GET by ID, GET list)
- [x] Update `app/main.py` (lifespan startup/shutdown, include jobs router)
- [x] Initialize Alembic with async `env.py` configuration
- [x] Create and run migration `001_create_jobs_table`
- [x] Verify all endpoints work correctly

## Review

Phase 1 complete. All endpoints verified:
- `POST /jobs` → 201, saves to DB + pushes to Redis `job_queue`
- `GET /jobs/{id}` → 200 with job data, 404 if not found
- `GET /jobs?limit=10` → paginated list with total/limit/offset
- Validation: 422 for invalid job type (must be `email.send`, `report.generate`, or `image.process`)
- Redis queue: confirmed job IDs enqueued via `LRANGE job_queue 0 -1`
- Health check: still returns `{"status":"ok"}`

Key decisions:
- FastAPI lifespan (not deprecated `on_event`) for startup/shutdown
- Global module state for engine/redis (simpler than `app.state`)
- DB commit before Redis push (safer failure mode)
- Alembic migrations run manually, not on startup
