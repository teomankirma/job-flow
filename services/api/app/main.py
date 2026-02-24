import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import close_db, init_db
from app.redis_client import close_redis, init_redis
from app.routes.jobs import router as jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_redis()
    yield
    await close_db()
    await close_redis()


app = FastAPI(title="Job Flow API", version="0.1.0", lifespan=lifespan)
app.include_router(jobs_router)


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
