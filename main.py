from fastapi import FastAPI

from mike.api.routers.coverage_evaluation_router import router as coverage_router
from mike.api.routers.policy_ingestion_router import router as ingestion_router


app = FastAPI(title="Mike Backend", version="0.1.0")
app.include_router(coverage_router)
app.include_router(ingestion_router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "mike-backend",
        "message": "Coverage evaluation API is running",
    }
