
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import logging
from dotenv import load_dotenv

from groq import Groq
from services.pdf_reader import extract_text_from_pdf
from services.chunker import chunk_text

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

groq_client = Groq(api_key=GROQ_API_KEY)

pinecone_ok = False
index = None

try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX)
    pinecone_ok = True
    logging.info("Pinecone initialized successfully.")
except Exception as e:
    logging.warning(f"Pinecone not available: {e}")

# -----------------------------
# FastAPI App Setup
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskBody(BaseModel):
    query: str


@app.post("/extract")
async def extract_endpoint(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        text = extract_text_from_pdf(pdf_bytes)
        chunks = chunk_text(text)

        if pinecone_ok:
            vectors = []
            for i, chunk in enumerate(chunks):


                from openai import OpenAI
                OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
                client = OpenAI(api_key=OPENAI_API_KEY)

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
        print("User Query:", q)

        if not pinecone_ok:
     
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You answer questions about uploaded PDF text."},
                    {"role": "user", "content": q}
                ]
            )
            return {"answer": completion.choices[0].message.content}

        from openai import OpenAI
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=OPENAI_API_KEY)

        q_emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=q
        ).data[0].embedding

        result = index.query(
            vector=q_emb,
            top_k=5,
            include_metadata=True
        )

        matches = result.matches
        if not matches:
            return {"answer": "No relevant content found in PDF."}

        context = " ".join([m.metadata["text"] for m in matches])

        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You answer using PDF context."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {q}"}
            ]
        )

        answer = completion.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        logging.exception("Error in /ask")
        return {"error": str(e)}

