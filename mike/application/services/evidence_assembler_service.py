from __future__ import annotations

from mike.domain.models import (
    CoverageQuestion,
    EvidenceDiagnostics,
    EvidencePackage,
    RetrievedPolicyChunk,
    RetrievalStrategy,
)


class EvidenceAssemblerService:
    def build(
        self,
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
