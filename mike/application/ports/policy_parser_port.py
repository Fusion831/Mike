from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document


class PolicyParserPort(ABC):
    @abstractmethod
    async def parse_pdf_to_markdown(self, source: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def split_markdown_headers(self, markdown: str) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    async def generate_structured_summary(self, markdown: str) -> Any:
        raise NotImplementedError
