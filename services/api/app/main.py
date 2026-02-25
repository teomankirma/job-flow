import os
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_db, init_db
from app.middleware.rate_limit import RateLimitMiddleware
from app.redis_client import close_redis, init_redis
from app.routes.jobs import router as jobs_router
from app.routes.metrics import router as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
    except FileNotFoundError:
        pass  # alembic not on PATH (e.g. test environment)

    init_db()
    init_redis()
    yield
    await close_db()
    await close_redis()


app = FastAPI(title="Job Flow API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)
app.include_router(jobs_router)
app.include_router(metrics_router)


@app.get("/")
async def root():
    return {"service": "job-flow-api", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
