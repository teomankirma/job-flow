# Job Flow

A distributed background job processing system with retry logic, dead-letter queues, and a real-time dashboard. Built with FastAPI, Redis, PostgreSQL, and Next.js.

Demonstrates production-grade patterns: async job execution, exponential backoff retries, idempotency, rate limiting, graceful shutdown, and full-stack integration — all orchestrated via Docker Compose.

## Architecture

```
+-----------+       +-----------+       +-----------+
|  Next.js  | ----> |  FastAPI  | ----> |  Worker   |
|   :3000   | <---- |   :8000   |       | (asyncio) |
+-----------+       +-----+-----+       +-----+-----+
                          |                   |
                    +-----v-----+       +-----v-----+
                    |  Postgres | <---- |   Redis   |
                    |   :5432   |       |   :6379   |
                    +-----------+       +-----------+
                                        | job_queue |
                                        | retry_q   |
                                        | dlq       |
                                        +-----------+
```

**Data flow:** Client submits jobs via the API → API persists to PostgreSQL and pushes to Redis queue → Worker pops from queue, executes handler → On failure: exponential backoff retry via Redis ZSET or dead-letter after max attempts.

## Features

- **Async job processing** — Redis-backed queue with BLPOP, asyncio worker with configurable concurrency
- **Retry with exponential backoff** — Failed jobs retry at `2^attempts` seconds via Redis Sorted Set with atomic Lua script
- **Dead-letter queue** — Jobs exceeding max attempts land in DLQ for inspection and manual retry
- **Idempotency** — `Idempotency-Key` header prevents duplicate job creation (race-condition safe)
- **Rate limiting** — Sliding-window per-IP via Redis ZSET pipeline (POST only)
- **Real-time dashboard** — Next.js frontend with 2s polling, URL-persisted filters, responsive layout
- **Metrics endpoint** — Queue sizes, job counts by status, failure tracking
- **Structured logging** — JSON logs with job_id, duration, status context
- **Graceful shutdown** — Workers drain in-flight jobs on SIGTERM
- **Auto-migration** — Alembic runs on API startup

## Tech Stack

| Layer     | Technology                                                                  |
|-----------|-----------------------------------------------------------------------------|
| Frontend  | Next.js 16, TypeScript, Tailwind CSS v4, TanStack Query, Framer Motion     |
| API       | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async)                  |
| Worker    | Python 3.12, asyncio, Redis BLPOP, Semaphore concurrency                   |
| Database  | PostgreSQL 17, Alembic migrations                                          |
| Queue     | Redis 7 (List + Sorted Set + Lua scripts)                                  |
| Infra     | Docker Compose (5 services), health checks, volume persistence             |

## Quick Start

### Prerequisites

- Docker and Docker Compose v2

### Run

```bash
cp .env.example .env
docker compose up --build
```

| Service   | URL                              |
|-----------|----------------------------------|
| Dashboard | http://localhost:3000             |
| API       | http://localhost:8000             |
| API Docs  | http://localhost:8000/docs        |

### Local Development (Next.js only)

```bash
bun install
bun dev
```

## API Reference

### Create a job

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type": "email.send", "payload": {"to": "user@example.com", "subject": "Hello"}}'
```

### Create with idempotency key

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{"type": "report.generate", "payload": {"name": "Q4 Report"}, "max_attempts": 5}'
```

### Get job status

```bash
curl http://localhost:8000/jobs/{job_id}
```

### List jobs with filters

```bash
curl "http://localhost:8000/jobs?status=failed&limit=10&offset=0"
```

### Retry a failed job

```bash
curl -X POST http://localhost:8000/jobs/{job_id}/retry
```

### System metrics

```bash
curl http://localhost:8000/metrics
```

```json
{
  "total_jobs": 150,
  "active_jobs": 3,
  "completed_jobs": 120,
  "failed_jobs": 5,
  "dead_letter_jobs": 2,
  "queue_length": 10,
  "retry_queue_length": 3,
  "dlq_length": 2
}
```

## Job Types

