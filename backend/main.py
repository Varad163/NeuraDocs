from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.chunker import chunk_text
from services.pdf_reader import extract_text_from_pdf
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keys
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX")

client = OpenAI(api_key=OPENAI_KEY)

pc = Pinecone(api_key=PINECONE_KEY)
index = pc.Index(INDEX_NAME)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini")


@app.post("/extract")
async def extract_endpoint(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()

        # Extract text
        text = extract_text_from_pdf(pdf_bytes)

        # Make chunks
        chunks = chunk_text(text)

        # Upload to Pinecone
        vectors = []
        for i, chunk in enumerate(chunks):
            emb = embeddings.embed_query(chunk)
            vectors.append({
                "id": f"{file.filename}-{i}",
                "values": emb,
                "metadata": {"text": chunk}
            })

        index.upsert(vectors)

        return {"chunks": chunks, "message": "Uploaded to Pinecone!"}

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}


@app.post("/ask")
async def ask_question(query: str):
    try:
        q_emb = embeddings.embed_query(query)

        result = index.query(
            vector=q_emb,
            top_k=5,
            include_metadata=True
        )

        docs = " ".join([m["metadata"]["text"] for m in result["matches"]])

        response = llm.predict(
            f"Use the following PDF context:\n{docs}\n\nQuestion: {query}"
        )

        return {"answer": response}

    except Exception as e:
        return {"error": str(e)}
