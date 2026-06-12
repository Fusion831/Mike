# Coverage Evaluation Architecture

## 1. System Overview

This subsystem provides evidence-grounded policy coverage evaluation for Mike.

Hard constraints:
- The system must not answer from general insurance knowledge.
- Every claim in the answer must be traceable to policy citations.
- Confidence must be categorical (`high`, `medium`, `low`) with rationale.

Architecture style:
- Clean Architecture with inward-only dependencies.
- Domain and application layers define contracts.
- Infrastructure implements adapters for Qdrant, LLM, and persistence.

Layers:
- API layer: FastAPI routers and HTTP contracts.
- Service layer: orchestration use-cases and validation.
- Retrieval layer: retrieve + rerank + evidence packaging.
- LLM layer: structured reasoning from evidence only.
- Repository layer: policy, chunk, evaluation, audit persistence.
- Domain layer: Pydantic entities, enums, and invariants.

## 2. Data Flow Diagrams (Text)

### Evaluation pipeline
1. Client submits coverage question.
2. API maps request to `CoverageQuestion`.
3. `CoverageEvaluationService` checks policy access/version.
4. `RetrievalPort` fetches relevant chunks (policy-filtered).
5. `RerankPort` reranks retrieved chunks.
6. `EvidenceAssemblerService` creates `EvidencePackage`.
7. `CoverageReasoningPort` generates structured answer draft.
8. `CitationValidatorService` validates claim-to-citation traceability.
9. `ConfidenceService` assigns `high|medium|low`.
10. `CoverageEvaluationRepositoryPort` stores evaluation.
11. `AuditRepositoryPort` stores retrieval/LLM traces.
12. API returns answer, reasoning, risks, confidence, and citations.

### Policy ingestion pipeline
1. Client uploads policy PDF.
2. API invokes `PolicyIngestionService`.
3. Parsing adapter converts PDF to markdown and header chunks.
4. Policy summary adapter generates structured `PolicySummary` output.
5. Service stores policy version metadata and all chunks.
6. Service also stores a summary-derived chunk to improve retrieval recall.
7. Coverage evaluation then retrieves from these stored chunks.

### Insufficient evidence branch
1. Evidence package has empty/weak relevant chunks.
2. Reasoning adapter emits `cannot_determine_from_policy`.
3. Confidence becomes `low` with insufficiency flags.
4. Response includes missing-information guidance and audit trace IDs.

## 3. Pydantic Models

Defined in `mike/domain/models.py`:
- `CoverageQuestion`
- `CoverageAnswer`
- `CoverageEvidence`
- `CoverageCitation`
- `CoverageRisk`
- `CoverageEvaluation`
- `ConfidenceAssessment`
- `RetrievedPolicyChunk`
- `EvidencePackage`

Supporting models:
- `RetrievalRequest`, `RetrievalResponse`, `RetrievalMeta`
- `CoverageAnswerDraft`, `ClaimCitationLink`
- `CitationValidationResult`
- `EvaluationAudit`, `EvaluationTrace`
- `PolicyVersionRef`, `RetrievalStrategy`, `EvidenceDiagnostics`

## 4. Service Interfaces

Application services:
- `CoverageEvaluationService`: orchestrates complete workflow.
- `PolicyAccessService`: policy authorization and version resolution.
- `PolicyIngestionService`: document parse + summary generation + chunk registration.
- `EvidenceAssemblerService`: evidence package construction.
- `CitationValidatorService`: claim/citation traceability validation.
- `ConfidenceService`: deterministic confidence assignment.

Ports:
- Retrieval: `RetrievalPort`, `RerankPort`
- LLM: `CoverageReasoningPort`
- Policy parser: `PolicyParserPort`
- Repositories: policy/chunks/evaluations/audit ports

## 5. Repository Interfaces

Defined in `mike/application/ports/repositories.py`:
- `PolicyRepositoryPort`
- `PolicyChunkRepositoryPort`
- `CoverageEvaluationRepositoryPort`
- `AuditRepositoryPort`

In-memory adapters are provided for local runtime and testing.

## 6. API Contracts

### POST /v1/policies/{policy_id}/coverage/evaluations
Request model: `CoverageQuestionInput`
- `question_text`
- `scenario_context`
- `requested_decision_type`
- `session_id`
- `client_request_id`

