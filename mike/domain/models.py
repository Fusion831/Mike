from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from mike.domain.enums import (
    CitationRole,
    ConfidenceEffect,
    ConfidenceLevel,
    CoverageDecision,
    CoverageRiskCategory,
    DecisionType,
    EvaluationStatus,
    GroundingStatus,
    RiskSeverity,
    SourceType,
)


class PolicyFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    operator: str
    value: str | int | float | bool | None


class RetrievalStrategy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector_k: int = Field(ge=1, le=100)
    keyword_fallback_used: bool = False
    filters_applied: list[PolicyFilter] = Field(default_factory=list)


class EvidenceDiagnostics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_retrieved: int = Field(ge=0)
    total_selected: int = Field(ge=0)
    average_similarity: float = Field(ge=0)
    coverage_of_key_terms: list[str] = Field(default_factory=list)
    missing_key_terms: list[str] = Field(default_factory=list)


class CoverageQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    policy_id: UUID
    session_id: UUID | None = None
    question_text: str = Field(min_length=3, max_length=4000)
    scenario_context: dict[str, str] | None = None
    locale: str | None = None
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    requested_decision_type: DecisionType = DecisionType.COVERAGE
    client_request_id: str | None = None


class RetrievedPolicyChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    document_id: str
    policy_id: UUID
    heading: str | None = None
    subsection: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    chunk_text: str = Field(min_length=1)
    token_count: int = Field(ge=0)
    source_type: SourceType = SourceType.POLICY_CONTRACT
    embedding_model: str
    retrieval_score: float
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    effective_date: date | None = None
    version_tag: str | None = None


class CoverageCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation_id: str
    document_id: str
    chunk_id: str
    heading: str | None = None
    subsection: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    quoted_text: str = Field(min_length=1)
    quote_start_char: int | None = Field(default=None, ge=0)
    quote_end_char: int | None = Field(default=None, ge=0)
    citation_role: CitationRole
    relevance_note: str | None = None

    @model_validator(mode="after")
    def validate_quote_range(self) -> "CoverageCitation":
        if self.quote_start_char is not None and self.quote_end_char is not None:
            if self.quote_end_char < self.quote_start_char:
                raise ValueError("quote_end_char must be >= quote_start_char")
        return self


class CoverageEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    summary: str
    supporting_citations: list[CoverageCitation] = Field(default_factory=list)
    contradicting_citations: list[CoverageCitation] = Field(default_factory=list)
    unresolved_ambiguities: list[str] = Field(default_factory=list)
    missing_information_needed: list[str] = Field(default_factory=list)


class CoverageRisk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_id: UUID = Field(default_factory=uuid4)
    category: CoverageRiskCategory
    severity: RiskSeverity
    statement: str
    triggering_conditions: list[str] = Field(default_factory=list)
    mitigation_steps: list[str] = Field(default_factory=list)
    citations: list[CoverageCitation] = Field(default_factory=list)


class CoverageAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer_id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    decision: CoverageDecision
    short_answer: str
    detailed_reasoning: str
    conditions: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    evidence: CoverageEvidence
    risks: list[CoverageRisk] = Field(default_factory=list)
    answer_generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConfidenceFactor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factor_name: str
    factor_effect: ConfidenceEffect
    explanation: str


class ConfidenceAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: ConfidenceLevel
    rationale: str
    factors: list[ConfidenceFactor] = Field(default_factory=list)
    insufficiency_flags: list[str] = Field(default_factory=list)
    policy_grounding_status: GroundingStatus


class EvidencePackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_package_id: UUID = Field(default_factory=uuid4)
    policy_id: UUID
    question_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    retrieval_strategy: RetrievalStrategy
    retrieved_chunks: list[RetrievedPolicyChunk] = Field(default_factory=list)
    reranked_chunk_ids: list[str] = Field(default_factory=list)
    selected_chunks: list[RetrievedPolicyChunk] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    diagnostics: EvidenceDiagnostics


class RetrievalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: UUID
    policy_id: UUID
    policy_version: str
    query_text: str
    top_k: int = Field(default=12, ge=1, le=100)
    filters: list[PolicyFilter] = Field(default_factory=list)


class RetrievalMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector_store: str
    index_name: str
    embedding_model: str
    retrieval_latency_ms: int = Field(ge=0)


class RetrievalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunks: list[RetrievedPolicyChunk] = Field(default_factory=list)
    retrieval_meta: RetrievalMeta


class ClaimCitationLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str
    citation_ids: list[str] = Field(default_factory=list)


class CoverageAnswerDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: CoverageDecision
    short_answer: str
    detailed_reasoning: str
    conditions: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    evidence_summary: str
    supporting_citations: list[CoverageCitation] = Field(default_factory=list)
    contradicting_citations: list[CoverageCitation] = Field(default_factory=list)
    unresolved_ambiguities: list[str] = Field(default_factory=list)
    missing_information_needed: list[str] = Field(default_factory=list)
    risks: list[CoverageRisk] = Field(default_factory=list)
    claim_to_citation_map: list[ClaimCitationLink] = Field(default_factory=list)


class CitationValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    grounded_claim_count: int = Field(default=0, ge=0)


class EvaluationAudit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    retrieval_trace_id: str
    llm_trace_id: str
    model_name: str
    prompt_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: int = Field(ge=0)
    policy_version_used: str


class CoverageEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluation_id: UUID = Field(default_factory=uuid4)
    question: CoverageQuestion
    evidence_package: EvidencePackage
    answer: CoverageAnswer
    confidence: ConfidenceAssessment
    citations: list[CoverageCitation] = Field(default_factory=list)
    processing_status: EvaluationStatus
    audit: EvaluationAudit

    @field_validator("citations")
    @classmethod
    def dedupe_citations(cls, value: list[CoverageCitation]) -> list[CoverageCitation]:
        seen: set[str] = set()
        deduped: list[CoverageCitation] = []
        for item in value:
            key = f"{item.document_id}:{item.chunk_id}:{item.citation_id}"
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped

    @model_validator(mode="after")
    def ensure_citations_when_decidable(self) -> "CoverageEvaluation":
        if (
            self.answer.decision != CoverageDecision.CANNOT_DETERMINE_FROM_POLICY
            and not self.citations
        ):
            raise ValueError("Decidable answers require at least one citation")
        return self


class PolicyVersionRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: UUID
    version: str


class EvaluationTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluation_id: UUID
    retrieval_request: RetrievalRequest
    retrieval_response: RetrievalResponse
    evidence_package: EvidencePackage
    answer_draft: CoverageAnswerDraft
    citation_validation: CitationValidationResult
