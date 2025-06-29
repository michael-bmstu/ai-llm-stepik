import json
from json import JSONDecodeError
import requests
from config import OLLAMA_HOST, OLLAMA_PORT

MODEL_NAME = "llama3.2:3b"
MODE = 'chat'

url_api = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/"

chat_hist = []
system_prompt = "You are ai tech expert, your task is to provide reference information on my questions"
chat_hist.append({"role": "system", "content": system_prompt})

# start chating
print("Start the dialog!")
while True:
    print("*** to end the dialog: type \"stop\" or press Ctrl+C ***")
    print("- your message:")
    message = input()
    if message.lower() == "stop":
        break
    chat_hist.append({"role": "user", "content": message})

    payload = {
        "model": MODEL_NAME,
        "messages": chat_hist,
        "stream": True,
    }
    try:
        with requests.post(url=url_api + MODE, json=payload, stream=True) as response:
            response.raise_for_status()
            answer = ""
            print()
            print(f"- {MODEL_NAME} answer:")
            for line in response.iter_lines():
                try:
                    line = json.loads(line)
                    answer += line["message"]["content"]
                    print(line["message"]["content"], end='', flush=True)
                except JSONDecodeError as e:
                    pass
            print()
            print()
    except Exception as e:
        print("Request filed:", e)
    
    chat_hist.append({"role": "assistant", "content": answer})

print("The dialog was ended, bye!")