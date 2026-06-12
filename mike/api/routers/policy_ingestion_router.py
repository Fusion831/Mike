from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile

from mike.api.dependencies import container
from mike.api.schemas import PolicyIngestionResponse, PolicyPathIngestionRequest


router = APIRouter(prefix="/v1", tags=["policy-ingestion"])
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DOCUMENTS_ROOT = WORKSPACE_ROOT / "documents"


@router.post("/policies/{policy_id}/ingest", response_model=PolicyIngestionResponse)
async def ingest_policy_pdf(policy_id: UUID, file: UploadFile = File(...)) -> PolicyIngestionResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    result = await container.policy_ingestion_service.ingest_pdf_bytes(
        policy_id=policy_id,
        filename=file.filename,
        file_bytes=payload,
        policy_version="v1",
    )
    return PolicyIngestionResponse.model_validate(result)


@router.post("/policies/{policy_id}/ingest-from-path", response_model=PolicyIngestionResponse)
async def ingest_policy_from_path(policy_id: UUID, payload: PolicyPathIngestionRequest) -> PolicyIngestionResponse:
    requested_path = Path(payload.file_path).expanduser().resolve()
    allowed_root = DOCUMENTS_ROOT.resolve()

    if allowed_root not in requested_path.parents and requested_path != allowed_root:
        raise HTTPException(status_code=400, detail="file_path must be inside the documents directory")
    if not requested_path.exists() or not requested_path.is_file():
        raise HTTPException(status_code=404, detail="File path not found")
    if requested_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    result = await container.policy_ingestion_service.ingest_pdf_path(
        policy_id=policy_id,
        file_path=str(requested_path),
        policy_version=payload.policy_version,
    )
    return PolicyIngestionResponse.model_validate(result)


@router.get("/policies/{policy_id}/summary")
def get_policy_summary(policy_id: UUID):
    summary = container.policy_ingestion_service.get_policy_summary(policy_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Policy summary not found")
    return {
        "policy_id": str(policy_id),
        "summary": summary,
    }
