import requests
import json

OLLAMA_API_URL = "https://ollama-api.nodemixaholic.com/v1"
MODEL_NAME = "sparksammy/tinysam-l3.2-v2"

def get_ollama_response(prompt: str) -> str:
    """Gets a response from the Ollama API."""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/chat/completions",
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False, # Keep it simple for now
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return "Sorry, I'm having trouble connecting to my brain right now."
    except (KeyError, IndexError) as e:
        print(f"Error parsing Ollama response: {e}")
        return "Sorry, I received an unexpected response from my brain." 