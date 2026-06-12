from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from mike.router import router


app = FastAPI(title="Mike Backend", version="0.1.0")
app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "mike-backend",
        "message": "Coverage evaluation API is running",
    }


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
