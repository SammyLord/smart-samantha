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

        // Prepare payload for the backend
        const payload = { message: messageText };

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
            if (data.error) {
                appendMessage(`Error: ${data.error}`, 'ai-message error-message');
                speak(`Error: ${data.error}`);
            } else if (data.action === 'autosci_initiate') {
                // Display the initial loading message for AutoSCI
                appendMessage(data.response, 'ai-message system-message'); // Use a distinct class if you want to style it
                speak(data.response);

                // Now make the follow-up request to actually execute AutoSCI
                fetch('/execute_autosci', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                    // body: JSON.stringify({}) // No body needed for now, but can add if params are needed
                })
                .then(response => response.json())
                .then(autosciData => {
                    if (autosciData.error) {
                        appendMessage(`AutoSCI Error: ${autosciData.error}`, 'ai-message error-message');
                        speak(`AutoSCI Error: ${autosciData.error}`);
                    } else {
                        appendMessage(autosciData.response, 'ai-message');
                        speak(autosciData.response);
                    }
                })
                .catch(error => {
                    console.error('AutoSCI Execution Error:', error);
                    const errorMsg = 'Sorry, something went wrong while trying to make an AutoSCI discovery.';
                    appendMessage(errorMsg, 'ai-message error-message');
                    speak(errorMsg);
                });

            } else {
                appendMessage(data.response, 'ai-message');
                speak(data.response); // Speak the AI's response
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const errorMsg = 'Sorry, something went wrong with the request.';
            appendMessage(errorMsg, 'ai-message');
            speak(errorMsg);
        });
    }

    function appendMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', className);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
    }
}); 