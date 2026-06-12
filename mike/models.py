from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, List
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ==========================================
# 1. Enums
# ==========================================

class DecisionType(str, Enum):
    COVERAGE = "coverage"
    REFERRAL_REQUIREMENT = "referral_requirement"
    NETWORK_IMPACT = "network_impact"
    PRIOR_AUTH = "prior_auth"
    COST_SHARING = "cost_sharing"
    EXCLUSIONS = "exclusions"


class SourceType(str, Enum):
    POLICY_CONTRACT = "policy_contract"
    RIDER = "rider"
    ENDORSEMENT = "endorsement"
    AMENDMENT = "amendment"
    SUMMARY_OF_BENEFITS = "summary_of_benefits"


class CitationRole(str, Enum):
    SUPPORTS_COVERAGE = "supports_coverage"
    SUPPORTS_EXCLUSION = "supports_exclusion"
    SUPPORTS_CONDITION = "supports_condition"
    SUPPORTS_RISK = "supports_risk"
    SUPPORTS_UNCERTAINTY = "supports_uncertainty"


class CoverageRiskCategory(str, Enum):
    DENIAL_RISK = "denial_risk"
    PRIOR_AUTH_RISK = "prior_auth_risk"
    REFERRAL_RISK = "referral_risk"
    OUT_OF_NETWORK_RISK = "out_of_network_risk"
    DOCUMENTATION_RISK = "documentation_risk"
    TIMING_RISK = "timing_risk"
    POLICY_AMBIGUITY_RISK = "policy_ambiguity_risk"


class RiskSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CoverageDecision(str, Enum):
    LIKELY_COVERED = "likely_covered"
    LIKELY_NOT_COVERED = "likely_not_covered"
    CONDITIONALLY_COVERED = "conditionally_covered"
    CANNOT_DETERMINE_FROM_POLICY = "cannot_determine_from_policy"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceEffect(str, Enum):
    RAISES = "raises"
    LOWERS = "lowers"
    NEUTRAL = "neutral"


class GroundingStatus(str, Enum):
    FULLY_GROUNDED = "fully_grounded"
    PARTIALLY_GROUNDED = "partially_grounded"
    WEAKLY_GROUNDED = "weakly_grounded"


class EvaluationStatus(str, Enum):
    COMPLETED = "completed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    FAILED_VALIDATION = "failed_validation"


# ==========================================
# 2. Domain & Retrieval Models
# ==========================================

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


# ==========================================
# 3. LLM Structured Output Schemas
# ==========================================

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


# ==========================================
# 4. Policy Summary Models (from policy/models.py)
# ==========================================

class PlanOverview(BaseModel):
    insurer_name: str
    plan_name: str
    mikes_eli5_summary: str = Field(description="A 3-sentence 'Explain Like I'm 5' summary. Break down how this plan functions, who it is best for, and the biggest financial risk.")
    network_rules: str = Field(description="Explanation of network rules. E.g., 'This is an HMO. You must stay in-network.'")
    specialist_referral_required: bool = Field(description="True if the user MUST get a PCP referral to see a specialist.")
    referral_details: str = Field(description="Specific rules about getting referrals, or 'No referral needed' if false.")


class FinancialDetail(BaseModel):
    amount: str
    nuance: str = Field(description="Crucial context (e.g., 'Applies per family', 'Does not apply to prescription drugs').")


class Financials(BaseModel):
    in_network_deductible: FinancialDetail
    out_of_network_deductible: FinancialDetail
    out_of_pocket_max: FinancialDetail


class CareCost(BaseModel):
    cost: str
    conditions: str = Field(description="e.g., 'Only applies AFTER deductible is met', or 'Waived for first 3 visits'.")


class RoutineCare(BaseModel):
    preventive_care: CareCost
    primary_care: CareCost
    specialist: CareCost


class EmergencyScenarios(BaseModel):
    emergency_room: CareCost
    ambulance: CareCost
    urgent_care: CareCost


class DrugTier(BaseModel):
    tier_name: str = Field(description="e.g., 'Tier 1 Generic', 'Preferred Brand', 'Specialty'")
    cost: str = Field(description="Copay or coinsurance")
    notes: str = Field(description="Specific rules (e.g., 'Requires step therapy', 'Limited to 30-day supply')")


class PriorAuthorizationItem(BaseModel):
    service: str = Field(description="e.g., MRI, CT Scan, Physical Therapy, Bariatric Surgery")
    details: str = Field(description="What are the specific requirements to get this approved?")
    citation: str = Field(description="Exact markdown heading or section title where this information appears.If unavailable, return 'Citation unavailable in source text")


class CoverageExclusion(BaseModel):
    exclusion: str = Field(description="e.g., Cosmetic surgery, Adult dental, Experimental treatments")
    explanation: str = Field(description="Why is it excluded or are there any rare exceptions?")
    citation: str = Field(description="Exact markdown heading or section title where this information appears.If unavailable, return 'Citation unavailable in source text")


class ScenarioExample(BaseModel):
    scenario: str
    estimated_user_cost: str
    assumptions: list[str]
    explanation: str


class DenialRisk(BaseModel):
    risk: str = Field(description="e.g., 'Missing a Filing Deadline', 'Using an Out-of-Network Anesthesiologist'")
    explanation: str = Field(description="How this trap typically happens based on the policy text.")
    prevention_tip: str = Field(description="Actionable advice for the user to prevent this denial.")
    citation: str = Field(
        description="""
        Exact markdown heading or section title where this information appears.
        If unavailable, return 'Citation unavailable in source text
        """
    )


class PolicySummary(BaseModel):
    overview: PlanOverview
    financials: Financials
    routine_care: RoutineCare
    emergency_care: EmergencyScenarios
    drug_tiers: list[DrugTier] = Field(description="Extract all prescription drug tiers mentioned.")
    prior_authorization_requirements: list[PriorAuthorizationItem] = Field(description="Extract every explicit prior authorization requirement found.")
    excluded_services: list[CoverageExclusion] = Field(description="Extract every explicit exclusion found.")
    example_scenarios: list[ScenarioExample] = Field(description="Create 3 relatable medical scenarios (e.g., broken bone, hospital stay, chronic illness) and estimate the cost.")
    denial_risks: list[DenialRisk] = Field(description="Identify 3 to 5 strict rules that will result in an automatic claim denial if not followed.")


# ==========================================
# 5. API Schemas
# ==========================================

class CoverageQuestionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(min_length=3, max_length=4000)
    scenario_context: dict[str, str] | None = None
    requested_decision_type: DecisionType = DecisionType.COVERAGE
    session_id: UUID | None = None
    client_request_id: str | None = None


class CoverageEvaluationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluation_id: UUID
    processing_status: str
    answer: dict[str, Any]
    confidence: dict[str, Any]
    citations: list[dict[str, Any]]
    audit_ref: dict[str, Any]


class PolicyIngestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: str
    version: str
    filename: str
    ingested_at: str
    markdown_chunk_count: int
    total_chunk_count: int
    summary_generated: bool


class PolicyPathIngestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_path: str = Field(min_length=1)
    policy_version: str = Field(default="v1", min_length=1)
