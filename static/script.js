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
            setCookie('nextcloudPass', nextcloudPassInput.value, 365); // Storing password in cookie is not ideal for production
            alert('Nextcloud settings saved! Password is stored in a cookie, which is not recommended for sensitive data in production environments.');
            settingsModal.style.display = "none";
        };
    }

    // Load settings from cookies on page load
    function loadSettings() {
        const url = getCookie('nextcloudUrl');
        const user = getCookie('nextcloudUser');
        const pass = getCookie('nextcloudPass');
        if (nextcloudUrlInput && url) nextcloudUrlInput.value = url;
        if (nextcloudUserInput && user) nextcloudUserInput.value = user;
        if (nextcloudPassInput && pass) nextcloudPassInput.value = pass;
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
        if (messageText === '') return;

        appendMessage(messageText, 'user-message');
        userInput.value = '';

        // Create a placeholder for AI's response / system messages
        let aiResponsePlaceholder = appendMessage("Samantha is thinking...", 'ai-message system-message');

        // Prepare payload for the backend
        const payload = { 
            message: messageText,
            use_evolution_mode: evolutionModeToggle ? evolutionModeToggle.checked : true
        };

        // Read Nextcloud creds from cookies and add to payload if they exist
        const ncUrl = getCookie('nextcloudUrl');
        const ncUser = getCookie('nextcloudUser');
        const ncPass = getCookie('nextcloudPass');

        if (ncUrl && ncUser && ncPass) {
            payload.nextcloud_creds = {
                url: ncUrl,
                user: ncUser,
                password: ncPass
            };
        }

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload) // Send the modified payload
        })
        .then(response => response.json())
        .then(data => {
            // Clear placeholder styles first, then update content and add new class if needed
            aiResponsePlaceholder.classList.remove('system-message', 'error-message');

            if (data.error) {
                aiResponsePlaceholder.textContent = `Error: ${data.error}`;
                aiResponsePlaceholder.classList.add('error-message');
                speak(`Error: ${data.error}`);
            } else if (data.action === 'autosci_initiate') {
                aiResponsePlaceholder.textContent = data.response; // The "Please wait, thinking deeply..." message
                aiResponsePlaceholder.classList.add('system-message');
                speak(data.response);

                // Now make the follow-up request to actually execute AutoSCI
                // Create a new placeholder for the actual AutoSCI discovery result
                let autosciResultPlaceholder = appendMessage("AutoSCI discovery in progress...", 'ai-message system-message');
                
                fetch('/execute_autosci', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(autosciData => {
                    autosciResultPlaceholder.classList.remove('system-message', 'error-message');
                    if (autosciData.error) {
                        autosciResultPlaceholder.textContent = `AutoSCI Error: ${autosciData.error}`;
                        autosciResultPlaceholder.classList.add('error-message');
                        speak(`AutoSCI Error: ${autosciData.error}`);
                    } else {
                        autosciResultPlaceholder.textContent = autosciData.response;
                        // autosciResultPlaceholder.classList.remove('system-message'); // Already removed above
                        speak(autosciData.response);
                    }
                })
                .catch(error => {
                    console.error('AutoSCI Execution Error:', error);
                    autosciResultPlaceholder.classList.remove('system-message');
                    autosciResultPlaceholder.textContent = 'Sorry, something went wrong while trying to make an AutoSCI discovery.';
                    autosciResultPlaceholder.classList.add('error-message');
                    speak(autosciResultPlaceholder.textContent);
                });

            } else { // Standard successful response (including multi-step refinement)
                aiResponsePlaceholder.textContent = data.response;
                // aiResponsePlaceholder.classList.remove('system-message'); // Already removed above
                speak(data.response);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            aiResponsePlaceholder.classList.remove('system-message');
            aiResponsePlaceholder.textContent = 'Sorry, something went wrong with the request.';
            aiResponsePlaceholder.classList.add('error-message');
            speak(aiResponsePlaceholder.textContent);
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
}); 