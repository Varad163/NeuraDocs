from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backend.services.chunker import chunk_text
from backend.services.pdf_reader import extract_text_from_pdf

app = FastAPI(title="NeuraDocs API")

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/extract")
def extract_endpoint(path: str):
    try:
        text = extract_text_from_pdf(path)
        chunks = chunk_text(text)
        return JSONResponse({"chunks": len(chunks)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
