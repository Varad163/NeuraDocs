from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_text(text):
    splitter=RecursiveCharacterTextSplitter(
        chunk_sizes=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)
    