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
    },
    "autosci_discover": []
}

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

def process_user_intent(user_message: str) -> dict:
    """
    Processes the user's message to determine intent and extract entities using an LLM.
    The LLM is prompted to return a JSON object with the intent and entities.
    """
    prompt = generate_nlu_prompt(user_message)
    
    # LLM call
    raw_response = get_ollama_response(prompt)
    
    # Regex to find JSON object in the response, in case the LLM adds extra text.
    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    
    if not json_match:
        print(f"NLU Error: LLM did not return a valid JSON object. Response: {raw_response}")
        return {"intent": "casual_chat", "entities": {}}

    try:
        parsed_json = json.loads(json_match.group(0))
        
        # Validate the structure
        intent = parsed_json.get("intent")
        entities = parsed_json.get("entities", {})
        
        if intent not in INTENT_DEFINITIONS:
            print(f"NLU Warning: LLM returned an unknown intent '{intent}'. Defaulting to casual_chat.")
            return {"intent": "casual_chat", "entities": {}}
            
        # --- Post-processing for specific, structured entities ---
        # We will handle specific extraction for youtube directly in the app route
        # to ensure it's robust, so no special handling is needed here.

        print(f"NLU Result: Intent='{intent}', Entities={entities}")
        return {"intent": intent, "entities": entities}

    except json.JSONDecodeError as e:
        print(f"NLU Error: Failed to decode JSON from LLM response. Error: {e}. Response: {json_match.group(0)}")
        return {"intent": "casual_chat", "entities": {}}
    except Exception as e:
        print(f"NLU Error: An unexpected error occurred during NLU processing. Error: {e}")
        return {"intent": "casual_chat", "entities": {}}

def get_intent_and_entities(user_input, mcp_tools=None):
    """
    Identifies the user's intent and extracts relevant entities from the input.
    This version is simplified to rely more on the LLM's direct JSON output.
    """
    if mcp_tools is None:
        mcp_tools = []
        
    # Build the tool definitions for the prompt
    tool_definitions = ""
    for intent, entities in INTENT_DEFINITIONS.items():
        entity_list = ", ".join(entities)
        tool_definitions += f'- "{intent}": {entity_list if entity_list else "No entities"}\n'

    if mcp_tools:
        tool_definitions += "\n# Additional MCP tools:\n"
        for tool in mcp_tools:
            # For now, we assume MCP tools might need arguments but don't have a defined schema here.
            # A more advanced version could parse the tool's inputSchema.
            tool_definitions += f'- "{tool["name"]}": {tool["description"]}\n'

    prompt = f"""
From the user input "{user_input}", identify the primary intent and extract any relevant entities.

Here are the available tools and the entities they expect:
{tool_definitions}

Respond with a single, valid JSON object with two keys: "intent" and "entities".
- The "intent" must be a string that exactly matches one of the available tool names. If it's an MCP tool, prefix the name with "mcp_".
- The "entities" must be a JSON object containing the extracted values.

If the user input is just casual conversation (e.g., "hello", "how are you?"), respond with:
{{"intent": "casual_chat", "entities": {{}}}}

User: "what's the weather like in New York?"
{{"intent": "get_weather", "entities": {{"location": "New York"}}}}

User: "list my files in the documents folder on nextcloud"
{{"intent": "nextcloud_list_files", "entities": {{"path": "/documents"}}}}

User: "run the database migration"
{{"intent": "mcp_migrate_db", "entities": {{}}}}

User: "{user_input}"
Result:
"""

    llm_response = get_ollama_response(THINKER_MODEL_NAME, prompt)

    # Basic cleanup of the response
    llm_response = llm_response.strip()

    # Find the JSON object in the response
    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
    
    if not json_match:
        print(f"NLU Error: No JSON object found in LLM response: {llm_response}")
        return "casual_chat", {}

    try:
        parsed_json = json.loads(json_match.group(0))
        intent = parsed_json.get("intent", "casual_chat")
        entities = parsed_json.get("entities", {})
        
        # If the intent is an MCP tool, we don't need to validate it against INTENT_DEFINITIONS
        is_mcp_intent = any(tool['name'] == intent.replace('mcp_', '', 1) for tool in mcp_tools)

        if not is_mcp_intent and intent not in INTENT_DEFINITIONS:
             print(f"NLU Warning: LLM returned an unknown intent '{intent}'. Defaulting to casual_chat.")
             return "casual_chat", {}

        print(f"NLU Result: Intent='{intent}', Entities={entities}")
        return intent, entities

    except json.JSONDecodeError as e:
        print(f"NLU Error: Failed to decode JSON from LLM response. Error: {e}. Response: {json_match.group(0)}")
        return "casual_chat", {}
    except Exception as e:
        print(f"NLU Error: An unexpected error occurred during NLU processing. Error: {e}")
        return "casual_chat", {} 