import requests
import random # Keep for fallback or if API fails
import urllib.parse

BIBLE_API_URL = "https://bible-api.com/"

def get_random_bible_verse() -> str:
    """Fetches a random Bible verse using a predefined list for randomness, then fetching that specific verse."""
    # For true randomness with an API that fetches specific verses, we need a list to pick from.
    # This list can be expanded.
    common_verses = [
        "John 3:16", "Romans 8:28", "Philippians 4:13", "Proverbs 3:5-6", "Jeremiah 29:11",
        "Isaiah 41:10", "Psalm 23:1", "1 Corinthians 10:13", "Galatians 5:22-23", "Ephesians 2:8-9"
    ]
    verse_reference = random.choice(common_verses)
    return get_specific_bible_verse(verse_reference)

def get_specific_bible_verse(verse_reference: str) -> str:
    """Fetches a specific Bible verse using bible-api.com."""
    if not verse_reference:
        return "Please provide a Bible verse reference (e.g., John 3:16)."
    
    try:
        # Sanitize and encode the reference
        encoded_reference = urllib.parse.quote(verse_reference.strip())
        url = f"{BIBLE_API_URL}{encoded_reference}?translation=kjv" # Default to KJV, can be parameterized
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        reference = data.get("reference", verse_reference)
        text = data.get("text", "")
        translation = data.get("translation_name", "Selected Translation")

        if not text:
            return f"Sorry, I couldn't find the text for '{verse_reference}'. Please check the reference."

        return f"{reference} ({translation}):\n{text.strip()}"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Bible verse '{verse_reference}': {e}")
        # Fallback to old placeholder if API fails for some reason
        return _get_placeholder_verse(f"(Could not connect to Bible API for {verse_reference})")
    except (KeyError, IndexError, ValueError) as e: # ValueError for json.JSONDecodeError in older requests
        print(f"Error parsing Bible verse data for '{verse_reference}': {e}")
        return f"Sorry, there was an issue processing the Bible verse '{verse_reference}'."

def _get_placeholder_verse(prefix_message="") -> str:
    """Fallback placeholder verse."""
    placeholder_verses = [
        "For God so loved the world... (John 3:16)",
        "The Lord is my shepherd... (Psalm 23:1)",
        "I can do all things through Christ... (Philippians 4:13)"
    ]
    return f"{prefix_message} {random.choice(placeholder_verses)} (Placeholder)"

# We might also want to adjust nlu.py if the user can ask for specific verses.
# For now, get_random_bible_verse is the primary entry point from app.py.
# If NLU can extract a verse_reference entity, app.py could call get_specific_bible_verse.