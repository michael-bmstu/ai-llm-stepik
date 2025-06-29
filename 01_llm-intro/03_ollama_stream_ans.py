import json
from json import JSONDecodeError
import requests
from conifg import OLLAMA_HOST, OLLAMA_PORT

url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

MODEL_NAME = "llama3.2:3b"

print('Start the dialog!\nEnd dialog: type \'/stop\' or Ctrl+C')
prompt = input('You: ')
while prompt != '/exit':
    params = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
    }
    with requests.post(url, json=params, stream=True) as response:
        response.raise_for_status()
        print(f'{MODEL_NAME}: ', end='')
        for chunk in response.iter_content(chunk_size=256):
            try:
                chunk = json.loads(chunk)
                print(chunk['response'], end='')
            except JSONDecodeError as ex:
                pass
        print()
    prompt = input('You: ')