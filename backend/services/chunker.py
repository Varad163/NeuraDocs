# backend/services/chunker.py

from typing import List

# Try to import RecursiveCharacterTextSplitter from langchain_text_splitters if available
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    _HAS_LANGCHAIN_SPLITTER = True
except Exception:
    _HAS_LANGCHAIN_SPLITTER = False

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
    """
    Return list of chunks. Prefer langchain's splitter if installed, else fallback to a simple word-based chunker.
    """
    if not text:
        return []

    if _HAS_LANGCHAIN_SPLITTER:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        return splitter.split_text(text)

    # fallback: word-based greedy chunking
    words = text.split()
    chunks = []
    current = []
    for w in words:
        if len(" ".join(current + [w])) > chunk_size:
            chunks.append(" ".join(current))
            current = [w]
        else:
            current.append(w)

    if current:
        chunks.append(" ".join(current))
    return chunks
