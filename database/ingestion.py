from docling.document_converter import DocumentConverter
from typing import List
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue
import uuid



model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = QdrantClient(":memory:")

source = "./RandomFile.pdf"  # file path or URL
client.create_collection(
    "manual_Ingestion",
    vectors_config = VectorParams(size = 384, distance = Distance.DOT)
)
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
    while start < len(doc):
        chunk = doc[start:start+chunk_size]
        chunks.append(chunk)
        start += (chunk_size - overlap)
        
    return chunks
#Size 384 for embeddings
def embeddings(chunks: List[str]) -> List[List[float]]:
    embeds = []
    for chunk in chunks:
        embeds.append(model.encode(chunk))
    return embeds

chunking = chunks(data,300,50)
modelEmbeddings = embeddings(chunking)
print(f"Length of Embeddings: {len(modelEmbeddings[0])}")


Points = []

for chunk,embedding in zip(chunking,modelEmbeddings):
    my_uuid = uuid.uuid4()
    id = my_uuid.int
    Points.append(PointStruct(id = id, vector = embedding,payload = {"text":chunk} ))

    
client.upsert(
    collection_name = "manual_Ingestion",
    wait = True,
    points = Points,
    
)

Query = "What is a distributed Database?"
query = model.encode(Query)

search_result = client.query_points(
    collection_name = "manual_Ingestion",
    query = query,
    with_payload = True,
    limit = 3,
).points

print(search_result)


