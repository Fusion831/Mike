from __future__ import annotations

from docling.document_converter import DocumentConverter
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter


async def parse_pdf_to_markdown(source: str) -> str:
    converter = DocumentConverter()
    doc = converter.convert(source).document
    data = doc.export_to_markdown()
    return data


async def split_markdown_headers(markdown: str) -> list[Document]:
    headers_to_split_on = [
        ("#", "Chapter"),
        ("##", "Section"),
        ("###", "Subsection"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
    )
    markdown_chunks = markdown_splitter.split_text(markdown)
    return markdown_chunks
