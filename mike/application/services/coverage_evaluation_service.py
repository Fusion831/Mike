from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from mike.application.ports.llm_reasoning_port import CoverageReasoningPort
from mike.application.ports.repositories import (
    AuditRepositoryPort,
    CoverageEvaluationRepositoryPort,
)
from mike.application.ports.retrieval_port import RerankPort, RetrievalPort
from mike.application.services.citation_validator_service import CitationValidatorService
from mike.application.services.confidence_service import ConfidenceService
from mike.application.services.evidence_assembler_service import EvidenceAssemblerService
from mike.application.services.policy_access_service import PolicyAccessService
from mike.domain.enums import EvaluationStatus
from mike.domain.models import (
    CoverageAnswer,
    CoverageEvaluation,
    CoverageEvidence,
    CoverageQuestion,
    EvaluationAudit,
    EvaluationTrace,
    RetrievalRequest,
)


class CoverageEvaluationService:
    def __init__(
        self,
        policy_access_service: PolicyAccessService,
        retrieval_port: RetrievalPort,
        rerank_port: RerankPort,
        evidence_assembler: EvidenceAssemblerService,
        reasoning_port: CoverageReasoningPort,
        citation_validator: CitationValidatorService,
        confidence_service: ConfidenceService,
        evaluation_repository: CoverageEvaluationRepositoryPort,
        audit_repository: AuditRepositoryPort,
    ) -> None:
        self._policy_access_service = policy_access_service
        self._retrieval_port = retrieval_port
        self._rerank_port = rerank_port
        self._evidence_assembler = evidence_assembler
        self._reasoning_port = reasoning_port
        self._citation_validator = citation_validator
        self._confidence_service = confidence_service
        self._evaluation_repository = evaluation_repository
        self._audit_repository = audit_repository

    def evaluate_coverage(self, question: CoverageQuestion) -> CoverageEvaluation:
        started = datetime.now(timezone.utc)

        self._policy_access_service.assert_user_policy_access(question.user_id, question.policy_id)
        policy_version = self._policy_access_service.resolve_effective_version(question.policy_id)

        retrieval_request = RetrievalRequest(
            question_id=question.question_id,
            policy_id=question.policy_id,
            policy_version=policy_version.version,
            query_text=question.question_text,
            top_k=12,
        )
        retrieval_response = self._retrieval_port.retrieve(retrieval_request)
        reranked = self._rerank_port.rerank(question.question_text, retrieval_response.chunks)
        evidence = self._evidence_assembler.build(
            question=question,
            retrieved=retrieval_response.chunks,
            reranked=reranked,
            vector_k=retrieval_request.top_k,
        )

        answer_draft = self._reasoning_port.evaluate(question, evidence)
        validation = self._citation_validator.validate(answer_draft=answer_draft, evidence=evidence)

        answer = CoverageAnswer(
            question_id=question.question_id,
            decision=answer_draft.decision,
            short_answer=answer_draft.short_answer,
            detailed_reasoning=answer_draft.detailed_reasoning,
            conditions=answer_draft.conditions,
            next_steps=answer_draft.next_steps,
            evidence=CoverageEvidence(
                question_id=question.question_id,
                summary=answer_draft.evidence_summary,
                supporting_citations=answer_draft.supporting_citations,
                contradicting_citations=answer_draft.contradicting_citations,
                unresolved_ambiguities=answer_draft.unresolved_ambiguities,
                missing_information_needed=answer_draft.missing_information_needed,
            ),
            risks=answer_draft.risks,
        )

        confidence = self._confidence_service.assess(answer=answer, evidence=evidence, validation=validation)
        processing_status = EvaluationStatus.COMPLETED
        if not validation.is_valid:
            processing_status = EvaluationStatus.FAILED_VALIDATION
        elif answer_draft.decision.value == "cannot_determine_from_policy":
            processing_status = EvaluationStatus.INSUFFICIENT_EVIDENCE

        citations = answer_draft.supporting_citations + answer_draft.contradicting_citations

        retrieval_trace_id = self._audit_repository.save_retrieval_trace(
            {
                "question_id": str(question.question_id),
                "request": retrieval_request.model_dump(mode="json"),
                "response": retrieval_response.model_dump(mode="json"),
            }
        )
        llm_trace_id = self._audit_repository.save_llm_trace(
            {
                "question_id": str(question.question_id),
                "answer_draft": answer_draft.model_dump(mode="json"),
                "citation_validation": validation.model_dump(mode="json"),
            }
        )

        latency_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        audit = EvaluationAudit(
            retrieval_trace_id=retrieval_trace_id,
            llm_trace_id=llm_trace_id,
            model_name="gemini-2.5-flash",
            prompt_version="coverage_eval_v1",
            latency_ms=latency_ms,
            policy_version_used=policy_version.version,
        )

        evaluation = CoverageEvaluation(
            question=question,
            evidence_package=evidence,
            answer=answer,
            confidence=confidence,
            citations=citations,
            processing_status=processing_status,
            audit=audit,
        )

        self._evaluation_repository.save(evaluation)

        _ = EvaluationTrace(
            evaluation_id=evaluation.evaluation_id,
            retrieval_request=retrieval_request,
            retrieval_response=retrieval_response,
            evidence_package=evidence,
            answer_draft=answer_draft,
            citation_validation=validation,
        )

        return evaluation

    def get_evaluation(self, evaluation_id):
        return self._evaluation_repository.get(evaluation_id)

    def get_trace(self, retrieval_trace_id: str, llm_trace_id: str) -> dict:
        return {
            "retrieval": self._audit_repository.get_trace(retrieval_trace_id),
            "llm": self._audit_repository.get_trace(llm_trace_id),
            "trace_bundle_id": str(uuid4()),
        }
