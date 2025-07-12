from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from config import mistral_params

chat_history = InMemoryChatMessageHistory()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a very good translator. Translate given sentence into {target} language"),
        ("placeholder", "chat_history"),
        ("human", "{input_question}"),
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
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.1,
    mistral_api_key=mistral_params["api_key"]
)
base_chain = prompt | trimmer | llm
chain = RunnableWithMessageHistory(
    base_chain, lambda session_id: chat_history,
    input_messages_key="input_question",
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
        "input": user_input,}, config={{"configurable": {"session_id": "unused"}}}):
        print(ai_message_chunk.content, end="", flush=True)
    print()
print("Bye, bro")