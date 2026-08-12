from langchain_ollama import ChatOllama


model = ChatOllama(
    model="llama3.2",
    temperature=0,
)


async def ask_model(question: str) -> str:
    response = await model.ainvoke(question)
    return response.content