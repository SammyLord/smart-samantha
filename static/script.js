document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const micButton = document.getElementById('micButton');
    const chatBox = document.getElementById('chatBox');

    // Settings Modal Elements
    const settingsButton = document.getElementById('settingsButton');
    const settingsModal = document.getElementById('settingsModal');
    const closeSettingsModal = document.getElementById('closeSettingsModal');
    const saveSettingsButton = document.getElementById('saveSettingsButton');
    const nextcloudUrlInput = document.getElementById('nextcloudUrl');
    const nextcloudUserInput = document.getElementById('nextcloudUser');
    const nextcloudPassInput = document.getElementById('nextcloudPass');
    const caldavUrlInput = document.getElementById('caldavUrl');
    const caldavUserInput = document.getElementById('caldavUser');
    const caldavPassInput = document.getElementById('caldavPass');
    const numTheoriesInput = document.getElementById('numTheories');
    const autosciButton = document.getElementById('autosciButton');
    const evolutionModeToggle = document.getElementById('evolutionModeToggle');

    // Cookie helper functions
    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    // Settings Modal Logic
    if (settingsButton) {
        settingsButton.onclick = () => { settingsModal.style.display = "block"; };
    }
    if (closeSettingsModal) {
        closeSettingsModal.onclick = () => { settingsModal.style.display = "none"; };
    }
    window.onclick = (event) => {
        if (event.target === settingsModal) {
            settingsModal.style.display = "none";
        }
    };

    if (saveSettingsButton) {
        saveSettingsButton.onclick = () => {
            setCookie('nextcloudUrl', nextcloudUrlInput.value, 365);
            setCookie('nextcloudUser', nextcloudUserInput.value, 365);
            setCookie('nextcloudPass', nextcloudPassInput.value, 365);
            setCookie('caldavUrl', caldavUrlInput.value, 365);
            setCookie('caldavUser', caldavUserInput.value, 365);
            setCookie('caldavPass', caldavPassInput.value, 365);
            setCookie('numTheories', numTheoriesInput.value, 365);
            alert('Settings saved! Note: Passwords are stored in cookies, which is not recommended for sensitive data in production environments.');
            settingsModal.style.display = "none";
        };
    }

    // Load settings from cookies on page load
    function loadSettings() {
        nextcloudUrlInput.value = getCookie('nextcloudUrl') || '';
        nextcloudUserInput.value = getCookie('nextcloudUser') || '';
        nextcloudPassInput.value = getCookie('nextcloudPass') || '';
        caldavUrlInput.value = getCookie('caldavUrl') || '';
        caldavUserInput.value = getCookie('caldavUser') || '';
        caldavPassInput.value = getCookie('caldavPass') || '';
        numTheoriesInput.value = getCookie('numTheories') || '1';
    }
    loadSettings();

    // AutoSCI Button Logic
    if (autosciButton) {
        autosciButton.onclick = () => {
            userInput.value = "activate autosci mode"; // Pre-fill input with command
            sendMessage(); // Trigger the send message logic
        };
    }

    // Speech Recognition (STT)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            userInput.value = speechResult;
            sendMessage(); // Optionally send message immediately after speech
        };

        recognition.onspeechend = () => {
            recognition.stop();
            micButton.textContent = '🎤';
            micButton.disabled = false;
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            alert(`Error in speech recognition: ${event.error}`);
            micButton.textContent = '🎤';
            micButton.disabled = false;
        };
    } else {
        console.warn('Speech Recognition API not supported in this browser.');
        micButton.disabled = true;
        micButton.title = 'Speech input not supported by your browser.';
    }

    // Text-to-Speech (TTS)
    const synth = window.speechSynthesis;
    let voices = [];

    function populateVoiceList() {
        if(typeof synth === 'undefined') {
            return;
        }
        voices = synth.getVoices();
        // You could add logic here to select a preferred voice
    }
    populateVoiceList();
    if (typeof synth !== 'undefined' && synth.onvoiceschanged !== undefined) {
        synth.onvoiceschanged = populateVoiceList;
    }

    function speak(text) {
        if (!synth || !text) {
            return;
        }
        const utterThis = new SpeechSynthesisUtterance(text);
        utterThis.onerror = (event) => {
            console.error('SpeechSynthesisUtterance.onerror', event);
        };
        // Optional: select a voice
        // const selectedVoice = voices.find(voice => voice.name === 'Google US English'); // Example
        // if (selectedVoice) utterThis.voice = selectedVoice;
        synth.speak(utterThis);
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    micButton.addEventListener('click', () => {
        if (!recognition) return;
        if (micButton.textContent === '🎤') {
            try {
                recognition.start();
                micButton.textContent = '...'; // Indicate listening
                micButton.disabled = true;
            } catch (e) {
                console.error("Error starting recognition (already started?)", e);
                 micButton.textContent = '🎤';
                 micButton.disabled = false;
            }
        } else {
            recognition.stop();
            micButton.textContent = '🎤';
            micButton.disabled = false;
        }
    });

    function sendMessage() {
        const messageText = userInput.value.trim();
        if (!messageText) return;

        // Add user message to chat
        addMessageToChat('user', messageText);
        userInput.value = '';

        // Show placeholder for AI response
        const aiResponsePlaceholder = addMessageToChat('assistant', 'Thinking...', 'system-message');
        
        // Hide or remove the autosci placeholder initially
        const autosciResultPlaceholder = document.querySelector('.autosci-result-placeholder');
        if (autosciResultPlaceholder) {
            autosciResultPlaceholder.style.display = 'none';
        }

        // Get credentials and settings
        const numTheories = parseInt(numTheoriesInput.value || '1');
        const evolutionMode = evolutionModeToggle.checked;
        const nextcloudCreds = getNextcloudCredentials();
        const caldavCreds = getCaldavCredentials();

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: messageText,
                nextcloud_creds: nextcloudCreds,
                caldav_creds: caldavCreds,
                use_evolution_mode: evolutionMode,
                num_theories: numTheories
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.action === 'autosci_initiate_prompt') {
                // Handle AutoSCI initiation
                const taskId = data.task_id;
                // Create a dedicated placeholder for this AutoSCI task
                const autosciTaskPlaceholder = addMessageToChat('assistant', `AutoSCI discovery started (Task ID: ${taskId})...`, 'system-message');
                pollAutosciStatus(taskId, autosciTaskPlaceholder, numTheories);
                aiResponsePlaceholder.remove(); // Remove the general "Thinking..." placeholder
            } else {
                // Handle regular chat responses
                aiResponsePlaceholder.textContent = data.response;
                aiResponsePlaceholder.classList.remove('system-message');
                speak(data.response);
            }
        })
        .catch(error => {
            console.error('Chat Error:', error);
            aiResponsePlaceholder.textContent = 'Sorry, an error occurred.';
            aiResponsePlaceholder.classList.add('error-message');
            speak('Sorry, an error occurred.');
        });
    }

    function pollAutosciStatus(taskId, placeholderElement, totalTheories) {
        const pollInterval = setInterval(() => {
            fetch(`/check_autosci_status/${taskId}`)
                .then(response => response.json())
                .then(statusData => {
                    if (statusData.status === 'completed') {
                        clearInterval(pollInterval);
                        placeholderElement.textContent = statusData.response;
                        placeholderElement.classList.remove('system-message');
                        speak(statusData.response);
                    } else if (statusData.status === 'failed') {
                        clearInterval(pollInterval);
                        placeholderElement.textContent = `AutoSCI Error: ${statusData.error}`;
                        placeholderElement.classList.add('error-message');
                        placeholderElement.classList.remove('system-message');
                        speak(`AutoSCI Error: ${statusData.error}`);
                    } else if (statusData.status === 'running' && statusData.progress) {
                        // More detailed progress update
                        const { completed, total } = statusData.progress;
                        placeholderElement.textContent = `AutoSCI discovery in progress... (${completed}/${total} theories completed)`;
                    } else {
                        // Fallback progress update
                        placeholderElement.textContent = `AutoSCI discovery in progress...`;
                    }
                })
                .catch(error => {
                    clearInterval(pollInterval);
                    console.error('AutoSCI Status Check Error:', error);
                    placeholderElement.textContent = 'Sorry, something went wrong while checking the AutoSCI discovery status.';
                    placeholderElement.classList.add('error-message');
                    placeholderElement.classList.remove('system-message');
                    speak(placeholderElement.textContent);
                });
        }, 3000); // Poll every 3 seconds
    }
    
    function addMessageToChat(role, content, className = '') {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${role}-message`);
        if (className) {
            messageElement.classList.add(className);
        }
        // Basic Markdown-to-HTML conversion
        let formattedContent = content.replace(/\n/g, '<br>'); // Newlines to <br>
        formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>'); // **bold** to <b>
        formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<i>$1</i>');     // *italic* to <i>
        
        messageElement.innerHTML = formattedContent;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
        return messageElement;
    }

    function getNextcloudCredentials() {
        const url = getCookie('nextcloudUrl');
        const user = getCookie('nextcloudUser');
        const pass = getCookie('nextcloudPass');
        if (url && user && pass) {
            return { url, user, password: pass };
        }
        return null;
    }

    function getCaldavCredentials() {
        const url = getCookie('caldavUrl');
        const user = getCookie('caldavUser');
        const pass = getCookie('caldavPass');
        if (url && user && pass) {
            return { url, user, password: pass };
        }
        return null;
    }
}); 