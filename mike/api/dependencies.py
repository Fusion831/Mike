from __future__ import annotations

from mike.application.services.citation_validator_service import CitationValidatorService
from mike.application.services.confidence_service import ConfidenceService
from mike.application.services.coverage_evaluation_service import CoverageEvaluationService
from mike.application.services.evidence_assembler_service import EvidenceAssemblerService
from mike.application.services.policy_ingestion_service import PolicyIngestionService
from mike.application.services.policy_access_service import PolicyAccessService
from mike.infrastructure.parsing.policy_parser_adapter import PolicyParserAdapter
from mike.infrastructure.llm.gemini_coverage_reasoning_adapter import GeminiCoverageReasoningAdapter
from mike.infrastructure.repositories.in_memory_audit_repository import InMemoryAuditRepository
from mike.infrastructure.repositories.in_memory_coverage_evaluation_repository import (
    InMemoryCoverageEvaluationRepository,
)
from mike.infrastructure.repositories.in_memory_policy_repository import InMemoryPolicyRepository
from mike.infrastructure.retrieval.local_policy_chunk_repository import LocalPolicyChunkRepository
from mike.infrastructure.retrieval.qdrant_retrieval_adapter import QdrantRetrievalAdapter
from mike.infrastructure.retrieval.simple_rerank_adapter import SimpleRerankAdapter


class Container:
    def __init__(self) -> None:
        self.policy_repository = InMemoryPolicyRepository()
        self.chunk_repository = LocalPolicyChunkRepository()
        self.evaluation_repository = InMemoryCoverageEvaluationRepository()
        self.audit_repository = InMemoryAuditRepository()
        self.policy_parser_adapter = PolicyParserAdapter()

        self.policy_access_service = PolicyAccessService(self.policy_repository)
        self.policy_ingestion_service = PolicyIngestionService(
            policy_repository=self.policy_repository,
            chunk_repository=self.chunk_repository,
            parser_adapter=self.policy_parser_adapter,
        )
        self.retrieval_adapter = QdrantRetrievalAdapter(self.chunk_repository)
        self.rerank_adapter = SimpleRerankAdapter()
        self.evidence_assembler = EvidenceAssemblerService()
        self.reasoning_adapter = GeminiCoverageReasoningAdapter()
        self.citation_validator = CitationValidatorService()
        self.confidence_service = ConfidenceService()

        self.coverage_evaluation_service = CoverageEvaluationService(
            policy_access_service=self.policy_access_service,
            retrieval_port=self.retrieval_adapter,
            rerank_port=self.rerank_adapter,
            evidence_assembler=self.evidence_assembler,
            reasoning_port=self.reasoning_adapter,
            citation_validator=self.citation_validator,
            confidence_service=self.confidence_service,
            evaluation_repository=self.evaluation_repository,
            audit_repository=self.audit_repository,
        )


container = Container()
