# Smart Samantha AI Agent

A conversational AI agent with a web interface, powered by a local LLM via Ollama, and integrated with various services.

## Overview

Smart Samantha is a Python-based AI assistant built with Flask for the web interface and an Ollama-compatible Large Language Model (LLM) for its core intelligence. The agent aims to understand natural language requests, process them, and interact with external services or provide conversational responses.

Current capabilities include:
- Text-based and voice-based (via browser STT/TTS) chat.
- Natural Language Understanding (NLU) to determine user intent and extract entities.
- Integration with Nextcloud (listing files).
- Fetching current weather information.
- Performing web searches (via DuckDuckGo Instant Answers).
- Retrieving random Bible verses.

## Features

-   **Web Interface**: Chat with Samantha through a clean web UI.
-   **Voice Interaction**: Use your microphone to talk to Samantha and hear responses spoken back (requires browser support for Web Speech API).
-   **LLM Powered**: Uses the `sparksammy/tinysam-l3.2-v2` model (configurable) via an Ollama-compatible API endpoint (`https://ollama-api.nodemixaholic.com/v1`).
-   **NLU Layer**: Processes user input to determine intent (e.g., get weather, search web, list Nextcloud files) and extracts relevant entities (e.g., location for weather, search query, path for Nextcloud).
-   **Modular Integrations**:
    -   **Nextcloud**: List files and folders from your Nextcloud instance. Credentials are set via a settings menu in the UI and stored in browser cookies. Operations are performed server-side.
    -   **Weather**: Get current weather information using the Open-Meteo API (no API key required).
    -   **Web Search**: Get quick answers and information using the DuckDuckGo Instant Answer API (no API key required).
    -   **Bible Verses**: Fetch random Bible verses from bible-api.com (no API key required).
-   **Settings**: Configure Nextcloud connection details (URL, username, password) through an in-app settings modal.

## Setup

1.  **Prerequisites**:
    *   Python 3.8+
    *   An Ollama-compatible API endpoint accessible and running the desired model (default: `sparksammy/tinysam-l3.2-v2` at `https://ollama-api.nodemixaholic.com/v1`). You can change the `OLLAMA_API_URL` and `MODEL_NAME` constants in `llm.py`.

2.  **Clone the Repository (if applicable)**:
    ```bash
    # git clone <repository_url>
    # cd smart-samantha-ai 
    ```

3.  **Create a Virtual Environment (Recommended)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    The `requirements.txt` file includes:
    *   Flask
    *   Requests
    *   webdavclient3

## Running the Application

1.  **Start the Flask Application**:
    ```bash
    python app.py
    ```

2.  **Access the Web Interface**:
    Open your web browser and navigate to `http://127.0.0.1:5000` (or the address shown in your terminal).

## Using the Features

-   **Chat**: Type your message in the input box or click the microphone icon to use voice input.
-   **Nextcloud Integration**:
    1.  Click the "⚙️ Settings" button in the top-right corner.
    2.  Enter your Nextcloud instance URL (e.g., `https://cloud.example.com`), your Nextcloud username, and your Nextcloud password.
    3.  Click "Save Settings".
    4.  You can then ask Samantha to list files, e.g., "list my files on nextcloud", "show me what's in /Documents/Work on nextcloud".
-   **Weather**: Ask "what's the weather in London?".
-   **Web Search**: Ask "search for the capital of France" or "what is a neural network?".
-   **Bible Verse**: Ask "give me a bible verse".

## Code Structure

-   `app.py`: Main Flask application, handles routing and core logic.
-   `llm.py`: Handles communication with the Ollama LLM API.
-   `nlu.py`: Performs Natural Language Understanding (intent recognition, entity extraction).
-   `requirements.txt`: Python dependencies.
-   `README.md`: This file.
-   `integrations/`: Directory for modules that connect to external services.
    -   `__init__.py`
    -   `bible.py`
    -   `nextcloud.py` (server-side WebDAV logic)
    -   `weather.py`
    -   `web_search.py`
-   `static/`: Contains static assets for the web interface.
    -   `style.css`: CSS for styling.
    -   `script.js`: Client-side JavaScript for UI interactions, STT/TTS, and sending messages.
-   `templates/`: Contains HTML templates.
    -   `index.html`: Main HTML page for the chat interface.

## Future Enhancements (Potential Roadmap)

-   **Refined NLU**: Improve intent classification accuracy and entity extraction robustness.
-   **Expanded Nextcloud Capabilities**:
    -   More efficient file/folder type detection (using PROPFIND).
    -   Implement file upload, download, creation of folders, deletion, etc.
    -   Allow navigation through Nextcloud directories.
-   **Contextual Conversations**: Maintain conversation history for more natural follow-up questions.
-   **Improved Security**:
    -   For Nextcloud: Implement OAuth2 or Nextcloud App Passwords instead of storing user's main password.
-   **User Authentication/Accounts**: If the agent were to be multi-user or store persistent user-specific data.
-   **Additional Integrations**: As desired by the user (e.g., calendar, email, other APIs).
-   **Streaming LLM Responses**: For a more interactive feel.
-   **Customizable "Wake Word"**: For voice activation.

---
This README should provide a good starting point! 