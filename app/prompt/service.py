import os
import requests

url = os.getenv("API_URL")
headers = {
    "authorization": f"OAuth {os.getenv("SOY_TOKEN")}",
    "content-type": "application/json",
}

class PromptClass:
    @staticmethod
    def send_prompt(prompt: str) -> str:
        payload = {
            "model": "gpt-4.1-nano",
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post(url, json=payload, headers=headers)

        data = response.json()
        return data["response"]["choices"][0]["message"]["content"]
