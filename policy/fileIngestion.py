from docling.document_converter import DocumentConverter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from typing import List
from langchain_core.documents import Document




async def parse_markdown(source : str) -> str:
    converter = DocumentConverter()
    doc = converter.convert(source).document
    data = doc.export_to_markdown()
    return data

async def parse_headers(markdown) -> List[Document]:
    headers_to_split_on = [
    ("#", "Chapter"),       
    ("##", "Section"),      
    ("###", "Subsection"),  
    ]
    markdownSplitter = MarkdownHeaderTextSplitter(
        headers_to_split_on = headers_to_split_on,
    )
    MarkdownChunks = markdownSplitter.split_text(markdown)
    return MarkdownChunks