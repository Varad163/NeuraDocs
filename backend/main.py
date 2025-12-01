from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
import os
import logging

from services.pdf_reader import extract_text_from_pdf
from services.chunker import chunk_text

from openai import OpenAI

# Load environment
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

client = OpenAI(api_key=OPENAI_KEY)

# Try Pinecone
pinecone_ok = False
try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=PINECONE_KEY)
    index = pc.Index(PINECONE_INDEX)
    pinecone_ok = True
    logging.info("Pinecone initialized.")
except Exception as e:
    logging.warning(f"Pinecone disabled: {e}")
    index = None

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Model for Ask endpoint
class AskBody(BaseModel):
    query: str


@app.post("/extract")
async def extract_endpoint(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        text = extract_text_from_pdf(pdf_bytes)
        chunks = chunk_text(text)

        # Embed & insert into Pinecone
        if pinecone_ok:
            vectors = []
            for i, chunk in enumerate(chunks):
                emb = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=chunk
                ).data[0].embedding

                vectors.append({
                    "id": f"{file.filename}_{i}",
                    "values": emb,
                    "metadata": {"text": chunk}
                })

            index.upsert(vectors)

        return {"chunks": chunks}

    except Exception as e:
        logging.exception("Error in /extract")
        return {"error": str(e)}


@app.post("/ask")
async def ask_question(body: AskBody):
    try:
        q = body.query

        # Query embedding
        q_emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=q
        ).data[0].embedding

        # Query Pinecone
        matches = []
        if pinecone_ok:
            result = index.query(
                vector=q_emb,
                top_k=5,
                include_metadata=True
            )
            matches = result["matches"]

        # Build context
        context = " ".join([m["metadata"]["text"] for m in matches])

        # Chat completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant for PDF Q&A."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {q}"}
            ]
        )

        answer = response.choices[0].message["content"]

        return {"answer": answer}

    except Exception as e:
        logging.exception("Error in /ask")
        return {"error": str(e)}
