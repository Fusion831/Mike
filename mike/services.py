from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException

import mike.llm as llm
import mike.parser as parser
from mike.models import (
    CitationRole,
    CitationValidationResult,
    ClaimCitationLink,
    ConfidenceAssessment,
    ConfidenceFactor,
    ConfidenceLevel,
    ConfidenceEffect,
    CoverageAnswer,
    CoverageAnswerDraft,
    CoverageDecision,
    CoverageEvaluation,
    CoverageEvidence,
    CoverageQuestion,
    EvaluationAudit,
    EvaluationStatus,
    EvaluationTrace,
    EvidenceDiagnostics,
    EvidencePackage,
    GroundingStatus,
    RetrievalMeta,
    RetrievalRequest,
    RetrievalResponse,
    RetrievedPolicyChunk,
    RetrievalStrategy,
    SourceType,
)
from mike.storage import Storage


# ==========================================
# 1. Helper Functions (Stateless Business Logic)
# ==========================================

def rerank_chunks(query: str, chunks: list[RetrievedPolicyChunk]) -> list[RetrievedPolicyChunk]:
    query_terms = set(query.lower().split())

    def score(chunk: RetrievedPolicyChunk) -> tuple[float, float]:
        overlap = len(query_terms.intersection(set(chunk.chunk_text.lower().split())))
        return (float(overlap), chunk.retrieval_score)

    return sorted(chunks, key=score, reverse=True)


def assemble_evidence(
    question: CoverageQuestion,
    retrieved: list[RetrievedPolicyChunk],
    reranked: list[RetrievedPolicyChunk],
    vector_k: int,
) -> EvidencePackage:
    selected = reranked[: min(8, len(reranked))]
    avg_score = 0.0
    if selected:
        avg_score = sum(item.retrieval_score for item in selected) / len(selected)

    lower_question = question.question_text.lower()
    key_terms = [word for word in lower_question.split() if len(word) > 3]
    missing = [word for word in key_terms if not any(word in c.chunk_text.lower() for c in selected)]

    diagnostics = EvidenceDiagnostics(
        total_retrieved=len(retrieved),
        total_selected=len(selected),
        average_similarity=max(avg_score, 0.0),
        coverage_of_key_terms=[w for w in key_terms if w not in missing],
        missing_key_terms=missing,
    )

    gaps: list[str] = []
    if not selected:
        gaps.append("No relevant policy chunks retrieved")
    if missing:
        gaps.append("Some key terms were not covered in selected chunks")

    return EvidencePackage(
        policy_id=question.policy_id,
        question_id=question.question_id,
        retrieval_strategy=RetrievalStrategy(vector_k=vector_k, keyword_fallback_used=False),
        retrieved_chunks=retrieved,
        reranked_chunk_ids=[item.chunk_id for item in reranked],
        selected_chunks=selected,
        evidence_gaps=gaps,
        diagnostics=diagnostics,
    )


def validate_citations(answer_draft: CoverageAnswerDraft, evidence: EvidencePackage) -> CitationValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    selected_chunk_ids = {chunk.chunk_id for chunk in evidence.selected_chunks}
    citation_ids = {
        citation.citation_id
        for citation in (answer_draft.supporting_citations + answer_draft.contradicting_citations)
    }

    for citation in (answer_draft.supporting_citations + answer_draft.contradicting_citations):
        if citation.chunk_id not in selected_chunk_ids:
            errors.append(f"Citation chunk not in evidence package: {citation.chunk_id}")
        if not citation.document_id or not citation.chunk_id:
            errors.append("Citation missing required document_id or chunk_id")

    grounded_claim_count = 0
    for link in answer_draft.claim_to_citation_map:
        if not link.citation_ids:
            errors.append(f"Claim '{link.claim_id}' has no citation IDs")
        else:
            missing_links = [cid for cid in link.citation_ids if cid not in citation_ids]
            if missing_links:
                errors.append(
                    f"Claim '{link.claim_id}' references unknown citation IDs: {', '.join(missing_links)}"
                )
            else:
                grounded_claim_count += 1

    if (
        answer_draft.decision != CoverageDecision.CANNOT_DETERMINE_FROM_POLICY
        and not answer_draft.supporting_citations
        and not answer_draft.contradicting_citations
    ):
        errors.append("Decidable answer requires citations")

    if answer_draft.decision == CoverageDecision.CANNOT_DETERMINE_FROM_POLICY and not evidence.evidence_gaps:
        warnings.append("Insufficient-evidence decision returned without explicit evidence gaps")

    return CitationValidationResult(
        is_valid=not errors,
        errors=errors,
        warnings=warnings,
        grounded_claim_count=grounded_claim_count,
    )


