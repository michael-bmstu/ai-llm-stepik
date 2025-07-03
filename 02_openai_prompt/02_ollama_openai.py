from openai import OpenAI
from config import ollama_params

client = OpenAI(
    api_key=ollama_params["api_key"],
    base_url=ollama_params["base_url"]
)
MODEL_NAME = "llama3.2:3b"

message = "Привет! Когда ждать появления Dota 3?"

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": message,
        }
    ],
    model=MODEL_NAME,
    temperature=0.1
)

print(chat_completion.choices[0].message.content)