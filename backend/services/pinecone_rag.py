import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = os.getenv("PINECONE_INDEX_NAME")
region = os.getenv("PINECONE_REGION")

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=region
        )
    )

index = pc.Index(index_name)

model = SentenceTransformer("all-MiniLM-L6-v2")

def store_chunks(chunks):
    vectors = []
    for i, chunk in enumerate(chunks):
        emb = model.encode(chunk).tolist()
        vectors.append({
            "id": f"chunk_{i}",
            "values": emb,
            "metadata": {"text": chunk},
        })

    index.upsert(vectors=vectors)

def query_chunks(query):
    emb = model.encode(query).tolist()
    results = index.query(
        vector=emb,
        top_k=5,
        include_metadata=True
    )
    return [match["metadata"]["text"] for match in results["matches"]]
