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
            alert('Settings saved!');
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
            userInput.value = "activate autosci mode";
            sendMessage();
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
            sendMessage();
        };

        recognition.onspeechend = () => {
            recognition.stop();
            micButton.textContent = '🎤';
            micButton.disabled = false;
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            micButton.textContent = '🎤';
            micButton.disabled = false;
        };
    }

    // Text-to-Speech (TTS)
    const synth = window.speechSynthesis;
    function speak(text) {
        if (!synth || !text) return;
        const utterThis = new SpeechSynthesisUtterance(text);
        utterThis.onerror = (event) => {
            console.error('SpeechSynthesisUtterance.onerror', event);
        };
        synth.speak(utterThis);
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendMessage());

    micButton.addEventListener('click', () => {
        if (!recognition) return;
        if (micButton.textContent === '🎤') {
            try {
                recognition.start();
                micButton.textContent = '...';
                micButton.disabled = true;
            } catch (e) {
                console.error("Error starting recognition", e);
                micButton.textContent = '🎤';
                micButton.disabled = false;
            }
        } else {
            recognition.stop();
        }
    });

    function sendMessage() {
        const messageText = userInput.value.trim();
        if (!messageText) return;

        addMessageToChat('user', messageText);
        userInput.value = '';

        const aiResponsePlaceholder = addMessageToChat('assistant', 'Thinking...', 'system-message');

        const nextcloudCreds = getNextcloudCredentials();
        const caldavCreds = getCaldavCredentials();

        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: messageText,
                nextcloud_creds: nextcloudCreds,
                caldav_creds: caldavCreds,
                use_evolution_mode: evolutionModeToggle.checked,
                num_theories: parseInt(numTheoriesInput.value || '1')
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.action === 'autosci_initiate_prompt') {
                // Handle AutoSCI initiation
                const taskId = data.task_id;
                const numTheories = parseInt(numTheoriesInput.value || '1');
                // Create a dedicated placeholder for this AutoSCI task
                const autosciTaskPlaceholder = addMessageToChat('assistant', `AutoSCI discovery started (Task ID: ${taskId})...`, 'system-message');
                pollAutosciStatus(taskId, autosciTaskPlaceholder, numTheories);
                aiResponsePlaceholder.remove(); // Remove the general "Thinking..." placeholder
            } else {
                // Use the placeholder to show the final response
                aiResponsePlaceholder.innerHTML = data.response; // Update content
                aiResponsePlaceholder.parentElement.classList.remove('system-message'); // Update class on the wrapper
                saveChatHistory(chatBox); // Save final state
                speak(data.response);
            }
        })
        .catch(error => {
            console.error('Chat Error:', error);
            aiResponsePlaceholder.innerHTML = 'Sorry, an error occurred.';
            aiResponsePlaceholder.parentElement.classList.add('error-message');
            saveChatHistory(chatBox);
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
                        placeholderElement.innerHTML = statusData.response;
                        placeholderElement.parentElement.classList.remove('system-message');
                        saveChatHistory(document.getElementById('chatBox'));
                        speak(statusData.response);
                    } else if (statusData.status === 'failed') {
                        clearInterval(pollInterval);
                        placeholderElement.innerHTML = `AutoSCI Error: ${statusData.error}`;
                        placeholderElement.parentElement.classList.add('error-message');
                        saveChatHistory(document.getElementById('chatBox'));
                        speak(`AutoSCI Error: ${statusData.error}`);
                    } else if (statusData.status === 'running' && statusData.progress) {
                        const { completed, total } = statusData.progress;
                        placeholderElement.innerHTML = `AutoSCI discovery in progress... (${completed}/${total} theories completed)`;
                    } else {
                        placeholderElement.innerHTML = `AutoSCI discovery in progress...`;
                    }
                })
                .catch(error => {
                    clearInterval(pollInterval);
                    console.error('AutoSCI Status Check Error:', error);
                    placeholderElement.innerHTML = 'Sorry, something went wrong while checking the AutoSCI discovery status.';
                    placeholderElement.parentElement.classList.add('error-message');
                    saveChatHistory(document.getElementById('chatBox'));
                    speak(placeholderElement.textContent);
                });
        }, 3000); // Poll every 3 seconds
    }

    function getNextcloudCredentials() {
        return {
            url: nextcloudUrlInput.value.trim(),
            user: nextcloudUserInput.value.trim(),
            password: nextcloudPassInput.value.trim()
        };
    }

    function getCaldavCredentials() {
        return {
            url: caldavUrlInput.value.trim(),
            user: caldavUserInput.value.trim(),
            password: caldavPassInput.value.trim()
        };
    }

    // Load history at the end of DOMContentLoaded
    loadChatHistory();
});

function saveChatHistory(chatBox) {
    const messages = [];
    chatBox.childNodes.forEach(node => {
        if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('chat-message')) {
            messages.push({
                role: node.dataset.role,
                content: node.querySelector('.message-content').innerHTML,
                className: node.className.replace('chat-message', '').trim()
            });
        }
    });
    localStorage.setItem('chatHistory', JSON.stringify(messages));
}

function loadChatHistory() {
    const chatBox = document.getElementById('chatBox');
    const messages = JSON.parse(localStorage.getItem('chatHistory') || '[]');
    messages.forEach(msg => {
        addMessageToChat(msg.role, msg.content, msg.className, false); // Add without re-saving
    });
}

function addMessageToChat(role, content, className = '', save = true) {
    const chatBox = document.getElementById('chatBox');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = `chat-message ${role}-message ${className}`.trim();
    messageWrapper.dataset.role = role;

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // If the content is from user input, escape it to prevent HTML injection
    // Otherwise, for assistant messages or loaded history, we assume it's safe HTML
    if (role === 'user' && save === true) {
         messageContent.textContent = content;
    } else {
         messageContent.innerHTML = content;
    }

    messageWrapper.appendChild(messageContent);
    chatBox.appendChild(messageWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;

    if (save) {
        saveChatHistory(chatBox);
    }

    return messageContent; // Return for updates
}