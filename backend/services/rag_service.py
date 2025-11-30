from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def build_prompt(context, question):
    return f"""
    Use the context below to answer the user's question.

    ===== CONTEXT =====
    {context}

    ===== QUESTION =====
    {question}

    Provide the best possible answer based on the context.
    """

def generate_answer(context, question):
    prompt = build_prompt(context, question)
    response = llm.invoke(prompt)
    return response.content
