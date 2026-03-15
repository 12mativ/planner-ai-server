import os
import requests

url = os.getenv("API_URL")

payload = {
    "model": "gpt-4.1-nano",
    "messages": [
        {
            "role": "user",
            "content": "Hello!"
        }
    ]
}

headers = {
    "authorization": f"OAuth {os.getenv("SOY_TOKEN")}",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()
print(data["response"]["choices"][0]["message"]["content"])
