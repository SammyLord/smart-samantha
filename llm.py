import requests
import json
import os
from dotenv import load_dotenv

if not load_dotenv():
    print("Error loading .env file. Ensure it contains OLLAMA_API_URL, POW, PRIVATE_KEY, GEN_MODEL, and THINK_MODEL.")
    exit(1)

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
# Primary model for general tasks, idea generation
GENERATOR_MODEL_NAME = os.getenv("GEN_MODEL")
# Advanced model for critical thinking, evaluation, and complex tasks
THINKER_MODEL_NAME = os.getenv("THINK_MODEL")

def get_ollama_response(prompt: str, model_name: str = GENERATOR_MODEL_NAME, history: list = None) -> str:
    """
    Gets a response from the Ollama API, allowing model selection and conversation history.
    """
    if history:
        messages = history + [{"role": "user", "content": prompt}]
    else:
        messages = [{"role": "user", "content": prompt}]

    response = None # Initialize response to None to handle cases where the request itself fails early
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/chat/completions",
            json={
                "model": model_name,
                "messages": messages,
                "stream": False, 
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json() # This is where JSONDecodeError can occur
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.JSONDecodeError as e: # Specific catch for JSON decoding errors
        print(f"JSONDecodeError: Failed to decode Ollama response (model: {model_name}). Error: {e}")
        if response is not None:
            print(f"Ollama raw response text: {response.text}")
        return f"Sorry, I received a malformed response from my brain ({model_name}). Check logs for details."
    except requests.exceptions.RequestException as e: # For other network/HTTP errors (e.g., connection, timeout, non-200 status if raise_for_status hits)
        print(f"RequestException: Error communicating with Ollama (model: {model_name}): {e}")
        if response is not None: # If response exists, it might have useful info despite the exception
            print(f"Ollama response status code: {response.status_code}")
            print(f"Ollama response text (on RequestException): {response.text}")
        return f"Sorry, I'm having trouble connecting to my brain ({model_name}) right now."
    except (KeyError, IndexError) as e: # For issues with expected response structure AFTER successful JSON parsing
        print(f"DataStructureError: Error parsing Ollama response structure (model: {model_name}): {e}")
        # It might also be useful to print response.text here if parsing the structure fails
        if response is not None and hasattr(response, 'text'):
             print(f"Ollama raw response text (for structure error): {response.text}")
        return f"Sorry, I received an unexpected response structure from my brain ({model_name})." 