import json
import re
from llm import get_ollama_response, THINKER_MODEL_NAME

# A dictionary defining the intents and the entities they might have.
INTENT_DEFINITIONS = {
    "get_weather": {
        "description": "User wants to know the current weather.",
        "entities": {
            "location": {
                "type": "string",
                "description": "The city or area to get the weather for, e.g., 'San Francisco'."
            }
        },
        "examples": [
            "What's the weather like in London today?",
            "tell me the weather for Paris"
        ]
    },
    "search_web": {
        "description": "User wants to search the web for information.",
        "entities": {
            "query_term": {
                "type": "string",
                "description": "The topic or question to search for, e.g., 'latest news on AI'."
            }
        },
        "examples": [
            "Search for the best Italian restaurants near me",
            "Who is the CEO of OpenAI?"
        ]
    },
    "get_bible_verse": {
        "description": "User wants to get a random Bible verse.",
        "entities": {},
        "examples": [
            "Read me a bible verse",
            "Give me a random verse from the Bible"
        ]
    },
    "nextcloud_list_files": {
        "description": "User wants to list files or folders from their Nextcloud account.",
        "entities": {
            "path": {
                "type": "string",
                "description": "The directory path to list. Defaults to '/' if not specified. E.g., '/Documents/Work'."
            }
        },
        "examples": [
            "What files are in my Nextcloud?",
            "Show me the contents of the /Photos/2024 folder on my cloud."
        ]
    },
    "nextcloud_read_file": {
        "description": "User wants to read the content of a specific file from their Nextcloud account.",
        "entities": {
            "path": {
                "type": "string",
                "description": "The full path to the file to be read, e.g., '/Documents/report.txt'."
            }
        },
        "examples": [
            "Read the file /notes.txt from my Nextcloud.",
            "Can you show me what's in 'Documents/Project Plan.md' on my cloud?"
        ]
    },
    "nextcloud_query": {
        "description": "User has a general query or request for Nextcloud that isn't listing files.",
        "entities": {
            "task_details": {
                "type": "string",
                "description": "The specific task the user wants to perform on Nextcloud."
            }
        },
        "examples": [
            "Can you organize my files on Nextcloud?",
            "On my cloud, find the presentation from last week."
        ]
    },
    "get_calendar_events": {
        "description": "User wants to know about their schedule, appointments, or events from their calendar.",
        "entities": {
             "date_range": {
                "type": "string",
                "description": "The specific date or range, e.g., 'today', 'tomorrow', 'this week'. (Optional)"
            }
        },
        "examples": [
            "What's on my agenda for today?",
            "Do I have any meetings tomorrow?"
        ]
    },
    "query_youtube_video": {
        "description": "User is asking a question about a specific YouTube video, identified by a URL.",
        "entities": {
            "video_id": {
                "type": "string",
                "description": "The 11-character ID of the YouTube video extracted from the URL."
            },
            "question": {
                "type": "string",
                "description": "The specific question the user has about the video. Defaults to 'Summarize the video' if not explicit."
            }
        },
        "examples": [
            "What is the main argument in this video? https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "Summarize this for me: https://youtu.be/o-YBDTqX_ZU"
        ]
    },
     "autosci_mode": {
        "description": "User explicitly wants to activate the 'AutoSCI' scientific discovery mode.",
        "entities": {},
        "examples": [
            "activate autosci mode",
            "Let's make a scientific discovery"
        ]
    },
    "casual_chat": {
        "description": "User is making small talk or asking a question that doesn't fit other intents.",
        "entities": {},
        "examples": [
            "Hello, how are you?",
            "What's your name?"
        ]
    }
}

def get_intent_and_entities(user_message: str, mcp_tools=None) -> tuple[str, dict]:
    """
    Processes the user's message to determine intent and extract entities using an LLM,
    including dynamically provided MCP tools.
    """
    if mcp_tools is None:
        mcp_tools = []

    # Dynamically create the intent list and formatting for the prompt
    intent_list = "\n".join([f"- {name}: {details['description']}" for name, details in INTENT_DEFINITIONS.items()])
    
    if mcp_tools:
        mcp_tool_list = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in mcp_tools])
        intent_list += "\n" + mcp_tool_list

    json_format_description = """
Respond with a single JSON object in the following format:
{
  "intent": "INTENT_NAME",
  "entities": {
    "entity_name_1": "value_1",
    "entity_name_2": "value_2"
  },
  "confidence": 0.9,
  "reasoning": "A brief explanation of why you chose this intent and entities."
}

- "intent" must be ONE of the intent names listed above.
- "entities" must be an object containing the extracted entities for that intent. If no entities are found for a given intent, provide an empty object {}.
- For `query_youtube_video`, extract the `video_id` from the URL. The user's question is the part of the message that is not the URL.
- For `nextcloud_list_files`, if no path is mentioned, the `path` entity should default to "/".
"""

    prompt = f"""
You are a highly intelligent Natural Language Understanding (NLU) engine. Your task is to analyze the user's message and determine their intent and any associated entities.

Here are the possible intents:
{intent_list}

{json_format_description}

---
User message: "{user_message}"
---

Now, provide the JSON output based on the user's message.
"""
    
    # LLM call
    raw_response = get_ollama_response(prompt, model_name=THINKER_MODEL_NAME)
    
    # Regex to find JSON object in the response, in case the LLM adds extra text.
    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    
    if not json_match:
        print(f"NLU Error: LLM did not return a valid JSON object. Response: {raw_response}")
        return "casual_chat", {}

    try:
        parsed_json = json.loads(json_match.group(0))
        
        # Validate the structure
        intent = parsed_json.get("intent", "casual_chat")
        entities = parsed_json.get("entities", {})
        
        # Check if the returned intent is valid (either in predefined or MCP tools)
        mcp_tool_names = [tool['name'] for tool in mcp_tools]
        if intent not in INTENT_DEFINITIONS and intent not in mcp_tool_names:
            print(f"NLU Warning: LLM returned an unknown intent '{intent}'. Defaulting to casual_chat.")
            return "casual_chat", {}
            
        return intent, entities

    except json.JSONDecodeError:
        print(f"NLU Error: Failed to parse JSON from LLM response: {raw_response}")
        return "casual_chat", {}

def generate_nlu_prompt(user_message: str) -> str:
    """Generates the full prompt for the LLM to perform NLU."""
    
    # Dynamically create the intent list and formatting for the prompt
    intent_list = "\n".join([f"- {name}: {details['description']}" for name, details in INTENT_DEFINITIONS.items()])
    
    json_format_description = """
Respond with a single JSON object in the following format:
{
  "intent": "INTENT_NAME",
  "entities": {
    "entity_name_1": "value_1",
    "entity_name_2": "value_2"
  },
  "confidence": 0.9,
  "reasoning": "A brief explanation of why you chose this intent and entities."
}

- "intent" must be ONE of the intent names listed above.
- "entities" must be an object containing the extracted entities for that intent. If no entities are found for a given intent, provide an empty object {}.
- For `query_youtube_video`, extract the `video_id` from the URL. The user's question is the part of the message that is not the URL.
- For `nextcloud_list_files`, if no path is mentioned, the `path` entity should default to "/".
"""

    prompt = f"""
You are a highly intelligent Natural Language Understanding (NLU) engine. Your task is to analyze the user's message and determine their intent and any associated entities.

Here are the possible intents:
{intent_list}

{json_format_description}

---
User message: "{user_message}"
---

Now, provide the JSON output based on the user's message.
"""
    return prompt 