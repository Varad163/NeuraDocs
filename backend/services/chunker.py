from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)