def assess_confidence(
    answer: CoverageAnswer,
    evidence: EvidencePackage,
    validation: CitationValidationResult,
) -> ConfidenceAssessment:
    factors: list[ConfidenceFactor] = []
    insufficiency_flags: list[str] = []

    if not evidence.selected_chunks:
        factors.append(
            ConfidenceFactor(
                factor_name="evidence_availability",
                factor_effect=ConfidenceEffect.LOWERS,
                explanation="No selected chunks were available for reasoning.",
            )
        )
        insufficiency_flags.append("no_selected_chunks")

    if validation.errors:
        factors.append(
            ConfidenceFactor(
                factor_name="citation_integrity",
                factor_effect=ConfidenceEffect.LOWERS,
                explanation="One or more claims could not be traced to valid citations.",
            )
        )
        insufficiency_flags.append("citation_validation_failed")
    else:
        factors.append(
            ConfidenceFactor(
                factor_name="citation_integrity",
                factor_effect=ConfidenceEffect.RAISES,
                explanation="All claims and citations passed traceability checks.",
            )
        )

    if evidence.evidence_gaps:
        factors.append(
            ConfidenceFactor(
                factor_name="evidence_gaps",
                factor_effect=ConfidenceEffect.LOWERS,
                explanation="Evidence package contains unresolved gaps.",
            )
        )
        insufficiency_flags.extend([f"gap:{g}" for g in evidence.evidence_gaps])

    if answer.decision == CoverageDecision.CANNOT_DETERMINE_FROM_POLICY:
        level = ConfidenceLevel.LOW
        grounding = GroundingStatus.WEAKLY_GROUNDED
        rationale = "Policy evidence is insufficient to support a decisive coverage determination."
    elif validation.errors or len(evidence.evidence_gaps) > 0:
        level = ConfidenceLevel.LOW
        grounding = GroundingStatus.PARTIALLY_GROUNDED
        rationale = "Evidence exists but is incomplete or citation validation failed."
    elif len(answer.evidence.contradicting_citations) > 0:
        level = ConfidenceLevel.MEDIUM
        grounding = GroundingStatus.PARTIALLY_GROUNDED
        rationale = "Relevant clauses were found, but contradictory signals require conditional interpretation."
    else:
        level = ConfidenceLevel.HIGH
        grounding = GroundingStatus.FULLY_GROUNDED
        rationale = "Direct policy clauses support the determination with valid traceable citations."

    return ConfidenceAssessment(
        level=level,
        rationale=rationale,
        factors=factors,
        insufficiency_flags=sorted(set(insufficiency_flags)),
        policy_grounding_status=grounding,
    )


# ==========================================
# 2. Main Service Orchestrators
# ==========================================

