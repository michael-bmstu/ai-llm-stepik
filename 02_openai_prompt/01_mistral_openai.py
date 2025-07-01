from openai import OpenAI
from config import mistral_params

client = OpenAI(
    api_key=mistral_params['api'], 
    base_url=mistral_params['url']
    )
MODEL_NAME = "mistral-small-latest"

message = "Привет! Сколько тебе лет?"

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Ты профессор, которому 60 лет",
        },
        {
            "role": "user",
            "content": message,
        }
    ],
    model=MODEL_NAME,
    temperature=0.1
)

print(chat_completion.choices[0].message.content)