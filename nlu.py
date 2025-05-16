from llm import get_ollama_response
import re

POSSIBLE_INTENTS = [
    "get_weather", "search_web", "get_bible_verse", 
    "nextcloud_list_files", "nextcloud_query", 
    "autosci_mode", "casual_chat"
]

def process_user_intent(user_message: str) -> dict:
    """
    Processes the user's message to determine intent and extract entities.
    Step 1: Use LLM to determine intent.
    Step 2: If intent requires entities, use rule-based extraction from user_message.
    """
    # Step 1: Determine intent using LLM
    intent_prompt = f'''
User message: "{user_message}"
Based on this message, what is the user\'s primary intent?
Choose ONE from this list: {', '.join(POSSIBLE_INTENTS)}.
Respond with ONLY the chosen intent name. For example:
- If the user wants weather, respond with "get_weather".
- If the user asks to list or show files on Nextcloud (optionally mentioning a path), respond with "nextcloud_list_files".
- For other Nextcloud related queries that are not listing files, respond with "nextcloud_query".
- If the user explicitly asks for 'autosci mode' or 'make a scientific discovery', respond with "autosci_mode".
'''
    
    raw_intent_response = get_ollama_response(intent_prompt).strip().lower()
    
    identified_intent = "casual_chat"  # Default intent
    # Try to find the most direct match for the intent from the LLM's response
    for pi in POSSIBLE_INTENTS:
        if pi == raw_intent_response: # Exact match
            identified_intent = pi
            break
    if identified_intent == "casual_chat": # If no exact match, check if intent is in a more verbose response
        for pi in POSSIBLE_INTENTS:
            if pi in raw_intent_response.split(): # e.g. LLM says "intent is get_weather"
                identified_intent = pi
                break
            
    entities = {}

    # Step 2: Rule-based entity extraction based on identified intent
    if identified_intent == "get_weather":
        match = re.search(r"(?:in|for|at|near|of)\s+([A-Za-z0-9\s\-]+)(?:\?|$|today|tomorrow)", user_message, re.IGNORECASE)
        if match and match.group(1):
            entities['location'] = match.group(1).strip()
        else:
            # A simple fallback: check for capitalized words if no prepositional phrase found
            # This is very naive and might pick up other capitalized words.
            potential_locations = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", user_message)
            if potential_locations:
                 # Check if any of these are not common words (this part is tricky and omitted for simplicity)
                 # For now, just take the last one as a heuristic, could be improved
                 entities['location'] = potential_locations[-1] 
            else:
                entities['location'] = None
            
    elif identified_intent == "search_web":
        match = re.search(r"(?:search for|look up|find|what is|who is|tell me about)\s+(.+)(?:\?|$)", user_message, re.IGNORECASE)
        if match and match.group(1):
            entities['query_term'] = match.group(1).strip()
        else:
            # Fallback: if intent is search, but no clear query, take message after known trigger words, or whole message
            temp_query = user_message
            triggers = ["search for", "look up", "find", "what is", "who is", "tell me about", "search", "google"]
            for trigger in triggers:
                if user_message.lower().startswith(trigger + " "):
                    temp_query = user_message[len(trigger)+1:].strip()
                    break
            entities['query_term'] = temp_query if temp_query != user_message or not entities.get('query_term') else user_message
            if not entities['query_term']:
                 entities['query_term'] = user_message # ultimate fallback

    elif identified_intent == "nextcloud_query":
        match = re.search(r"(?:nextcloud|on nextcloud)\s*(?:can you|please|could you|to)?\s*(.+)", user_message, re.IGNORECASE)
        if match and match.group(1):
            entities['task_details'] = match.group(1).strip()
        else:
            parts = re.split(r"nextcloud", user_message, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) > 1 and parts[1].strip():
                entities['task_details'] = parts[1].strip().lstrip('to').strip()
            else:
                entities['task_details'] = None

    elif identified_intent == "nextcloud_list_files":
        # Try to extract a path. Examples:
        # "list files in /documents/work"
        # "show me my photos folder on nextcloud"
        # "what's in /my_folder on nextcloud?"
        path_match = re.search(r"(?:in|on|at|from|of|folder|directory|path)\s+([A-Za-z0-9\/_\-\.\s]+)", user_message, re.IGNORECASE)
        # More specific: looking for paths that start with / or a typical folder name structure
        explicit_path_match = re.search(r"\s(\/[A-Za-z0-9\/_\-\.\s]+|[A-Za-z0-9\._\-]+(?:\/[A-Za-z0-9\._\-]+)*)", user_message, re.IGNORECASE)

        extracted_path = '/' # Default to root
        if explicit_path_match and explicit_path_match.group(1):
            # Prioritize explicit paths like /documents or my_folder/notes
            extracted_path = explicit_path_match.group(1).strip()
        elif path_match and path_match.group(1):
            # Broader match for phrases like "in my documents folder"
            # This might need further cleaning or validation if it captures too much.
            potential_path = path_match.group(1).strip()
            # Avoid capturing generic terms if they were part of the trigger phrase and not a real path
            if potential_path.lower() not in ["nextcloud", "cloud", "server"]:
                 extracted_path = potential_path
        
        # Ensure path starts with / if it doesn't look like an absolute path already and is not just /.
        if not extracted_path.startswith('/') and extracted_path != '/':
            extracted_path = '/' + extracted_path
        
        # Simple cleaning: remove trailing common words that might be caught by regex if they are not part of path
        for word in [" folder", " directory", " path", " on nextcloud", " from nextcloud"]:
            if extracted_path.lower().endswith(word):
                extracted_path = extracted_path[:len(extracted_path)-len(word)]

        entities['path'] = extracted_path.strip() if extracted_path else '/'

    elif identified_intent == "autosci_mode":
        # No specific entities needed for this mode, it uses a hardcoded prompt.
        pass

    return {"intent": identified_intent, "entities": entities} 