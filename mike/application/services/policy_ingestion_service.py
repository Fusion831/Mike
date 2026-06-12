from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from uuid import UUID

from mike.application.ports.policy_parser_port import PolicyParserPort
from mike.application.ports.repositories import PolicyChunkRepositoryPort, PolicyRepositoryPort
from mike.domain.enums import SourceType
from mike.domain.models import RetrievedPolicyChunk


class PolicyIngestionService:
    def __init__(
        self,
        policy_repository: PolicyRepositoryPort,
        chunk_repository: PolicyChunkRepositoryPort,
        parser_adapter: PolicyParserPort,
    ) -> None:
        self._policy_repository = policy_repository
        self._chunk_repository = chunk_repository
        self._parser_adapter = parser_adapter

    @staticmethod
    def _estimate_token_count(text: str) -> int:
        return max(len(text.split()), 1)

    @staticmethod
    def _build_summary_text(summary: dict) -> str:
        return json.dumps(summary, ensure_ascii=True)

    async def ingest_pdf_bytes(
        self,
        *,
        policy_id: UUID,
        filename: str,
        file_bytes: bytes,
        policy_version: str = "v1",
    ) -> dict:
        suffix = os.path.splitext(filename)[1] or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        try:
            markdown_data = await self._parser_adapter.parse_pdf_to_markdown(temp_path)
            header_chunks = await self._parser_adapter.split_markdown_headers(markdown_data)

            raw_summary = await self._parser_adapter.generate_structured_summary(markdown_data)
            if hasattr(raw_summary, "model_dump"):
                summary_data = raw_summary.model_dump(mode="json")
            elif isinstance(raw_summary, dict):
                summary_data = raw_summary
            else:
                summary_data = {"summary_text": str(raw_summary)}

            retrieved_chunks: list[RetrievedPolicyChunk] = []
            document_id = f"policy_{policy_id}"

            for idx, chunk in enumerate(header_chunks):
                metadata = chunk.metadata or {}
                page_number = metadata.get("page")
                if isinstance(page_number, str) and page_number.isdigit():
                    page_number = int(page_number)
                if not isinstance(page_number, int):
                    page_number = None

                retrieved_chunks.append(
                    RetrievedPolicyChunk(
                        chunk_id=f"{policy_id}-md-{idx+1}",
                        document_id=document_id,
                        policy_id=policy_id,
                        heading=metadata.get("Section") or metadata.get("Chapter"),
                        subsection=metadata.get("Subsection"),
                        page_number=page_number,
                        chunk_text=chunk.page_content,
                        token_count=self._estimate_token_count(chunk.page_content),
                        source_type=SourceType.POLICY_CONTRACT,
                        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                        retrieval_score=0.0,
                        metadata={k: str(v) for k, v in metadata.items()},
                        version_tag=policy_version,
                    )
                )

            summary_text = self._build_summary_text(summary_data)
            retrieved_chunks.append(
                RetrievedPolicyChunk(
                    chunk_id=f"{policy_id}-summary-1",
                    document_id=document_id,
                    policy_id=policy_id,
                    heading="Policy Summary",
                    subsection="Structured Summary",
                    page_number=None,
                    chunk_text=summary_text,
                    token_count=self._estimate_token_count(summary_text),
                    source_type=SourceType.SUMMARY_OF_BENEFITS,
                    embedding_model="summary-json",
                    retrieval_score=0.0,
                    metadata={"generated_by": "policy.policyAgent.generate_policy"},
                    version_tag=policy_version,
                )
            )

            self._policy_repository.register_policy_document(
                policy_id=policy_id,
                version=policy_version,
                filename=filename,
                summary=summary_data,
            )
            self._chunk_repository.upsert_chunks(policy_id=policy_id, chunks=retrieved_chunks)

            return {
                "policy_id": str(policy_id),
                "version": policy_version,
                "filename": filename,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "markdown_chunk_count": len(header_chunks),
                "total_chunk_count": len(retrieved_chunks),
                "summary_generated": True,
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def ingest_pdf_path(
        self,
        *,
        policy_id: UUID,
        file_path: str,
        policy_version: str = "v1",
    ) -> dict:
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as source_file:
            data = source_file.read()
        return await self.ingest_pdf_bytes(
            policy_id=policy_id,
            filename=filename,
            file_bytes=data,
            policy_version=policy_version,
        )

    def get_policy_summary(self, policy_id: UUID) -> dict | None:
        return self._policy_repository.get_policy_summary(policy_id)
