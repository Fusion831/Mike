from __future__ import annotations

from uuid import uuid4

from mike.application.ports.repositories import AuditRepositoryPort


class InMemoryAuditRepository(AuditRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def save_retrieval_trace(self, payload: dict) -> str:
        trace_id = f"ret_{uuid4().hex[:12]}"
        self._store[trace_id] = payload
        return trace_id

    def save_llm_trace(self, payload: dict) -> str:
        trace_id = f"llm_{uuid4().hex[:12]}"
        self._store[trace_id] = payload
        return trace_id

    def get_trace(self, trace_id: str) -> dict | None:
        return self._store.get(trace_id)
