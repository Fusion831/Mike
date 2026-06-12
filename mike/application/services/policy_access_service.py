from __future__ import annotations

from datetime import date
from uuid import UUID

from mike.application.ports.repositories import PolicyRepositoryPort
from mike.domain.models import PolicyVersionRef


class PolicyAccessService:
    def __init__(self, policy_repository: PolicyRepositoryPort) -> None:
        self._policy_repository = policy_repository

    def assert_user_policy_access(self, user_id: UUID, policy_id: UUID) -> None:
        self._policy_repository.assert_user_policy_access(user_id=user_id, policy_id=policy_id)

    def resolve_effective_version(self, policy_id: UUID, on_date: date | None = None) -> PolicyVersionRef:
        return self._policy_repository.get_effective_policy_version(policy_id=policy_id, on_date=on_date)