class PolicyIngestionService:
    def __init__(self, storage_inst: Storage) -> None:
        self._storage = storage_inst

    @staticmethod
    def _estimate_token_count(text: str) -> int:
        return max(len(text.split()), 1)

    @staticmethod
    def _build_summary_text(summary: dict) -> str:
        return json.dumps(summary, ensure_ascii=True)

    async def ingest_pdf_bytes(
        self,
        *,
        policy_id: UUID,
        filename: str,
        file_bytes: bytes,
        policy_version: str = "v1",
    ) -> dict:
        suffix = os.path.splitext(filename)[1] or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        try:
            markdown_data = await parser.parse_pdf_to_markdown(temp_path)
            header_chunks = await parser.split_markdown_headers(markdown_data)

            raw_summary = await llm.generate_policy_summary(markdown_data)
            if hasattr(raw_summary, "model_dump"):
                summary_data = raw_summary.model_dump(mode="json")
            elif isinstance(raw_summary, dict):
                summary_data = raw_summary
            else:
                summary_data = {"summary_text": str(raw_summary)}

            retrieved_chunks: list[RetrievedPolicyChunk] = []
            document_id = f"policy_{policy_id}"

            for idx, chunk in enumerate(header_chunks):
                metadata = chunk.metadata or {}
                page_number = metadata.get("page")
                if isinstance(page_number, str) and page_number.isdigit():
                    page_number = int(page_number)
                if not isinstance(page_number, int):
                    page_number = None

                retrieved_chunks.append(
                    RetrievedPolicyChunk(
                        chunk_id=f"{policy_id}-md-{idx+1}",
                        document_id=document_id,
                        policy_id=policy_id,
                        heading=metadata.get("Section") or metadata.get("Chapter"),
                        subsection=metadata.get("Subsection"),
                        page_number=page_number,
                        chunk_text=chunk.page_content,
                        token_count=self._estimate_token_count(chunk.page_content),
                        source_type=SourceType.POLICY_CONTRACT,
                        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                        retrieval_score=0.0,
                        metadata={k: str(v) for k, v in metadata.items()},
                        version_tag=policy_version,
                    )
                )

            summary_text = self._build_summary_text(summary_data)
            retrieved_chunks.append(
                RetrievedPolicyChunk(
                    chunk_id=f"{policy_id}-summary-1",
                    document_id=document_id,
                    policy_id=policy_id,
                    heading="Policy Summary",
                    subsection="Structured Summary",
                    page_number=None,
                    chunk_text=summary_text,
                    token_count=self._estimate_token_count(summary_text),
                    source_type=SourceType.SUMMARY_OF_BENEFITS,
                    embedding_model="summary-json",
                    retrieval_score=0.0,
                    metadata={"generated_by": "policy.policyAgent.generate_policy"},
                    version_tag=policy_version,
                )
            )

            self._storage.register_policy_document(
                policy_id=policy_id,
                version=policy_version,
                filename=filename,
                summary=summary_data,
            )
            self._storage.upsert_chunks(policy_id=policy_id, chunks=retrieved_chunks)

            return {
                "policy_id": str(policy_id),
                "version": policy_version,
                "filename": filename,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "markdown_chunk_count": len(header_chunks),
                "total_chunk_count": len(retrieved_chunks),
                "summary_generated": True,
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def ingest_pdf_path(
        self,
        *,
        policy_id: UUID,
        file_path: str,
        policy_version: str = "v1",
    ) -> dict:
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as source_file:
            data = source_file.read()
        return await self.ingest_pdf_bytes(
            policy_id=policy_id,
            filename=filename,
            file_bytes=data,
            policy_version=policy_version,
        )

    def get_policy_summary(self, policy_id: UUID) -> dict | None:
        return self._storage.get_policy_summary(policy_id)


class CoverageEvaluationService:
    def __init__(self, storage_inst: Storage) -> None:
        self._storage = storage_inst

    def evaluate_coverage(self, question: CoverageQuestion) -> CoverageEvaluation:
        started = datetime.now(timezone.utc)

        self._storage.assert_user_policy_access(question.user_id, question.policy_id)
        policy_version = self._storage.get_effective_policy_version(question.policy_id)

        retrieval_request = RetrievalRequest(
            question_id=question.question_id,
            policy_id=question.policy_id,
            policy_version=policy_version.version,
            query_text=question.question_text,
            top_k=12,
        )

        # In-line retrieval search and response construction
        start_retrieve = time.perf_counter()
        retrieved_chunks = self._storage.search_chunks(
            policy_id=retrieval_request.policy_id,
            policy_version=retrieval_request.policy_version,
            query_text=retrieval_request.query_text,
            top_k=retrieval_request.top_k,
        )
        retrieval_elapsed_ms = int((time.perf_counter() - start_retrieve) * 1000)

        retrieval_response = RetrievalResponse(
            chunks=retrieved_chunks,
            retrieval_meta=RetrievalMeta(
                vector_store="qdrant",
                index_name="policy_chunks",
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                retrieval_latency_ms=max(retrieval_elapsed_ms, 0),
            ),
        )

        # Rerank and evidence assembly
        reranked = rerank_chunks(question.question_text, retrieval_response.chunks)
        evidence = assemble_evidence(
            question=question,
            retrieved=retrieval_response.chunks,
            reranked=reranked,
            vector_k=retrieval_request.top_k,
        )

        # Structured LLM reasoning
        answer_draft = llm.evaluate_coverage_reasoning(question, evidence)
        validation = validate_citations(answer_draft=answer_draft, evidence=evidence)

        # Build final answer
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

        confidence = assess_confidence(answer=answer, evidence=evidence, validation=validation)
        processing_status = EvaluationStatus.COMPLETED
        if not validation.is_valid:
            processing_status = EvaluationStatus.FAILED_VALIDATION
        elif answer_draft.decision.value == "cannot_determine_from_policy":
            processing_status = EvaluationStatus.INSUFFICIENT_EVIDENCE

        citations = answer_draft.supporting_citations + answer_draft.contradicting_citations

        # Save audit traces
        retrieval_trace_id = self._storage.save_retrieval_trace(
            {
                "question_id": str(question.question_id),
                "request": retrieval_request.model_dump(mode="json"),
                "response": retrieval_response.model_dump(mode="json"),
            }
        )
        llm_trace_id = self._storage.save_llm_trace(
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

        self._storage.save_evaluation(evaluation)

        # Trigger Pydantic validation of full evaluation trace
        _ = EvaluationTrace(
            evaluation_id=evaluation.evaluation_id,
            retrieval_request=retrieval_request,
            retrieval_response=retrieval_response,
            evidence_package=evidence,
            answer_draft=answer_draft,
            citation_validation=validation,
        )

        return evaluation

    def get_evaluation(self, evaluation_id: UUID) -> CoverageEvaluation | None:
        return self._storage.get_evaluation(evaluation_id)

    def get_trace(self, retrieval_trace_id: str, llm_trace_id: str) -> dict:
        return {
            "retrieval": self._storage.get_trace(retrieval_trace_id),
            "llm": self._storage.get_trace(llm_trace_id),
            "trace_bundle_id": str(uuid4()),
        }
