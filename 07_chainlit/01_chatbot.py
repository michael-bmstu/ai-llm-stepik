import chainlit as cl
from chainlit.input_widget import Select, Slider, TextInput

from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory, BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

import os
from dotenv import load_dotenv

load_dotenv()

session_store = dict()

def get_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

messages = [
    ("system", "You are an expert in {domain}. Your task is answer the question as short as possible"),
    ("placeholder", "{history}"),
    ("human", "{question}"),
]
prompt = ChatPromptTemplate(messages)

@cl.on_message # message processing
async def handle_message(message: cl.Message):
    # get user's vars
    model = cl.user_session.get("model", "mistral-large-latest")
    temp = cl.user_session.get("temp", 1)
    user_session = cl.user_session.get("id")
    domain = cl.user_session.get("domain", "Python programming")
    name = cl.user_session.get("name", "bro")
    thanks_msg = cl.Message(content=f"Thank you fot the question, {name}!")
    await thanks_msg.send()

    # define chain from settings
    llm = init_chat_model(model=model, temperature=temp, api_key=os.getenv("MISTRAL_KEY"))
    chain = RunnableWithMessageHistory(
        prompt | llm, get_session_history=get_history,
        input_messages_key="question", history_messages_key="history",
        ) | StrOutputParser()
    
    question = message.content
    thanks_action = cl.Action(
        label="❤",
        name="thanks_action",
        payload={"user_session_id": user_session},
        tooltip="Send thanks for the helpful reply"
    )
    dislike = cl.Action(
        label="dislike",
        name="dislike_action",
        payload={"user_session_id": user_session},
        tooltip="Send dislike for the bad answer",
    )

    msg = cl.Message(content="", actions=[thanks_action, dislike]) # create message
    async for chunk in chain.astream(
        {"domain": domain, "question": question, "history": messages}, 
        config=RunnableConfig(configurable={"session_id": user_session})
    ):
        await msg.stream_token(chunk)

    await msg.send() # close generation
    await thanks_msg.remove() # remove tmp message

# Actions processing
@cl.action_callback("thanks_action")
async def on_action(action: cl.Action):
    name = cl.user_session.get("name", "bro")
    print("message id:", action.forId, "action payload:", action.payload)
    await action.remove()
    await cl.Message(content=f"Thank you, {name}!").send()

@cl.action_callback("dislike_action")
async def on_action(action: cl.Action):
    name = cl.user_session.get("name", "bro")
    print("message id:", action.forId, "action payload:", action.payload)
    await action.remove()
    await cl.Message(content=f"Thank you for feedback, {name}!").send()

# Chat profile
@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Domain Chat-Bot",
            markdown_description="A chatbot that will help you in the domain you selected at the beginning of the dialogue",
            starters=[cl.Starter(label="Hello world", message="What is hello world in different domains"),],
        ),]

# What program do when chat is started
@cl.on_chat_start
async def main_start():
    # get user name, for dialogue
    ask = cl.AskUserMessage(content="Write your name, please", timeout=20)
    res = await ask.send()
    if res:
        name = res["output"]
        cl.user_session.set("name", name)
        await cl.Message(content=f"Hello, {name}").send()
    else:
        await ask.remove()
    
    # define chat settings (add icon with settings to chat)
    settings = cl.ChatSettings(
        [
            Select(
                id="model", label="Model", description="LLM model selection",
                values=["mistral-large-latest", "mistral-small-latest", "codestral-lates"], 
                initial_index=0
            ),
            TextInput(
                id="domain", label="LLM Domain", initial="Pyhton programming",
                placeholder="Type domain here",
                multiline=False
            ),
            Slider(
                id="temp", label="Temperature",
                initial=1, min=0, max=2, step=0.1,
            ),
        ]
    )
    await settings.send()

@cl.on_settings_update # process settings "confirm" button
async def setup_chat(settings):
    cl.user_session.set("model", settings["model"])
    cl.user_session.set("domain", settings["domain"])
    cl.user_session.set("temp", settings["temp"])

"""
run command
chainlit run 07_chainlit/01_chatbot.py -w
uv run --only-group chainlit chainlit run 07_chainlit/01_chatbot.py
"""