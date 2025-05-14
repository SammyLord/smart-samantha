from flask import Flask, render_template, request, jsonify
from llm import get_ollama_response
from nlu import process_user_intent
from integrations import weather, web_search, bible, nextcloud # Import integration modules

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Process user message for intent and entities
    nlu_result = process_user_intent(user_message)
    intent = nlu_result.get('intent')
    entities = nlu_result.get('entities', {})
    
    # Extract Nextcloud credentials if sent by the client
    nextcloud_creds = request.json.get('nextcloud_creds')
    
    ai_response = ""

    if intent == "get_weather":
        ai_response = weather.get_weather_data(location=entities.get('location'))
    elif intent == "search_web":
        ai_response = web_search.search_web(query=entities.get('query_term'))
    elif intent == "get_bible_verse":
        ai_response = bible.get_random_bible_verse()
    elif intent == "nextcloud_list_files" or intent == "nextcloud_query":
        if not nextcloud_creds or not all(k in nextcloud_creds for k in ['url', 'user', 'password']):
            ai_response = "It looks like you want to interact with Nextcloud, but your credentials aren't set or are incomplete. Please configure them in the settings (⚙️ icon)."
        else:
            ai_response = nextcloud.handle_nextcloud_action(creds=nextcloud_creds, nlu_data=nlu_result)
    elif intent == "casual_chat":
        # For casual chat, directly use the LLM for a general response
        ai_response = get_ollama_response(user_message) # Or a slightly modified prompt for chat
    else:
        # Fallback if intent isn't recognized by NLU (should ideally be casual_chat)
        ai_response = get_ollama_response(f"The user said: {user_message}. Try to respond helpfully.")

    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True) 