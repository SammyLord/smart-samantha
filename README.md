# Smart Samantha AI Agent

A conversational AI agent with a web interface, powered by local LLMs via Ollama, and integrated with various services.

## Overview

Smart Samantha is a Python-based AI assistant built with Flask for the web interface and utilizes a multi-LLM, multi-step approach for its core intelligence. The agent aims to understand natural language requests, process them through a sophisticated reasoning pipeline, and interact with external services or provide deeply considered conversational responses.

Current capabilities include:
- Text-based and voice-based (via browser STT/TTS) chat.
- Natural Language Understanding (NLU) to determine user intent and extract entities.
- **Advanced Problem Solving**: For general queries, uses a multi-step refinement process involving two different LLMs:
    1.  **Initial Idea Generation**: A generator LLM (`sparksammy/tinysam-l3.2-v2`) brainstorms initial approaches.
    2.  **Best Approach Selection**: A thinker LLM (`sparksammy/samantha-thinker-v2`) selects the most promising conceptual approach.
    3.  **Prototype Generation**: The generator LLM creates concrete prototypes for the selected approach.
    4.  **Iterative Evolution**: The thinker LLM selects the best prototype and iteratively refines it into a final solution.
- **"AutoSCI" Mode**: A creative mode where the AI invents a scientific/mathematical theory and then a related "discovery," powered by the thinker LLM.
- Integration with Nextcloud (listing files).
- Fetching current weather information.
- Performing web searches (via DuckDuckGo Instant Answers).
- Retrieving random Bible verses.

## Features

-   **Web Interface**: Chat with Samantha through a clean web UI.
-   **Voice Interaction**: Use your microphone to talk to Samantha and hear responses spoken back (requires browser support for Web Speech API).
-   **Dual LLM Powered**: 
    -   Generator Model: `sparksammy/tinysam-l3.2-v2` (for brainstorming and prototyping).
    -   Thinker Model: `sparksammy/samantha-thinker-v2` (for evaluation, selection, refinement, and creative tasks).
    -   Both accessed via an Ollama-compatible API endpoint (`https://ollama-api.nodemixaholic.com/v1`).
-   **NLU Layer**: Processes user input to determine intent (e.g., get weather, search web, list Nextcloud files, AutoSCI mode) and extracts relevant entities.
-   **Multi-Step Refinement for General Queries**: Provides more thoughtful and developed answers to complex or open-ended questions.
-   **Creative "AutoSCI" Mode**: Allows the AI to generate imaginative scientific theories and discoveries - similar to AlphaEvolve.
-   **Modular Integrations**:
    -   **Nextcloud**: List files and folders from your Nextcloud instance. Credentials are set via a settings menu in the UI and stored in browser cookies. Operations are performed server-side.
    -   **Weather**: Get current weather information using the Open-Meteo API (no API key required).
    -   **Web Search**: Get quick answers and information using the DuckDuckGo Instant Answer API (no API key required).
    -   **Bible Verses**: Fetch random Bible verses from bible-api.com (no API key required).
-   **Settings**: Configure Nextcloud connection details (URL, username, password) through an in-app settings modal.

## Setup

1.  **Prerequisites**:
    *   Python 3.8+
    *   An Ollama-compatible API endpoint accessible and running the desired models (default: `sparksammy/tinysam-l3.2-v2` and `sparksammy/samantha-thinker-v2` at `https://ollama-api.nodemixaholic.com/v1`). You can change the `OLLAMA_API_URL` and model name constants in `llm.py`.

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
    *(Note: The multi-step refinement process for general queries can be slow due to multiple LLM calls. Monitor your console for progress logs from `problem_solver.py`.)*

2.  **Access the Web Interface**:
    Open your web browser and navigate to `http://127.0.0.1:5000` (or the address shown in your terminal).

## Using the Features

-   **Chat**: Type your message in the input box or click the microphone icon to use voice input. General queries will trigger the multi-step refinement process.
-   **"AutoSCI" Mode**: Try saying "activate autosci mode" or "make a scientific discovery".
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
-   `llm.py`: Handles communication with the Ollama LLM API (supports multiple models).
-   `nlu.py`: Performs Natural Language Understanding (intent recognition, entity extraction).
-   `problem_solver.py`: Implements the multi-step refinement logic for general queries using generator and thinker LLMs.
-   `requirements.txt`: Python dependencies.
-   `README.md`: This file.
-   `integrations/`: Directory for modules that connect to external services or provide special modes.
    -   `__init__.py`
    -   `autosci.py` (Implements the AutoSCI creative mode)
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

-   **Performance Optimization**: Investigate ways to reduce latency for the multi-step refinement process (e.g., prompt optimization, considering asynchronous operations if feasible, parallel calls if models/API support).
-   **Refined NLU**: Improve intent classification accuracy and entity extraction robustness.
-   **Advanced Prompt Engineering**: Continuously refine prompts for all stages of the problem-solving pipeline and AutoSCI mode for better quality and coherence.
-   **Tune Idea/Prototype Counts**: Experiment with the number of initial ideas, prototypes, and evolution steps.
-   **User Feedback for Latency**: Implement visual cues in the UI to indicate when the multi-step process is active.
-   **Expanded Nextcloud Capabilities**.
-   **Contextual Conversations**.
-   **Improved Security for Nextcloud Credentials**.

---
This README reflects the latest advanced features. 
