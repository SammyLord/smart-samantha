import requests
import urllib.parse
import json
import re

DUCKDUCKGO_API_URL = "https://api.duckduckgo.com/"

def search_web(query: str) -> str:
    """Action for performing a web search."""
    if not query:
        return "What would you like me to search for on the web?"

    try:
        params = {
            "q": query,
            "format": "json",
            "no_html": 1, # Removes HTML from results
            "skip_disambig": 1 # Skip disambiguation pages, go to best result if possible
        }
        response = requests.get(DUCKDUCKGO_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # DuckDuckGo's API has various types of answers.
        # We'll try to get a concise answer or abstract.
        result_type = data.get("Type", "") # A (Article), D (Disambiguation), C (Category), N (Name), E (Exclusive), '' (nothing)
        abstract = data.get("AbstractText", "")
        answer = data.get("Answer", "")
        answer_type = data.get("AnswerType", "") # e.g., calc, definition, etc.
        definition = data.get("Definition", "")
        entity = data.get("Entity", "")
        heading = data.get("Heading", "")

        if answer and answer_type:
            return f"DuckDuckGo says ({answer_type}): {answer}"
        elif abstract:
            return f"{heading}: {abstract}"
        elif definition:
            source_name = data.get("DefinitionSource", "Definition")
            return f"{source_name} for '{heading if heading else entity if entity else query}': {definition}"
        elif heading and result_type == 'A': # Article heading without good abstract
            related_topics = data.get("RelatedTopics", [])
            first_related_text = ""
            if related_topics and isinstance(related_topics, list) and len(related_topics) > 0 and related_topics[0].get("Text"):
                first_related_text = " First related topic: " + related_topics[0].get("Text")
            if data.get("AbstractURL"): 
                 return f"Found an article titled '{heading}'. You can read more at {data.get("AbstractURL")} {first_related_text}"
            return f"Found an article titled '{heading}'. {first_related_text}"
        elif result_type == 'D':
            related_topics = data.get("RelatedTopics", [])
            options = []
            for topic in related_topics:
                if topic.get("Result"): # Check if it has a Result field, typical for disambiguation
                    match = re.search(r'<a href="(.*?)">(.*?)<\/a>', topic.get("Result"))
                    if match:
                         options.append(f'{match.group(2)} (More info: {match.group(1)})')
            if options:
                return f"'{query}' could refer to multiple things: \n - " + "\n - ".join(options)
            else:
                return f"I found a disambiguation page for '{query}', but couldn't extract options. Try being more specific or check {data.get('AbstractURL', 'DuckDuckGo')}."
        elif not abstract and not answer and not definition and data.get("Redirect"): # For !bang redirects
            if data["Redirect"].startswith("/"):
                return f"For more on that, try searching directly on DuckDuckGo: https://duckduckgo.com{data['Redirect']}"
            return f"For more on that, try: {data['Redirect']}"
        else:
            fallback_url = f"https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}"
            return f"I didn't find a direct answer for '{query}'. You can try searching on DuckDuckGo: {fallback_url}"
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching search data for '{query}': {e}")
        return f"Sorry, I'm having trouble searching the web for '{query}' right now."
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing search data for '{query}': {e}")
        return f"Sorry, there was an issue processing the search results for '{query}'." 