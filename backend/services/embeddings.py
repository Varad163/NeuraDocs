from langchain_openai import OpenAIEmbeddings

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

def embed_chunks(chunks):
    return embeddings_model.embed_documents(chunks)

def embed_query(query):
    return embeddings_model.embed_query(query)