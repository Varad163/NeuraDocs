from fastapi import FastAPI, UploadFile, File

from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
import os


load_dotenv()

app = FastAPI()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX") 

pc = Pinecone(api_key=PINECONE_KEY)
index = pc.Index(INDEX_NAME)


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

llm = ChatOpenAI(model="gpt-4o-mini")


@app.get("/")
def home():
    return {"message": "PDF Chat API is running!"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    reader = PdfReader(file.file)
    text = ""

   
    for page in reader.pages:
        text += page.extract_text()

   
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)

  
    vectors = embeddings.embed_documents(chunks)

    upserts = []
    for i, vector in enumerate(vectors):
        upserts.append((str(i), vector, {"text": chunks[i]}))

    index.upsert(upserts)

    return {"message": "PDF processed successfully!", "chunks": len(chunks)}


@app.post("/ask")
async def ask_question(question: str):
    q_vector = embeddings.embed_query(question)

    result = index.query(vector=q_vector, top_k=5, include_metadata=True)

    context = ""
    for match in result["matches"]:
        context += match["metadata"]["text"] + "\n"

    prompt = f"""
    Use the following context to answer the user's question.

    CONTEXT:
    {context}

    QUESTION:
    {question}
    """

    response = llm.invoke(prompt)

    return {"answer": response.content}
