from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import json
import logging
from dotenv import load_dotenv
from groq import Groq

from services.pdf_reader import extract_text_from_pdf
from services.chunker import chunk_text

# Load ENV
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not found in .env")

groq_client = Groq(api_key=GROQ_API_KEY)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data/chunks.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# FastAPI
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

def save_chunks(chunks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

def load_chunks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/extract")
async def extract_endpoint(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        text = extract_text_from_pdf(pdf_bytes)
        chunks = chunk_text(text)

        save_chunks(chunks)
        return {"chunks": chunks, "message": "PDF extracted successfully!"}

    except Exception as e:
        logging.exception("Error in /extract")
        return {"error": str(e)}

@app.post("/ask")
async def ask_question(body: AskBody):
    try:
        q = body.query.strip()
        print("User Query:", q)

        chunks = load_chunks()
        if not chunks:
            return {"answer": "No PDF extracted yet. Please upload a PDF first."}

        q_words = [w.lower() for w in q.split() if len(w) > 2]

        scored = []
        for chunk in chunks:
            score = sum(w in chunk.lower() for w in q_words)
            scored.append((score, chunk))

        scored.sort(reverse=True, key=lambda x: x[0])
        best_chunks = [c for s, c in scored[:5]]

        context = "\n\n".join(best_chunks)

        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You answer strictly using the context from the uploaded PDF."
                },
                {
                    "role": "user",
                    "content": f"PDF Context:\n{context}\n\nQuestion: {q}"
                }
            ]
        )

        return {"answer": completion.choices[0].message.content}

    except Exception as e:
        logging.exception("Error in /ask")
        return {"error": str(e)}
