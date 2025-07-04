from openai import OpenAI
from config import open_router_params

client = OpenAI(
    api_key=open_router_params["api_key"],
    base_url=open_router_params["base_url"],
)
MODEL_NAME = "deepseek/deepseek-r1-0528-qwen3-8b:free"
message = "Привет! Расскажи о сервисе open router"

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Ты опытный LLM-инженер, который знает толк в AI приложениях!",
        },
        {
            "role": "user",
            "content": message,
        }
    ],
    model=MODEL_NAME,
    temperature=0.7
)

print(chat_completion.choices[0].message.content)