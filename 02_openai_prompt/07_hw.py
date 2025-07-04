from openai import OpenAI
from config import mistral_params

client = OpenAI(
    api_key=mistral_params["api_key"],
    base_url=mistral_params["base_url"]
)
MODEL_NAME = "mistral-small-latest"


# User: 5.52 больше 5.152
# Assistant: Нет, 5.52 не больше 5.152. Число 5.52 равно 5152/915, что меньше, чем число 5.152.
system_prompt = """\
Проверь утверждение о сравнении чисел.
Пример:
1) 3 больше 4
ответ: нет, 3 меньше 4
2) 3.56 меньне 4.1
ответ: да, 3.56 меньше 4.1
"""
# user_message = "5.52 больше 5.152"
user_message = input("Введите утверждение о числах: ")
chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    model=MODEL_NAME
)
print(chat_completion.choices[0].message.content)