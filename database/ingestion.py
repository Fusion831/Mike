from docling.document_converter import DocumentConverter
from typing import List
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


source = "./RandomFile.pdf"  # file path or URL
converter = DocumentConverter() 
doc = converter.convert(source).document

#print(doc.export_to_markdown())  
data = doc.export_to_markdown()

def chunks(doc : str,chunk_size : int, overlap: int) -> List[str]:
    chunks = []
    #We want to create a ingestion pipeline which has chunk_size splits, and then overlap between them, 
    #My approach is to have a pointer to manage the chunks size to string them, append the string, then afterwards, we decrease 
    #pointer by 50 in it. 
    start = 0
    for i in range(len(doc)):
        if(i + chunk_size >= len(doc)):
            chunks.append(doc[i:])
            return chunks
        currChunk = doc[i:i+chunk_size]
        i = chunk_size - overlap
        chunks.append(currChunk)
        
    return chunks
#Size 384 for embeddings
def embeddings(chunks: List[str]):
    embeds = []
    for chunk in chunks:
        embeds.append(model.encode(chunk))
    return embeds

chunking = chunks(data,300,50)
modelEmbeddings = embeddings



