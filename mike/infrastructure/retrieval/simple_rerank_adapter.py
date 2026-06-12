from __future__ import annotations

from mike.application.ports.retrieval_port import RerankPort
from mike.domain.models import RetrievedPolicyChunk


class SimpleRerankAdapter(RerankPort):
    def rerank(self, query: str, chunks: list[RetrievedPolicyChunk]) -> list[RetrievedPolicyChunk]:
        query_terms = set(query.lower().split())

        def score(chunk: RetrievedPolicyChunk) -> tuple[float, float]:
            overlap = len(query_terms.intersection(set(chunk.chunk_text.lower().split())))
            return (float(overlap), chunk.retrieval_score)

        return sorted(chunks, key=score, reverse=True)
