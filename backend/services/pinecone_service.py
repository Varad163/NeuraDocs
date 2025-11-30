from pinecone import Pinecone
from utils.config import PINECONE_API_KEY, PINECONE_INDEX

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

def upsert_chunks(chunks, vectors):
    records = []
    for i, vector in enumerate(vectors):
        records.append((str(i), vector, {"text": chunks[i]}))

    index.upsert(records)

def query_pinecone(vector, top_k=5):
    return index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True
    )
