import json
import requests
from config import OLLAMA_HOST, OLLAMA_PORT

url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

MODEL_NAME = "llama3.2:3b"

prompt = "how are you? my sweet?"
params = {
    "model": MODEL_NAME,
    "prompt": prompt,
    "stream": False,
}

response = requests.post(url, json=params).json()
print(json.dumps(response, indent=4))