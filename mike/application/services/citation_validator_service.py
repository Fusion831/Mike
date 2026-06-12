from __future__ import annotations

from mike.domain.enums import CoverageDecision
from mike.domain.models import (
    CitationValidationResult,
    CoverageAnswerDraft,
    EvidencePackage,
)


class CitationValidatorService:
    def validate(self, answer_draft: CoverageAnswerDraft, evidence: EvidencePackage) -> CitationValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        selected_chunk_ids = {chunk.chunk_id for chunk in evidence.selected_chunks}
        citation_ids = {citation.citation_id for citation in (answer_draft.supporting_citations + answer_draft.contradicting_citations)}

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
