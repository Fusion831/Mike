from __future__ import annotations

from langchain_core.documents import Document

from mike.application.ports.policy_parser_port import PolicyParserPort
from policy.fileIngestion import parse_headers, parse_markdown
from policy.policyAgent import generate_policy


class PolicyParserAdapter(PolicyParserPort):
    async def parse_pdf_to_markdown(self, source: str) -> str:
        return await parse_markdown(source)

    async def split_markdown_headers(self, markdown: str) -> list[Document]:
        return await parse_headers(markdown)

    async def generate_structured_summary(self, markdown: str):
        return await generate_policy(markdown)
