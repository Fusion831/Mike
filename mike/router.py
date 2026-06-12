from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, File, Header, HTTPException, UploadFile

from mike.models import (
    CoverageEvaluationResponse,
    CoverageQuestion,
    CoverageQuestionInput,
    PolicyIngestionResponse,
    PolicyPathIngestionRequest,
)
from mike.services import CoverageEvaluationService, PolicyIngestionService
from mike.storage import storage

router = APIRouter(prefix="/v1")

# Resolve paths relative to router's location (mike/router.py)
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_ROOT = WORKSPACE_ROOT / "documents"

# Global instanced services mapping to the global storage singleton
ingestion_service = PolicyIngestionService(storage)
evaluation_service = CoverageEvaluationService(storage)


# ==========================================
# 1. Policy Ingestion Routes
# ==========================================

@router.post(
    "/policies/{policy_id}/ingest",
    response_model=PolicyIngestionResponse,
    tags=["policy-ingestion"],
)
async def ingest_policy_pdf(
    policy_id: UUID,
    file: UploadFile = File(...),
) -> PolicyIngestionResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    result = await ingestion_service.ingest_pdf_bytes(
        policy_id=policy_id,
        filename=file.filename,
        file_bytes=payload,
        policy_version="v1",
    )
    return PolicyIngestionResponse.model_validate(result)


@router.post(
    "/policies/{policy_id}/ingest-from-path",
    response_model=PolicyIngestionResponse,
    tags=["policy-ingestion"],
)
async def ingest_policy_from_path(
    policy_id: UUID,
    payload: PolicyPathIngestionRequest,
) -> PolicyIngestionResponse:
    requested_path = Path(payload.file_path).expanduser().resolve()
    allowed_root = DOCUMENTS_ROOT.resolve()

    if allowed_root not in requested_path.parents and requested_path != allowed_root:
        raise HTTPException(status_code=400, detail="file_path must be inside the documents directory")
    if not requested_path.exists() or not requested_path.is_file():
        raise HTTPException(status_code=404, detail="File path not found")
    if requested_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    result = await ingestion_service.ingest_pdf_path(
        policy_id=policy_id,
        file_path=str(requested_path),
        policy_version=payload.policy_version,
    )
    return PolicyIngestionResponse.model_validate(result)


@router.get(
    "/policies/{policy_id}/summary",
    tags=["policy-ingestion"],
)
def get_policy_summary(policy_id: UUID):
    summary = ingestion_service.get_policy_summary(policy_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Policy summary not found")
    return {
        "policy_id": str(policy_id),
        "summary": summary,
    }


# ==========================================
# 2. Coverage Evaluation Routes
# ==========================================

@router.post(
    "/policies/{policy_id}/coverage/evaluations",
    response_model=CoverageEvaluationResponse,
    tags=["coverage-evaluation"],
)
def create_coverage_evaluation(
    policy_id: UUID,
    payload: CoverageQuestionInput,
    x_user_id: UUID | None = Header(default=None),
) -> CoverageEvaluationResponse:
    user_id = x_user_id or UUID("00000000-0000-0000-0000-000000000001")

    question = CoverageQuestion(
        user_id=user_id,
        policy_id=policy_id,
        session_id=payload.session_id,
        question_text=payload.question_text,
        scenario_context=payload.scenario_context,
        requested_decision_type=payload.requested_decision_type,
        submitted_at=datetime.now(timezone.utc),
        client_request_id=payload.client_request_id,
    )

    evaluation = evaluation_service.evaluate_coverage(question)
    return CoverageEvaluationResponse(
        evaluation_id=evaluation.evaluation_id,
        processing_status=evaluation.processing_status.value,
        answer=evaluation.answer.model_dump(mode="json"),
        confidence=evaluation.confidence.model_dump(mode="json"),
        citations=[item.model_dump(mode="json") for item in evaluation.citations],
        audit_ref={
            "retrieval_trace_id": evaluation.audit.retrieval_trace_id,
            "llm_trace_id": evaluation.audit.llm_trace_id,
            "prompt_version": evaluation.audit.prompt_version,
            "model_name": evaluation.audit.model_name,
        },
    )


@router.get(
    "/coverage/evaluations/{evaluation_id}",
    tags=["coverage-evaluation"],
)
def get_coverage_evaluation(evaluation_id: UUID):
    evaluation = evaluation_service.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation.model_dump(mode="json")


@router.get(
    "/coverage/evaluations/{evaluation_id}/trace",
    tags=["coverage-evaluation"],
)
def get_coverage_evaluation_trace(evaluation_id: UUID):
    evaluation = evaluation_service.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation_service.get_trace(
        retrieval_trace_id=evaluation.audit.retrieval_trace_id,
        llm_trace_id=evaluation.audit.llm_trace_id,
    )
