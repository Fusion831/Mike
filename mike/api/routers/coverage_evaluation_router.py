from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException

from mike.api.dependencies import container, seed_demo_policy
from mike.api.schemas import CoverageEvaluationResponse, CoverageQuestionInput
from mike.domain.models import CoverageQuestion


router = APIRouter(prefix="/v1", tags=["coverage-evaluation"])


@router.post(
    "/policies/{policy_id}/coverage/evaluations",
    response_model=CoverageEvaluationResponse,
)
def create_coverage_evaluation(
    policy_id: UUID,
    payload: CoverageQuestionInput,
    x_user_id: UUID | None = Header(default=None),
) -> CoverageEvaluationResponse:
    user_id = x_user_id or UUID("00000000-0000-0000-0000-000000000001")

    # Demo bootstrap for local development. Replace with real policy lifecycle logic.
    seed_demo_policy(policy_id)

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

    evaluation = container.coverage_evaluation_service.evaluate_coverage(question)
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


@router.get("/coverage/evaluations/{evaluation_id}")
def get_coverage_evaluation(evaluation_id: UUID):
    evaluation = container.coverage_evaluation_service.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation.model_dump(mode="json")


@router.get("/coverage/evaluations/{evaluation_id}/trace")
def get_coverage_evaluation_trace(evaluation_id: UUID):
    evaluation = container.coverage_evaluation_service.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return container.coverage_evaluation_service.get_trace(
        retrieval_trace_id=evaluation.audit.retrieval_trace_id,
        llm_trace_id=evaluation.audit.llm_trace_id,
    )
