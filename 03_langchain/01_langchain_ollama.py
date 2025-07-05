from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from config import ollama_params

llm = ChatOllama(
    model = "llama3.2:3b",
    temperature=0.1,
    num_predict=300,
    base_url=ollama_params["base_url"],    
)

system_prompt = SystemMessage(content="You translate Russian to English. \
                              Translate the user sentence and write only result:")
print("Start the translation!")
print("To end translation type \"stop\" или \"стоп\"")
while True:
    print("Your message for translation into English:")
    message = input()
    if message.lower() in ("stop", "стоп"):
        break
    history = [system_prompt, HumanMessage(content=message)]
    for chunk in llm.stream(history):
        print(chunk.content, end="")
    print()