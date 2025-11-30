from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
import os


# Load env variables
load_dotenv()

app = FastAPI()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX") 


# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_KEY)
index = pc.Index(INDEX_NAME)


# Embeddings + LLM
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini")


@app.get("/")
def home():
    return {"message": "NeuraDocs RAG API is running!"}



# -------------------------
# UPLOAD PDF & STORE VECTORS
# -------------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    reader = PdfReader(file.file)
    text = ""

    # Extract text from PDF
    for page in reader.pages:
        text += page.extract_text()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)

    # Embed
    vectors = embeddings.embed_documents(chunks)

    # Pinecone format
    to_upsert = [
        {
            "id": f"chunk-{i}",
            "values": vector,
            "metadata": {"text": chunks[i]}
        }
        for i, vector in enumerate(vectors)
    ]

    index.upsert(vectors=to_upsert)

    return {"message": "PDF processed successfully!", "chunks": len(chunks)}



# -------------------------
# ASK QUESTION
# -------------------------
class AskRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(req: AskRequest):

    question = req.question

    # Embed question
    q_vector = embeddings.embed_query(question)

    # Vector search
    result = index.query(
        vector=q_vector,
        top_k=5,
        include_metadata=True
    )

    # Build context
    context = "\n".join([m["metadata"]["text"] for m in result["matches"]])

    prompt = f"""
    You are a helpful AI assistant. 
    Use ONLY the following context to answer:

    CONTEXT:
    {context}

    QUESTION:
    {question}
    """

    # LLM response
    response = llm.invoke(prompt)

    return {"answer": response.content}
