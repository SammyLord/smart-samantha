from flask import Flask, render_template, request, jsonify
from llm import get_ollama_response
from nlu import process_user_intent
from integrations import weather, web_search, bible, nextcloud # Import integration modules
from integrations.autosci import trigger_autosci_discovery # Import the new autosci function
from problem_solver import solve_with_multi_step_refinement # Updated import

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
        print(f"App.py: Casual chat intent. Engaging multi-step solver for: {user_message}")
        ai_response = solve_with_multi_step_refinement(user_message)
    elif intent == "get_ollama_response": # This intent might be redundant
        print(f"App.py: get_ollama_response intent. Engaging multi-step solver for: {user_message}")
        ai_response = solve_with_multi_step_refinement(user_message)
    elif intent == "autosci_mode":
        print(f"App.py: AutoSCI mode triggered.")
        ai_response = trigger_autosci_discovery() # Uses THINKER_MODEL_NAME by default
    else:
        # Fallback for unrecognized intents or if something goes wrong with NLU
        print(f"App.py: Unrecognized NLU intent ('{intent}') or fallback. Engaging multi-step solver for: {user_message}")
        ai_response = solve_with_multi_step_refinement(user_message)

    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True) 