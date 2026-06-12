from __future__ import annotations

import time
from datetime import date
from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException

from mike.models import (
    CoverageEvaluation,
    PolicyVersionRef,
    RetrievedPolicyChunk,
    SourceType,
)


class Storage:
    def __init__(self) -> None:
        # Policy repositories in-memory store
        self._policy_versions: dict[UUID, str] = {}
        self._policy_summaries: dict[UUID, dict[str, Any]] = {}
        self._policy_filenames: dict[UUID, str] = {}

        # Chunk repositories in-memory store
        self._chunks: dict[UUID, list[RetrievedPolicyChunk]] = {}

        # Evaluation repositories in-memory store
        self._evaluations: dict[UUID, CoverageEvaluation] = {}

        # Audit repositories in-memory store
        self._audit_traces: dict[str, dict] = {}

    # Policy methods
    def seed_policy(self, policy_id: UUID, version: str = "v1") -> None:
        self._policy_versions[policy_id] = version

    def assert_user_policy_access(self, user_id: UUID, policy_id: UUID) -> None:
        # Replace with real ACL in production.
        if policy_id not in self._policy_versions:
            raise HTTPException(status_code=403, detail="Policy access denied or policy not found")

    def get_effective_policy_version(self, policy_id: UUID, on_date: date | None = None) -> PolicyVersionRef:
        version = self._policy_versions.get(policy_id)
        if version is None:
            raise HTTPException(status_code=409, detail="Policy version could not be resolved")
        return PolicyVersionRef(policy_id=policy_id, version=version)

    def register_policy_document(
        self,
        policy_id: UUID,
        version: str,
        filename: str,
        summary: dict[str, Any] | None,
    ) -> None:
        self._policy_versions[policy_id] = version
        self._policy_filenames[policy_id] = filename
        if summary is not None:
            self._policy_summaries[policy_id] = summary

    def get_policy_summary(self, policy_id: UUID) -> dict[str, Any] | None:
        return self._policy_summaries.get(policy_id)

    # Chunk methods
    def seed_chunks(self, policy_id: UUID, chunks: list[RetrievedPolicyChunk]) -> None:
        self._chunks[policy_id] = chunks

    def upsert_chunks(self, policy_id: UUID, chunks: list[RetrievedPolicyChunk]) -> None:
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

    # Evaluation methods
    def save_evaluation(self, evaluation: CoverageEvaluation) -> UUID:
        self._evaluations[evaluation.evaluation_id] = evaluation
        return evaluation.evaluation_id

    def get_evaluation(self, evaluation_id: UUID) -> CoverageEvaluation | None:
        return self._evaluations.get(evaluation_id)

    # Audit/trace methods
    def save_retrieval_trace(self, payload: dict) -> str:
        trace_id = f"ret_{uuid4().hex[:12]}"
        self._audit_traces[trace_id] = payload
        return trace_id

    def save_llm_trace(self, payload: dict) -> str:
        trace_id = f"llm_{uuid4().hex[:12]}"
        self._audit_traces[trace_id] = payload
        return trace_id

    def get_trace(self, trace_id: str) -> dict | None:
        return self._audit_traces.get(trace_id)


# Global singleton storage instance
storage = Storage()
