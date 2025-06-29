import json
import requests
from conifg import OLLAMA_HOST, OLLAMA_PORT


url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags"

response = requests.get(url)
data = response.json() 
print(json.dumps(data, indent=4))