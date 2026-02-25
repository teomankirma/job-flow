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

---

# Phase 2 — Worker MVP

## Tasks

- [x] Create `app/config.py` (env-based configuration: queue name, concurrency, poll timeout)
- [x] Create `app/log_config.py` (structured JSON logging with `JSONFormatter`)
- [x] Create `app/database.py` (async SQLAlchemy engine/session, same pattern as API)
- [x] Create `app/redis_client.py` (async Redis client, same pattern as API)
- [x] Create `app/models.py` (Job SQLAlchemy model, copy from API)
- [x] Create `app/handlers/email_send.py` (simulated email, always succeeds)
- [x] Create `app/handlers/report_generate.py` (simulated report, ~30% failure rate)
- [x] Create `app/handlers/__init__.py` (handler registry: job type → handler function)
- [x] Rewrite `app/main.py` (BLPOP loop, process_job, concurrency via semaphore, graceful shutdown)
- [x] Verify worker processes jobs end-to-end

## Review

Phase 2 complete. Worker MVP fully operational:
- `email.send` jobs: picked up within ~1s, processed in ~1s, status → `completed`
- `report.generate` jobs: 2-5s processing, ~30% random failure rate working
- Failed jobs: `status: "failed"`, `error_message` properly set, `attempts: 1`
- Concurrency: 5 simultaneous jobs (semaphore), remaining jobs queued until slots free
- Structured JSON logs: all lifecycle events logged with `job_id`, `job_type`, `status`, `duration_ms`
- Graceful shutdown: SIGTERM → stops accepting jobs → waits for in-flight → clean exit

Key decisions:
- Named logging module `log_config.py` to avoid shadowing stdlib `logging`
- Module-level imports (`from app import database as db`) to avoid stale references after `init_*()` calls
- Naive UTC datetimes via `_utcnow()` helper to match `TIMESTAMP WITHOUT TIME ZONE` columns
- Two-commit pattern: first commit sets `processing` + increments `attempts`, second sets final status
- Separate DB session in error path to avoid corrupted session issues

---

# Phase 3 — Reliability

## Tasks

- [x] Create Alembic migration `002_add_idempotency_key` (column + partial unique index)
- [x] Update both `models.py` files with `idempotency_key` column and index
- [x] Update API schemas: add `retrying`/`dead_letter` statuses, `idempotency_key` to response
- [x] Update API routes: `Idempotency-Key` header on POST, `status` filter on GET list
- [x] Update worker config: `RETRY_QUEUE_NAME`, `DLQ_NAME`, `RETRY_POLL_INTERVAL`
- [x] Update worker main: retry logic, `retry_scheduler()` coroutine, DLQ routing
- [x] Update worker log config: add `retry_delay_s` to extra fields
- [x] Run migration and verify all features end-to-end

## Review

Phase 3 complete. All reliability features verified:
- **Retry with exponential backoff**: Failed jobs get `retrying` status, ZADD to Redis sorted set with score = `time.time() + 2^attempts`. Retry scheduler polls ZSET every 1s, promotes due jobs via atomic Lua script (ZRANGEBYSCORE + ZREM + RPUSH). Observed: 2s delay after attempt 1, 4s after attempt 2.
- **Dead-letter queue**: Jobs exceeding `max_attempts` set to `dead_letter` status + RPUSH to `dead_letter_queue` Redis list. Verified with `max_attempts: 1` — failed job immediately dead-lettered.
- **Idempotency-Key**: `POST /jobs` with `Idempotency-Key` header returns 201 on first call, 200 with existing job on duplicate. Race condition handled via `IntegrityError` catch on partial unique index.
- **Status filter**: `GET /jobs?status=dead_letter` returns only dead-lettered jobs.
- **Graceful shutdown**: Worker loop + retry scheduler both respect `shutdown_event`, in-flight jobs complete before exit.

Key decisions:
- Redis ZSET for delayed retry queue (atomic Lua script prevents double-queuing across workers)
- New `retrying` and `dead_letter` statuses (clearer than overloading `failed`)
- Idempotency key as HTTP header (not body field) — cleaner separation of concerns
- `IntegrityError` handling for concurrent idempotency key race conditions
- `retry_scheduler()` runs as a peer coroutine to `worker_loop()` via `asyncio.gather()`

---

# Phase 4 — Frontend MVP

## Tasks

- [x] Add CORS middleware to FastAPI (`services/api/app/main.py`)
- [x] Add `POST /jobs/{id}/retry` endpoint to API routes
- [x] Install dependencies: `@tanstack/react-query`, `motion`, shadcn/ui (10 components)
- [x] Customize theme: dark industrial palette, sharp corners, status color variables, grid pattern
- [x] Override shadcn components: badge (status variants), button/card (no rounded corners)
- [x] Create TypeScript types (`lib/types/jobs.ts`) matching API contract
- [x] Create API client layer (`lib/api/client.ts`, `lib/api/jobs.ts`)
- [x] Create TanStack Query hooks with polling (`lib/api/hooks.ts`)
- [x] Create utility functions (`lib/utils/format.ts`) and motion presets (`lib/motion/variants.ts`)
- [x] Create QueryProvider and AppHeader layout components
- [x] Update root layout with providers, header, toaster, dark theme
- [x] Build shared components: StatusBadge, RetryButton, JobTypeLabel
- [x] Build Dashboard page: job table (desktop), card list (mobile), status filter tabs, pagination
- [x] Build Create Job page: form with type selector, JSON payload, max attempts
- [x] Build Job Detail page: metadata rows, payload display, error card, live polling
- [x] Verify build and lint pass

