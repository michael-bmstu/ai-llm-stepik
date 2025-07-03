from openai import OpenAI
from config import mistral_params

client = OpenAI(
    api_key=mistral_params["api_key"],
    base_url=mistral_params["base_url"]
)
MODEL_NAME = "mistral-small-latest"

system_prompt = """\
Classify the text into neutral, negative or positive
Examples:
1) Text: Wow that movie was rad!
AI: positive
2) Text: He is so bad!
AI: negative

Text: 
"""

user_message = "I think the vacation is okay."

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_message
        }
    ],
    model=MODEL_NAME,
    temperature=0.1
)
print(chat_completion.choices[0].message.content)