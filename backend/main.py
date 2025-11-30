from fastapi import FastAPI, UploadFile, File
from backend.services.chunker import chunk_text
from backend.services.pdf_reader import extract_text_from_pdf
from backend.services.pinecone_rag import store_chunks, query_chunks
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware

import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/extract")
async def extract_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    with open("temp.pdf", "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf("temp.pdf")
    chunks = chunk_text(text)

    store_chunks(chunks)

    return {"chunks": chunks}


@app.post("/chat")
async def chat(query: str):
    relevant_chunks = query_chunks(query)
    context = "\n\n".join(relevant_chunks)

    prompt = f"""
Use ONLY the context below to answer the question.

Context:
{context}

Question: {query}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"answer": response.choices[0].message["content"]}
