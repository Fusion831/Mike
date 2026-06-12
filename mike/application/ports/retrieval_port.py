from __future__ import annotations

from abc import ABC, abstractmethod

from mike.domain.models import RetrievalRequest, RetrievalResponse, RetrievedPolicyChunk


class RetrievalPort(ABC):
    @abstractmethod
    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        raise NotImplementedError


class RerankPort(ABC):
    @abstractmethod
    def rerank(self, query: str, chunks: list[RetrievedPolicyChunk]) -> list[RetrievedPolicyChunk]:
        raise NotImplementedError
