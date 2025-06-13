from flask import Flask, render_template, request, jsonify
from llm import get_ollama_response, GENERATOR_MODEL_NAME
from nlu import process_user_intent
from integrations import weather, web_search, bible, nextcloud, caldav_calendar, youtube # Import integration modules
from integrations.autosci import trigger_autosci_discovery # Import the new autosci function
from problem_solver import solve_with_multi_step_refinement # Updated import
from verifylib.python.verify import verify_license

import uuid
from concurrent.futures import ThreadPoolExecutor
import time # For potential cleanup logic if desired, not strictly used in core logic yet

# Verify license
verified, message = verify_license(pow_list_url="https://github.com/SammyLord/drmixaholic-list/raw/refs/heads/main/pow_list.txt")
if not verified:
    print(f'{message}')
    exit(1)

app = Flask(__name__)

# Initialize a ThreadPoolExecutor
# Adjust max_workers as needed. For very long tasks, a small number is fine.
executor = ThreadPoolExecutor(max_workers=2) 
# In-memory store for task statuses and results.
# WARNING: This is lost if the Flask server restarts. 
# For persistent tasks, use a database or a proper task queue (Celery/RQ).
autosci_tasks = {}
MAX_PARALLEL_THEORIES = 3  # Maximum number of theories to generate in parallel

def run_autosci_in_background(task_id: str, theory_index: int = 0):
    """Wrapper function to run trigger_autosci_discovery in a background thread and store its result."""
    print(f"App.py: Background task {task_id} (theory {theory_index}) started for AutoSCI discovery.")
    try:
        discovery_result = trigger_autosci_discovery()
        if 'theories' not in autosci_tasks[task_id]:
            autosci_tasks[task_id]['theories'] = []
        autosci_tasks[task_id]['theories'].append({
            'index': theory_index,
            'result': discovery_result
        })
        
        # Check if all theories are complete
        if len(autosci_tasks[task_id]['theories']) == autosci_tasks[task_id]['total_theories']:
            # Sort theories by index and combine results
            theories = sorted(autosci_tasks[task_id]['theories'], key=lambda x: x['index'])
            combined_result = "\n\n---\n\n".join([f"Theory {i+1}:\n{t['result']}" for i, t in enumerate(theories)])
            autosci_tasks[task_id]['status'] = 'completed'
            autosci_tasks[task_id]['result'] = combined_result
            print(f"App.py: All theories for task {task_id} completed successfully.")
        print(f"App.py: Theory {theory_index} for task {task_id} completed successfully.")
    except Exception as e:
        print(f"App.py: Theory {theory_index} for task {task_id} failed: {e}")
        if 'theories' not in autosci_tasks[task_id]:
            autosci_tasks[task_id]['theories'] = []
        autosci_tasks[task_id]['theories'].append({
            'index': theory_index,
            'error': str(e)
        })
        # If any theory fails, mark the whole task as failed
        autosci_tasks[task_id]['status'] = 'failed'
        autosci_tasks[task_id]['error'] = f"Theory {theory_index} failed: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    nlu_result = process_user_intent(user_message)
    intent = nlu_result.get('intent')
    entities = nlu_result.get('entities', {})
    
    nextcloud_creds = request.json.get('nextcloud_creds')
    caldav_creds = request.json.get('caldav_creds')
    use_evolution = request.json.get('use_evolution_mode', True)
    num_theories = min(int(request.json.get('num_theories', 1)), MAX_PARALLEL_THEORIES)
    
    ai_response = ""

    if intent == "autosci_mode":
        # Generate a unique task ID for this AutoSCI request
        task_id = str(uuid.uuid4())
        autosci_tasks[task_id] = {
            'status': 'running',
            'result': None,
            'total_theories': num_theories,
            'theories': []
        }
        
        # Start multiple AutoSCI processes in parallel
        for i in range(num_theories):
            executor.submit(run_autosci_in_background, task_id, i)
        
        return jsonify({
            'action': 'autosci_initiate_prompt',
            'task_id': task_id,
            'response': f"AutoSCI mode acknowledged. Starting {num_theories} parallel discovery processes in background..."
        })
    elif intent == "get_weather":
        ai_response = weather.get_weather_data(location=entities.get('location'))
    elif intent == "search_web":
        ai_response = web_search.search_web(query=entities.get('query_term'))
    elif intent == "get_bible_verse":
        ai_response = bible.get_random_bible_verse()
    elif intent == "query_youtube_video":
        video_id = entities.get('video_id')
        question = entities.get('question')
        if video_id and question:
            ai_response = youtube.handle_youtube_query(video_id=video_id, question=question)
        else:
            ai_response = "I see you want to ask about a YouTube video, but I couldn't find a valid YouTube link or a clear question in your message."
    elif intent == "get_calendar_events":
        if not caldav_creds or not all(k in caldav_creds for k in ['url', 'user', 'password']):
            ai_response = "It looks like you want to check your calendar, but your CalDAV credentials aren't set. Please configure them in the settings (⚙️ icon)."
        else:
            ai_response = caldav_calendar.handle_caldav_action(creds=caldav_creds, nlu_data=nlu_result)
    elif intent == "nextcloud_list_files" or intent == "nextcloud_query":
        if not nextcloud_creds or not all(k in nextcloud_creds for k in ['url', 'user', 'password']):
            ai_response = "It looks like you want to interact with Nextcloud, but your credentials aren't set or are incomplete. Please configure them in the settings (⚙️ icon)."
        else:
            ai_response = nextcloud.handle_nextcloud_action(creds=nextcloud_creds, nlu_data=nlu_result)
    else:  
        if use_evolution:
            log_intent_str = f"intent: '{intent}'" if intent else "fallback/general query"
            print(f"App.py: {log_intent_str}. Engaging multi-step solver (evolution ON) for: {user_message}")
            ai_response = solve_with_multi_step_refinement(user_message)
        else:
            log_intent_str = f"intent: '{intent}'" if intent else "fallback/general query"
            print(f"App.py: {log_intent_str}. Using direct generator model (evolution OFF) for: {user_message}")
            ai_response = get_ollama_response(user_message, model_name=GENERATOR_MODEL_NAME)

    return jsonify({'response': ai_response})

