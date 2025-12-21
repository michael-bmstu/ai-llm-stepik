import time
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_mistralai import ChatMistralAI
from langchain.chat_models import init_chat_model
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

import os
from dotenv import load_dotenv
load_dotenv()

ORDERS_STATUSES_DATA = {
    "a42": "Доставляется",
    "b61": "Выполнен",
    "k37": "Отменен",
}


@tool
def get_order_status(order_id: str) -> str:
    """Get status of order by order identifier"""
    time.sleep(2)
    return ORDERS_STATUSES_DATA.get(order_id, f"Не существует заказа с order_id={order_id}")

@tool
def cancel_order(order_id: str) -> str:
    """Cancel the order by order identifier"""
    time.sleep(2)
    if order_id not in ORDERS_STATUSES_DATA:
        return f"Такой заказ не существует"
    if ORDERS_STATUSES_DATA[order_id] != "Отменен":
        ORDERS_STATUSES_DATA[order_id] = "Отменен"
        return "Заказ успешно отменен"
    return "Заказ уже отменен"

tools = [get_order_status, cancel_order]
llm = init_chat_model(
    model="mistral-large-latest",
    api_key=os.getenv('MISTRAL_KEY')
)

prompt = ChatPromptTemplate(
    [
        ("system", (
            "Твоя задача отвечать на вопросы клиентов об их заказах, используя вызов инструментов."
            "Отвечай пользователю подробно и вежливо."
        )),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        # MessagesPlaceholder("agent_scratchpad"),
    ]
)

# agent = create_tool_calling_agent(llm, tools, prompt)
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

agent = create_agent(llm, tools)
agent_executor = prompt | agent

memory = InMemoryChatMessageHistory()
agent_with_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

config = {"configurable": {"session_id": "blank"}}
while True:
    print()
    user_question = input('You: ')
    answer = agent_with_history.invoke({"input": user_question}, config)
    print("Bot: ", answer['messages'][-1].content)