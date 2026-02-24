## Build roadmap (step-by-step)

### Phase 0 — Repo + setup ✅

- Create monorepo structure:
  - `services/api` (FastAPI)
  - `services/worker` (Python worker)
  - Next.js stays at root (`app/` directory)
- Add `docker-compose.yml` with **Postgres + Redis**.
- Add `.env.example` and basic README skeleton.

### Phase 1 — Backend MVP ✅

- **DB model**: `jobs` table (uuid, type, payload JSONB, status, attempts, max_attempts, error, timestamps).
- **API endpoints**:
  - `POST /jobs` (create + enqueue)
  - `GET /jobs/{id}` (status)
  - `GET /jobs` (list recent, pagination)
- Add migrations (Alembic) or SQL bootstrap script.
- Add basic validation with Pydantic.

### Phase 2 — Worker MVP ✅

- Worker polls Redis queue (blocking pop).
- Job lifecycle:
  - set `processing`
  - run handler
  - set `completed` or `failed`
- Implement 2 job types:
  - `report.generate` (sleep + random fail)
  - `email.send` (simulated)
- Add structured logs.

### Phase 3 — Reliability ✅

- **Retry with exponential backoff** + `max_attempts`.
- **Dead-letter queue** (Redis list) when exceeded.
- **Idempotency-Key** support on `POST /jobs`.
- Graceful shutdown for workers.

### Phase 4 — Frontend MVP

- Next.js pages:
  - `/` dashboard (jobs list + status)
  - `/create` (submit job)
  - `/jobs/[id]` (details + live polling)
- Polling every 1–2s (simple `setInterval` or React Query).

### Phase 5 — “Production polish”

- Metrics endpoint: `GET /metrics` (queue size, totals, failures).
- Rate limiting (basic, e.g., per IP in Redis).
- Dockerize API/worker/web; one-command `docker compose up`.
- Add tests:
  - API: create job, status transitions
  - Worker: retries + DLQ path

### Phase 6 — Portfolio-ready

- Strong README:
  - architecture diagram
  - local run instructions
  - API examples (curl)
  - screenshots of UI
  - tradeoffs + future improvements
- Add small load script to enqueue 1k jobs and show scaling workers.

