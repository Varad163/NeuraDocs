from fastapi import FastAPI, UploadFile, File
from services.chunker import chunk_text
from services.chunker import chunk_text
from services.pdf_reader import extract_text_from_pdf

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
    try:
        # read pdf bytes
        pdf_bytes = await file.read()

        # extract text
        text = extract_text_from_pdf(pdf_bytes)

        # split into chunks (we fix this too)
        chunks = chunk_text(text)

        return {"chunks": chunks}
    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}


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