---

# Phase 5 — Production Polish

## Tasks

- [x] Create `app/routes/metrics.py` (GET /metrics — job counts by status from DB + queue lengths from Redis)
- [x] Create `app/middleware/rate_limit.py` (Redis sliding-window per IP, POST only, 60 req/min default)
- [x] Update `app/main.py` (register metrics router, rate limit middleware, Alembic auto-migration on startup)
- [x] Add test dependencies to `services/api/requirements.txt` (pytest, pytest-asyncio, httpx)
- [x] Add test dependencies to `services/worker/requirements.txt` (pytest, pytest-asyncio)
- [x] Create API test suite: `tests/conftest.py`, `test_jobs.py`, `test_metrics.py`, `test_rate_limit.py` (18 tests)
- [x] Create worker test suite: `tests/conftest.py`, `test_worker.py` (8 tests)
- [x] Verify all 26 tests pass

## Review

Phase 5 complete. All features verified:
- **Metrics endpoint**: `GET /metrics` returns JSON with `total_jobs`, `active_jobs`, `completed_jobs`, `failed_jobs`, `dead_letter_jobs`, `queue_length`, `retry_queue_length`, `dlq_length`. Single DB query with conditional aggregation + Redis LLEN/ZCARD.
- **Rate limiting**: Sliding-window per IP via Redis ZSET pipeline. Only POST requests rate-limited. Returns 429 with `Retry-After` header. Configurable via `RATE_LIMIT_MAX`/`RATE_LIMIT_WINDOW` env vars. Graceful fallback when Redis unavailable.
- **Alembic auto-migration**: `alembic upgrade head` runs in API lifespan before `init_db()`. Idempotent, safe on every startup. Wrapped in `try/except FileNotFoundError` for test environments.
- **API tests (18)**: Create job (success, validation, idempotency), get job (found, not found), list jobs (empty, filtered, with items), retry job (failed, dead_letter, conflict, not found), metrics (counts, queue lengths), rate limiting (GET bypass, POST threshold, Retry-After header).
- **Worker tests (8)**: process_job (success path, retry path, DLQ path, invalid ID, not found), handler registry (known, unknown), exponential backoff formula.

Key decisions:
- No external libraries for metrics or rate limiting — self-contained implementations
- `func.count().filter()` for conditional aggregation in metrics (single DB round-trip)
- FakeRedis/FakePipeline test doubles for Redis operations (no real Redis needed)
- FastAPI `dependency_overrides` for test isolation (mock DB sessions, fake Redis)
- `asyncio_mode = auto` in pytest.ini for cleaner async test configuration

---

# Phase 6 — Portfolio-Ready

## Tasks

- [x] Move dashboard from `/` to `/dashboard` route (`app/dashboard/page.tsx`)
- [x] Update navigation: Dashboard link → `/dashboard`, logo stays `/`
- [x] Update Back button in job detail to link to `/dashboard`
- [x] Create landing page component (`components/about/about-content.tsx`)
- [x] Update homepage (`app/page.tsx`) with project overview, tech stack, features, architecture
- [x] Create load test script (`scripts/load_test.py`) — async, handles rate limiting, metrics polling
- [x] Rewrite `README.md` — architecture diagram, API examples, design decisions, project structure
- [x] Update `docs/ROADMAP.md` to mark Phase 6 complete
- [x] Verify build passes and all pages render correctly

## Review

Phase 6 complete. All deliverables verified:
- **Route restructure**: Dashboard moved to `/dashboard`. Homepage now serves the project landing page. Logo links to `/`, nav links to `/dashboard` and `/create`. Back button in job detail links to `/dashboard`.
- **Landing page**: Hero with tagline + CTA buttons, tech stack (3-column: Backend/Frontend/Infra with badges), 8 feature cards (2-col grid with lucide icons), ASCII architecture diagram. Uses existing Card, Badge, motion variants. Dark industrial theme maintained.
- **Load test script**: `scripts/load_test.py` — async httpx with semaphore concurrency (50), handles 429 with backoff, progress output, `--poll` flag for live metrics watching. CLI args: `--url`, `--count`, `--poll`.
- **README**: Complete rewrite with ASCII architecture diagram, features list, tech stack table, quick start, API reference (6 curl examples), job types table, load testing instructions, 6 design decisions explained, updated project structure, future improvements.
- **Build**: `next build` compiles successfully, all 4 routes generated (/, /dashboard, /create, /jobs/[id]). Zero lint errors.
