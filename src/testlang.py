from langchain_community.chat_models import ChatLlamaCpp
import multiprocessing

llm = ChatLlamaCpp(
    model_path = "models/kokos.gguf",
    max_tokens = 0,
    n_threads = multiprocessing.cpu_count() - 1,
)

messages = [
    ("system", ""), ("human", "Приве!"),
]

msg = llm.invoke(messages)
print(msg.content)
