from __future__ import annotations

from uuid import UUID

from mike.application.ports.repositories import PolicyChunkRepositoryPort
from mike.domain.enums import SourceType
from mike.domain.models import RetrievedPolicyChunk


class LocalPolicyChunkRepository(PolicyChunkRepositoryPort):
    def __init__(self) -> None:
        self._chunks: dict[UUID, list[RetrievedPolicyChunk]] = {}

    def seed_chunks(self, policy_id: UUID, chunks: list[RetrievedPolicyChunk]) -> None:
        self._chunks[policy_id] = chunks

    def search_chunks(
        self,
        policy_id: UUID,
        policy_version: str,
        query_text: str,
        top_k: int,
    ) -> list[RetrievedPolicyChunk]:
        all_chunks = self._chunks.get(policy_id, [])
        query_words = set(query_text.lower().split())

        scored: list[RetrievedPolicyChunk] = []
        for chunk in all_chunks:
            text_words = set(chunk.chunk_text.lower().split())
            overlap = len(query_words.intersection(text_words))
            score = float(overlap) / max(len(query_words), 1)
            scored.append(
                chunk.model_copy(
                    update={
                        "retrieval_score": score,
                        "source_type": chunk.source_type or SourceType.POLICY_CONTRACT,
                        "version_tag": policy_version,
                    }
                )
            )

        scored.sort(key=lambda c: c.retrieval_score, reverse=True)
        return scored[:top_k]
