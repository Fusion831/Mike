from __future__ import annotations

from uuid import UUID

from mike.application.ports.repositories import CoverageEvaluationRepositoryPort
from mike.domain.models import CoverageEvaluation


class InMemoryCoverageEvaluationRepository(CoverageEvaluationRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, CoverageEvaluation] = {}

    def save(self, evaluation: CoverageEvaluation) -> UUID:
        self._store[evaluation.evaluation_id] = evaluation
        return evaluation.evaluation_id

    def get(self, evaluation_id: UUID) -> CoverageEvaluation | None:
        return self._store.get(evaluation_id)