| Type               | Behavior                                      |
|--------------------|-----------------------------------------------|
| `email.send`       | Always succeeds, ~1s processing time          |
| `report.generate`  | ~30% random failure rate, 2–5s processing     |
| `image.process`    | No handler — always fails, tests DLQ path     |

## Load Testing

```bash
pip install httpx

# Enqueue 1000 jobs
python scripts/load_test.py --count 1000

# Enqueue and watch processing metrics live
python scripts/load_test.py --count 1000 --poll
```

For bulk testing, increase the rate limit:

```bash
RATE_LIMIT_MAX=10000 docker compose up
```

## Design Decisions

### Redis ZSET for retry queue

Retry delays are stored as scores (`time.time() + 2^attempts`) in a Redis Sorted Set. A Lua script atomically moves due jobs to the main queue (`ZRANGEBYSCORE` + `ZREM` + `RPUSH`), preventing double-queuing across multiple worker instances.

### DB commit before Redis push

The API commits the job to PostgreSQL before pushing to Redis. If the Redis push fails, the job exists in the DB with "pending" status but isn't queued — a safer failure mode than a queued job with no DB record.

### Two-commit pattern in worker

The worker commits "processing" status before executing the handler, then commits the final status. This makes in-progress work visible to the dashboard and prevents long-running jobs from appearing stuck as "pending."

### Separate DB sessions for error handling

The worker opens a fresh DB session in the error path. If the original session is in a broken state, the error handler can still update job status and schedule a retry.

### asyncio Semaphore for concurrency

All job handlers are I/O-bound (async sleep simulations). A semaphore with limit 5 caps concurrency without thread pool overhead. The GIL isn't a concern since there's no CPU-bound work.

### Sliding-window rate limiting

A Redis ZSET pipeline (`ZREMRANGEBYSCORE` + `ZADD` + `ZCARD` + `EXPIRE`) provides accurate sliding-window rate limiting with minimal Redis round-trips. Only POST requests are limited to avoid blocking dashboard reads.

## Project Structure

```
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout (header, providers)
│   ├── page.tsx                  # Landing page (project overview)
│   ├── dashboard/page.tsx        # Job dashboard
│   ├── create/page.tsx           # Create job form
│   └── jobs/[id]/page.tsx        # Job detail view
├── components/
│   ├── about/                    # Landing page content
│   ├── jobs/                     # Dashboard, detail, form components
│   ├── layout/                   # Header, navigation
│   └── ui/                       # shadcn/ui primitives
├── lib/
│   ├── api/                      # API client + React Query hooks
│   ├── motion/                   # Framer Motion variants
│   └── types/                    # TypeScript types
├── services/
│   ├── api/                      # FastAPI service
│   │   ├── app/main.py           # App entry, middleware, lifespan
│   │   ├── app/routes/jobs.py    # Job CRUD + retry endpoints
│   │   ├── app/routes/metrics.py # Metrics endpoint
│   │   ├── alembic/              # DB migrations
│   │   └── tests/                # 18 API tests
│   └── worker/                   # Worker service
│       ├── app/main.py           # Worker loop, retry scheduler
│       ├── app/handlers/         # Job type handlers
│       └── tests/                # 8 worker tests
├── scripts/
│   └── load_test.py              # Load testing script
├── docker-compose.yml            # 5-service orchestration
└── Dockerfile                    # Next.js container
```

## Running Tests

```bash
# API tests (18 tests)
cd services/api && pytest -v

# Worker tests (8 tests)
cd services/worker && pytest -v
```

## Future Improvements

- **Horizontal scaling** — run multiple worker replicas (the atomic Lua retry script already supports this)
- **Job priority** — multiple Redis queues with weighted polling
- **Webhook callbacks** — notify external services on job completion/failure
- **Job scheduling** — cron-like scheduled job submission
- **Job result storage** — persist handler return values for retrieval
- **Observability** — OpenTelemetry traces, Prometheus metrics export
- **Authentication** — API key or JWT-based access control

## License

MIT
