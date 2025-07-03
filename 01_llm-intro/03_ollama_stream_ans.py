import json
from json import JSONDecodeError
import requests
from config import OLLAMA_HOST, OLLAMA_PORT

url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

MODEL_NAME = "llama3.2:3b"

print("Start the dialog!\nEnd dialog: type \"/exit\" or Ctrl+C")
prompt = input("You: ")
while prompt != "/exit":
    params = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
    }
    with requests.post(url, json=params, stream=True) as response:
        response.raise_for_status()
        print(f"{MODEL_NAME}: ", end="")
        for chunk in response.iter_lines():
            try:
                chunk = json.loads(chunk)
                print(chunk["response"], end="", flush=True)
            except JSONDecodeError as ex:
                pass
        print()
    prompt = input("You: ")