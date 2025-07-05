from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import ollama_params

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.1,
    num_predict=200,
    base_url=ollama_params["base_url"],
)
messages = [
    ("system", "You are a very good translator. Translate given sentence into {target} language"),
    MessagesPlaceholder("history"),
]
prompt_template = ChatPromptTemplate(messages)
target = input("Enter the target language for translation: ")
print("To change the language, write \"change\"")
print("To end the chat, type \"stop\"")
history = []
while True:
    user_input = input("Text to translate: ")
    if user_input.lower() == "stop":
        break
    if user_input.lower() == "change":
        target = input("Enter the target language for translation: ")
        user_input = input("Text to translate: ")

    history.append(HumanMessage(content=user_input))
    prompt_value = prompt_template.invoke({"target": target, "history": history})
    ai_translate = ""
    print("Translate: ", end="")
    for ai_message_chunk in llm.stream(prompt_value.to_messages()):
        print(ai_message_chunk.content, end="", flush=True)
        ai_translate += ai_message_chunk.content
        
    history.append(AIMessage(content=ai_translate))
    print()
print("Bye, bro")