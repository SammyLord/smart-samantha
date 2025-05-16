import requests
import json

OLLAMA_API_URL = "https://ollama-api.nodemixaholic.com/v1"
# Primary model for general tasks, idea generation
GENERATOR_MODEL_NAME = "sparksammy/tinysam-l3.2-v2" 
# Advanced model for critical thinking, evaluation, and complex tasks
THINKER_MODEL_NAME = "sparksammy/samantha-thinker-v2" 

def get_ollama_response(prompt: str, model_name: str = GENERATOR_MODEL_NAME) -> str:
    """Gets a response from the Ollama API, allowing model selection."""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/chat/completions",
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False, 
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama (model: {model_name}): {e}")
        return f"Sorry, I'm having trouble connecting to my brain ({model_name}) right now."
    except (KeyError, IndexError) as e:
        print(f"Error parsing Ollama response (model: {model_name}): {e}")
        return f"Sorry, I received an unexpected response from my brain ({model_name})." 