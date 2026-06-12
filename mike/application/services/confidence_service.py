from __future__ import annotations

from mike.domain.enums import (
    ConfidenceEffect,
    ConfidenceLevel,
    CoverageDecision,
    GroundingStatus,
)
from mike.domain.models import (
    CitationValidationResult,
    ConfidenceAssessment,
    ConfidenceFactor,
    CoverageAnswer,
    EvidencePackage,
)


class ConfidenceService:
    def assess(
        self,
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