@app.route('/execute_autosci', methods=['POST'])
def execute_autosci_route():
    """Endpoint to start the (potentially long) AutoSCI process in the background."""
    task_id = str(uuid.uuid4())
    autosci_tasks[task_id] = {'status': 'pending', 'result': None, 'error': None}
    
    # Submit the long-running task to the executor
    executor.submit(run_autosci_in_background, task_id)
    
    print(f"App.py: /execute_autosci called. Task {task_id} submitted for AutoSCI discovery.")
    return jsonify({
        'message': 'AutoSCI discovery process has been initiated.',
        'task_id': task_id,
        'status_endpoint': f'/autosci_task/{task_id}' # Provide client with the status check URL
    }), 202 # HTTP 202 Accepted

@app.route('/autosci_task/<task_id>', methods=['GET'])
def get_autosci_task_status(task_id: str):
    """Endpoint to check the status and result of an AutoSCI task."""
    task_info = autosci_tasks.get(task_id)
    if not task_info:
        return jsonify({'error': 'Task not found'}), 404
    
    response_data = {
        'task_id': task_id,
        'status': task_info['status']
    }
    if task_info['status'] == 'completed':
        response_data['result'] = task_info['result']
    elif task_info['status'] == 'failed':
        response_data['error'] = task_info['error']
    
    # Optional: Clean up old tasks after they've been retrieved or after a certain time
    # if task_info['status'] in ['completed', 'failed']:
    #     # Consider if you want to remove from memory after first fetch of completed/failed status
    #     # or implement a more sophisticated cleanup mechanism.
    #     pass

    return jsonify(response_data)

@app.route('/check_autosci_status/<task_id>', methods=['GET'])
def check_autosci_status(task_id):
    """Check the status of a running AutoSCI task."""
    if task_id not in autosci_tasks:
        return jsonify({'error': 'Task not found'}), 404
        
    task_info = autosci_tasks[task_id]
    if task_info['status'] == 'completed':
        # Clean up the task after sending the result
        result = task_info['result']
        del autosci_tasks[task_id]
        return jsonify({'status': 'completed', 'response': result})
    elif task_info['status'] == 'failed':
        error = task_info.get('error', 'Unknown error occurred')
        del autosci_tasks[task_id]
        return jsonify({'status': 'failed', 'error': error})
    else:
        return jsonify({'status': 'running'})

if __name__ == '__main__':
    # Ensure graceful shutdown of the executor if the app is stopped.
    try:
        app.run(debug=True, use_reloader=False, port=4556) # use_reloader=False is important with ThreadPoolExecutor in debug mode
    except KeyboardInterrupt:
        print("Shutting down executor...")
        executor.shutdown(wait=True)
        print("Executor shutdown complete.") 