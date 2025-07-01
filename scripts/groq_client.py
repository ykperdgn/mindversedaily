import os
from dotenv import load_dotenv
load_dotenv()
import requests

def generate_content(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",  # Güncel ve desteklenen model
        "messages": [
            {"role": "system", "content": "You are a professional content writer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        print("HTTP Error while processing the prompt:\n")
        print(prompt[:500])  # show first 500 characters of the prompt for debugging
        raise e
