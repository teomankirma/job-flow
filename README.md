# Job Flow

A distributed background job processing system with a web interface.

## Architecture

- **Frontend**: Next.js (App Router, TypeScript, Tailwind CSS)
- **API**: FastAPI (Python 3.12+)
- **Worker**: Async Python worker service
- **Database**: PostgreSQL
- **Queue**: Redis

## Quick Start

### Prerequisites

- Docker and Docker Compose v2
- Bun (for local Next.js development)

### Running with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Services will be available at:

| Service    | URL                         |
|------------|-----------------------------|
| Frontend   | http://localhost:3000        |
| API        | http://localhost:8000        |
| API Health | http://localhost:8000/health |
| PostgreSQL | localhost:5432               |
| Redis      | localhost:6379               |

### Local Development (Next.js only)

```bash
bun install
bun dev
```

## Project Structure

```
├── app/                  # Next.js App Router
├── services/
│   ├── api/              # FastAPI service
│   └── worker/           # Worker service
├── docker-compose.yml    # All services
├── Dockerfile            # Next.js container
└── docs/                 # Project documentation
```

## Documentation

- [Product Requirements](docs/PRD.md)
- [Roadmap](docs/ROADMAP.md)
