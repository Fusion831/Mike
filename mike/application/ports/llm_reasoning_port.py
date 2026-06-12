from __future__ import annotations

from abc import ABC, abstractmethod

from mike.domain.models import CoverageAnswerDraft, CoverageQuestion, EvidencePackage


class CoverageReasoningPort(ABC):
    @abstractmethod
    def evaluate(self, question: CoverageQuestion, evidence: EvidencePackage) -> CoverageAnswerDraft:
        raise NotImplementedError
