from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from config import mistral_params

chat_history = InMemoryChatMessageHistory()

prompt = ChatPromptTemplate(
    [
        ("system", "You are a very good translator. Translate given sentence into {target} language"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)
trimmer = trim_messages(
    strategy="last",
    token_counter=len,
    max_tokens=10,
    start_on="human",
    end_on="human",
    include_system=True,
    allow_partial=False
)
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.1,)

base_chain = prompt | trimmer | llm
chain = RunnableWithMessageHistory(
    base_chain, lambda session_id: chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
) | StrOutputParser() # add parsing

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

    print("Translate: ", end="")
    for ai_message_chunk in chain.stream({
        "target": target,
        "input": user_input,}, config={"configurable": {"session_id": "unused"}}):
        print(ai_message_chunk, end="", flush=True)
    print()
print("Bye, bro")