Response model: `CoverageEvaluationResponse`
- `evaluation_id`
- `processing_status`
- `answer`
- `confidence`
- `citations`
- `audit_ref`

### GET /v1/coverage/evaluations/{evaluation_id}
Returns full stored `CoverageEvaluation` payload.

### GET /v1/coverage/evaluations/{evaluation_id}/trace
Returns retrieval and LLM trace payloads for audit.

### POST /v1/policies/{policy_id}/ingest
Uploads a policy PDF, parses markdown, generates policy summary, and stores chunks.

### POST /v1/policies/{policy_id}/ingest-from-path
Registers a preuploaded PDF from the server `documents/` directory.

### GET /v1/policies/{policy_id}/summary
Returns stored structured policy summary.

## 7. Folder Structure

```
mike/
  api/
    dependencies.py
    schemas.py
    routers/
      coverage_evaluation_router.py
      policy_ingestion_router.py
  application/
    ports/
      repositories.py
      retrieval_port.py
      llm_reasoning_port.py
      policy_parser_port.py
    services/
      coverage_evaluation_service.py
      policy_access_service.py
      policy_ingestion_service.py
      evidence_assembler_service.py
      citation_validator_service.py
      confidence_service.py
  domain/
    enums.py
    models.py
  infrastructure/
    parsing/
      policy_parser_adapter.py
    llm/
      gemini_coverage_reasoning_adapter.py
    retrieval/
      qdrant_retrieval_adapter.py
      simple_rerank_adapter.py
      local_policy_chunk_repository.py
    repositories/
      in_memory_policy_repository.py
      in_memory_coverage_evaluation_repository.py
      in_memory_audit_repository.py
main.py
```

## 8. Example Request/Response Payloads

### Request
```json
{
  "question_text": "Will physical therapy be covered after surgery?",
  "scenario_context": {
    "procedure": "knee surgery",
    "provider_network_status": "in_network",
    "prior_authorization_status": "unknown"
  },
  "requested_decision_type": "coverage",
  "client_request_id": "req-001"
}
```

### Response (shape)
```json
{
  "evaluation_id": "0aab7ef9-e618-47ca-97dc-bbe0fbcf8364",
  "processing_status": "completed",
  "answer": {
    "decision": "conditionally_covered",
    "short_answer": "...",
    "detailed_reasoning": "...",
    "conditions": ["..."],
    "next_steps": ["..."],
    "evidence": {
      "summary": "...",
      "supporting_citations": [],
      "contradicting_citations": [],
      "unresolved_ambiguities": [],
      "missing_information_needed": []
    },
    "risks": []
  },
  "confidence": {
    "level": "medium",
    "rationale": "...",
    "factors": [],
    "insufficiency_flags": [],
    "policy_grounding_status": "partially_grounded"
  },
  "citations": [],
  "audit_ref": {
    "retrieval_trace_id": "ret_xxx",
    "llm_trace_id": "llm_xxx",
    "prompt_version": "coverage_eval_v1",
    "model_name": "gemini-2.5-flash"
  }
}
```

## 9. Sequence Diagram (Text)

1. API receives request.
2. Service validates policy access/version.
3. Retrieval adapter queries chunk repository (Qdrant contract).
4. Reranker orders candidate chunks.
5. Evidence package built with diagnostics and gaps.
6. Gemini adapter generates structured `CoverageAnswerDraft`.
7. Citation validator enforces claim traceability.
8. Confidence service sets categorical confidence.
9. Evaluation and traces are persisted.
10. API returns a legally auditable result payload.

## 10. Future Extension Points

The design supports new verticals by adding domain-specific question/answer models while reusing shared evidence-grounding primitives.

Planned expansions:
- Claim denial analysis: add denial-specific risk taxonomy and reasoning prompts.
- Appeal generation: add draft-generation service consuming prior evaluations.
- Rental agreements: add contract-domain chunk metadata and risks.
- Traffic citations: add jurisdiction-aware retrieval filters and rule maps.

Reuse strategy:
- Keep `EvidencePackage`, citation validation, and confidence scoring core logic.
- Introduce additional use-case services and adapter prompts per domain.
