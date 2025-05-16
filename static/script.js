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
            setCookie('numTheories', numTheoriesInput.value, 365);
            alert('Settings saved! Note: Password is stored in a cookie, which is not recommended for sensitive data in production environments.');
            settingsModal.style.display = "none";
        };
    }

    // Load settings from cookies on page load
    function loadSettings() {
        const url = getCookie('nextcloudUrl');
        const user = getCookie('nextcloudUser');
        const pass = getCookie('nextcloudPass');
        const numTheories = getCookie('numTheories');
        if (nextcloudUrlInput && url) nextcloudUrlInput.value = url;
        if (nextcloudUserInput && user) nextcloudUserInput.value = user;
        if (nextcloudPassInput && pass) nextcloudPassInput.value = pass;
        if (numTheoriesInput && numTheories) numTheoriesInput.value = numTheories;
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
        const autosciResultPlaceholder = addMessageToChat('assistant', 'Starting AutoSCI discovery process...', 'system-message');

        // Get number of theories from settings
        const numTheories = parseInt(getCookie('numTheories') || '1');

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: messageText,
                nextcloud_creds: getNextcloudCredentials(),
                use_evolution_mode: true,
                num_theories: numTheories
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.action === 'autosci_initiate_prompt') {
                // Start polling for AutoSCI task status
                const taskId = data.task_id;
                const pollInterval = setInterval(() => {
                    fetch(`/check_autosci_status/${taskId}`)
                        .then(response => response.json())
                        .then(statusData => {
                            if (statusData.status === 'completed') {
                                clearInterval(pollInterval);
                                autosciResultPlaceholder.classList.remove('system-message');
                                autosciResultPlaceholder.textContent = statusData.response;
                                speak(statusData.response);
                            } else if (statusData.status === 'failed') {
                                clearInterval(pollInterval);
                                autosciResultPlaceholder.classList.remove('system-message');
                                autosciResultPlaceholder.classList.add('error-message');
                                autosciResultPlaceholder.textContent = `AutoSCI Error: ${statusData.error}`;
                                speak(`AutoSCI Error: ${statusData.error}`);
                            } else {
                                // Update status message to show progress
                                const theories = autosci_tasks[taskId]?.theories || [];
                                const completed = theories.length;
                                const total = autosci_tasks[taskId]?.total_theories || numTheories;
                                autosciResultPlaceholder.textContent = `AutoSCI discovery in progress... (${completed}/${total} theories completed)`;
                            }
                        })
                        .catch(error => {
                            clearInterval(pollInterval);
                            console.error('AutoSCI Status Check Error:', error);
                            autosciResultPlaceholder.classList.remove('system-message');
                            autosciResultPlaceholder.classList.add('error-message');
                            autosciResultPlaceholder.textContent = 'Sorry, something went wrong while checking the AutoSCI discovery status.';
                            speak(autosciResultPlaceholder.textContent);
                        });
                }, 2000); // Poll every 2 seconds

                // Remove the initial AI response placeholder since we're handling AutoSCI
                aiResponsePlaceholder.remove();
            } else {
                // Handle regular responses
                aiResponsePlaceholder.textContent = data.response;
                aiResponsePlaceholder.classList.remove('system-message');
                speak(data.response);
                // Remove the AutoSCI placeholder since we're not using it
                autosciResultPlaceholder.remove();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            aiResponsePlaceholder.classList.remove('system-message');
            aiResponsePlaceholder.classList.add('error-message');
            aiResponsePlaceholder.textContent = 'Sorry, something went wrong while processing your message.';
            speak(aiResponsePlaceholder.textContent);
            // Remove the AutoSCI placeholder since we're not using it
            autosciResultPlaceholder.remove();
        });
    }

    function appendMessage(text, className) {
        const messageDiv = document.createElement('div');
        // Ensure className is treated as potentially multiple classes
        const classes = className ? className.split(' ').filter(c => c) : [];
        messageDiv.classList.add('message', ...classes);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
        return messageDiv; // Return the created element
    }

    function addMessageToChat(role, content, className) {
        const messageDiv = appendMessage(content, className);
        messageDiv.classList.add('message', role);
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
        return messageDiv;
    }

    function getNextcloudCredentials() {
        const ncUrl = getCookie('nextcloudUrl');
        const ncUser = getCookie('nextcloudUser');
        const ncPass = getCookie('nextcloudPass');
        if (ncUrl && ncUser && ncPass) {
            return {
                url: ncUrl,
                user: ncUser,
                password: ncPass
            };
        }
        return null;
    }
}); 