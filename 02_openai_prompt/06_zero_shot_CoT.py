from openai import OpenAI
from config import mistral_params

client = OpenAI(
    api_key=mistral_params["api_key"],
    base_url=mistral_params["base_url"]
)

MODEL_NAME = "mistral-small-latest"

message = """\
Solve the task. Think step by step and give answer in format "Answer is True or False"
Task: Check if the odd numbers in this group add up to an even number: 17,  10, 19, 4, 8, 12, 24\
"""
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": message,
        },
    ],
    model=MODEL_NAME,
    temperature=0.1
)
print(chat_completion.choices[0].message.content)