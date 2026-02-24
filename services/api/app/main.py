import os

from fastapi import FastAPI

app = FastAPI(title="Job Flow API", version="0.1.0")


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
