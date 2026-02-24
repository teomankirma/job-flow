# Project: Distributed Job Processing System (Full-Stack)

---

# 1. Overview

We are building a **distributed background job processing system with a web interface**, using Python for backend services and Next.js for frontend.

The system allows users to:

- Submit background jobs
- Track job progress in real time
- Automatically retry failed jobs
- Inspect failures
- Observe system metrics

The backend demonstrates:

- Distributed systems fundamentals
- Async programming
- Queue-based architecture
- Fault tolerance
- Horizontal scalability

The frontend demonstrates:

- Full-stack integration
- API communication
- Real-time state updates
- Clean UI architecture

---

# 2. High-Level Architecture

```
Frontend (Next.js)
        ↓
FastAPI API Server
        ↓
Redis (Queue)
        ↓
Worker Service (Async Python)
        ↓
PostgreSQL (Persistent Storage)
```

All services run via **Docker Compose**.

---

# 3. Tech Stack

## Backend

### Language

- Python 3.12+

### API Framework

- FastAPI (async-native)

### ORM

- SQLAlchemy 2.0 (async mode)

### Database

- PostgreSQL

### Queue

- Redis

### Worker Concurrency

- asyncio
- Multiple worker containers

### Validation

- Pydantic

### Logging

- Structured JSON logging

### Testing

- pytest
- pytest-asyncio

---

## Frontend

### Framework

- Next.js (App Router)

### Language

- TypeScript

### Styling

- Tailwind CSS

### Data Fetching

Option A (simpler):

- Native fetch + polling

Option B (cleaner):

- TanStack Query with `refetchInterval`

### State

- Local component state (no global store required)

---

# 4. System Components

---

## 4.1 API Service (FastAPI)

Runs at:

```
http://localhost:8000
```

Responsibilities:

- Accept job submissions
- Store job metadata
- Push jobs to Redis queue
- Serve job status
- Expose system metrics

---

## 4.2 Worker Service

Separate Python service.

Responsibilities:

- Poll Redis queue
- Fetch job from DB
- Execute job handler
- Retry on failure
- Move failed jobs to Dead Letter Queue

Workers must:

- Support concurrency
- Graceful shutdown
- Backoff strategy

---

## 4.3 Redis

Used for:

- Main job queue
- Retry queue
- Dead-letter queue
- Optional: lightweight metrics

---

## 4.4 PostgreSQL

Stores:

Job table:

- id (UUID)
- type
- payload (JSONB)
- status (pending | processing | completed | failed)
- attempts
- max_attempts
- error_message
- created_at
- updated_at

Indexes:

- status index
- created_at index

---

# 5. Frontend Application

---

## 5.1 Pages

### 1. Dashboard (/)

Shows:

- List of recent jobs
- Status badges (color coded)
- Retry button (if failed)
- Auto-refresh (poll every 2 seconds)

---

### 2. Create Job Page (/create)

Form fields:

- Job type (dropdown)
- Payload (JSON input textarea)
- Max attempts

On submit:

- POST to API
- Redirect to job detail page

---

### 3. Job Detail Page (/jobs/[id])

Displays:

- Job metadata
- Status
- Attempts
- Error message
- Live status updates via polling

---

# 6. Job Types (MVP)

Implement 2–3 job types:

1. Email simulation
2. Report generation simulation (sleep + random failure)
3. Image processing simulation (fake heavy task)

Important:
Introduce random failure probability to test retry logic.

---

# 7. Reliability Features

---

## Retry Logic

- Exponential backoff:

  ```
  delay = 2^attempt seconds
  ```

- Max attempts configurable per job

---

## Dead Letter Queue

- Jobs exceeding max attempts moved to DLQ
- Visible in dashboard

---

## Idempotency

Support:

```
Idempotency-Key header
```

Prevent duplicate job creation.

---

# 8. Concurrency Model

Worker must:

- Use asyncio tasks
- Handle multiple jobs in parallel
- Limit concurrency (configurable)

Example:

- 5 jobs concurrently per worker
- Scale workers via Docker

---

# 9. Observability

---

## Logging

Log events:

- Job received
- Job started
- Job failed
- Retry scheduled
- Job completed

---

## Metrics Endpoint

GET /metrics

Returns:

- total_jobs
- active_jobs
- failed_jobs
- queue_length

---

# 10. Deployment Strategy

Local development:

- Docker Compose

Services:

- api
- worker
- postgres
- redis
- web

Optional future:

- Deploy to Railway / Fly.io / Render

---

# 11. Repository Structure

```
root/
 ├── app/                  # Next.js App Router
 ├── services/
 │    ├── api/             # FastAPI service
 │    └── worker/          # Worker service
 ├── docker-compose.yml
 ├── Dockerfile            # Next.js Dockerfile
 └── README.md
```

---

# 12. What This Project Demonstrates

After completion, you can confidently discuss:

Backend:

- Async programming in Python
- Distributed systems patterns
- Queue architecture
- Fault tolerance
- Retry & DLQ
- Horizontal scaling
- Database consistency
- Idempotency design

Frontend:

- Full-stack integration
- Real-time UI updates
- API-driven architecture
- Type-safe client-server interaction

System Design:

- Scalability decisions
- Failure handling
- Tradeoffs between sync vs async processing
