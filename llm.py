import requests
import json

OLLAMA_API_URL = "https://ollama-api.nodemixaholic.com/v1"
# Primary model for general tasks, idea generation
GENERATOR_MODEL_NAME = "sparksammy/tinysam-l3.2-v2" 
# Advanced model for critical thinking, evaluation, and complex tasks
THINKER_MODEL_NAME = "sparksammy/samantha-thinker-v2" 

def get_ollama_response(prompt: str, model_name: str = GENERATOR_MODEL_NAME) -> str:
    """Gets a response from the Ollama API, allowing model selection."""
    response = None # Initialize response to None to handle cases where the request itself fails early
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