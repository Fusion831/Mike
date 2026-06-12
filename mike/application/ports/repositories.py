from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any
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

    @abstractmethod
    def register_policy_document(
        self,
        policy_id: UUID,
        version: str,
        filename: str,
        summary: dict[str, Any] | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_policy_summary(self, policy_id: UUID) -> dict[str, Any] | None:
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

    @abstractmethod
    def upsert_chunks(self, policy_id: UUID, chunks: list[RetrievedPolicyChunk]) -> None:
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
