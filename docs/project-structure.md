# Project Structure

## Current layout

- `main.py`: FastAPI entrypoint and router registration.
- `mike/`: primary backend package for clean architecture layers.
  - `api/`: HTTP routers, schemas, dependency wiring.
  - `application/`: orchestration services and ports/interfaces.
  - `domain/`: enums and Pydantic domain models.
  - `infrastructure/`: adapters for parsing, retrieval, llm, repositories.
- `policy/`: policy-specific extraction and summary generation components.
  - `fileIngestion.py`: Docling + markdown header splitting.
  - `policyAgent.py`: Gemini structured policy summary generation.
  - `models.py`: `PolicySummary` schema.
- `documents/`: local source PDFs.
- `docs/`: architecture and operational docs.

## Recommended flow

1. Upload/ingest PDF via policy ingestion endpoint.
2. Parse + summarize policy text.
3. Store chunks and summary-derived chunk in repository.
4. Run coverage evaluation endpoint.
5. Retrieve and reason only over stored policy evidence.

## Why this organization

- Keeps policy parsing concerns separate from coverage evaluation orchestration.
- Allows replacing adapters (Qdrant, LLM, storage) without changing domain logic.
- Ensures policy summary artifacts are first-class retrieval evidence.
