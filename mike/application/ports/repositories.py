from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from mike.domain.models import (
    CoverageEvaluation,
    PolicyVersionRef,
    RetrievedPolicyChunk,
)


class PolicyRepositoryPort(ABC):
    @abstractmethod
    def assert_user_policy_access(self, user_id: UUID, policy_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_effective_policy_version(self, policy_id: UUID, on_date: date | None = None) -> PolicyVersionRef:
        raise NotImplementedError


class PolicyChunkRepositoryPort(ABC):
    @abstractmethod
    def search_chunks(
        self,
        policy_id: UUID,
        policy_version: str,
        query_text: str,
        top_k: int,
    ) -> list[RetrievedPolicyChunk]:
        raise NotImplementedError


class CoverageEvaluationRepositoryPort(ABC):
    @abstractmethod
    def save(self, evaluation: CoverageEvaluation) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def get(self, evaluation_id: UUID) -> CoverageEvaluation | None:
        raise NotImplementedError


class AuditRepositoryPort(ABC):
    @abstractmethod
    def save_retrieval_trace(self, payload: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def save_llm_trace(self, payload: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_trace(self, trace_id: str) -> dict | None:
        raise NotImplementedError
