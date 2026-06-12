from __future__ import annotations

import time

from mike.application.ports.repositories import PolicyChunkRepositoryPort
from mike.application.ports.retrieval_port import RetrievalPort
from mike.domain.models import RetrievalMeta, RetrievalRequest, RetrievalResponse


class QdrantRetrievalAdapter(RetrievalPort):
    def __init__(self, chunk_repository: PolicyChunkRepositoryPort) -> None:
        self._chunk_repository = chunk_repository

    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        start = time.perf_counter()
        chunks = self._chunk_repository.search_chunks(
            policy_id=request.policy_id,
            policy_version=request.policy_version,
            query_text=request.query_text,
            top_k=request.top_k,
        )
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        return RetrievalResponse(
            chunks=chunks,
            retrieval_meta=RetrievalMeta(
                vector_store="qdrant",
                index_name="policy_chunks",
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                retrieval_latency_ms=max(elapsed_ms, 0),
            ),
        )
