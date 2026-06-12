from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from fastapi import HTTPException

from mike.application.ports.repositories import PolicyRepositoryPort
from mike.domain.models import PolicyVersionRef


class InMemoryPolicyRepository(PolicyRepositoryPort):
    def __init__(self) -> None:
        self._policy_versions: dict[UUID, str] = {}
        self._policy_summaries: dict[UUID, dict[str, Any]] = {}
        self._policy_filenames: dict[UUID, str] = {}

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
