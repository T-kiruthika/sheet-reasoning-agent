document.addEventListener('DOMContentLoaded', function() {
    const fileUploadInput = document.getElementById('file-upload');
    const uploadStatusDiv = document.getElementById('upload-status');
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const themeToggle = document.getElementById('theme-toggle');

    function setTeam(isDark) {
        if (isDark) {
            document.body.classList.add('dark-mode');
            themeToggle.checked = true;
        } else {
            document.body.classList.remove('dark-mode');
            themeToggle.checked = false;
        }
    }
    
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme === 'dark') {
        setTeam(true);
    } else if (savedTheme === 'light') {
        setTeam(false);
    } else {
        setTeam(prefersDark);
    }

    themeToggle.addEventListener('change', () => {
        if (themeToggle.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });

    fileUploadInput.addEventListener('change', async function() {
        if (this.files.length === 0) return;

        const file = this.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        setStatus('Uploading and processing...', 'normal');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                setStatus(data.success, 'success');
                userInput.disabled = false;
                sendBtn.disabled = false;
                userInput.placeholder = "Ask a question about your data...";
                addBotMessage("Your file is ready. What would you like to know?");
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            setStatus(error.message, 'error');
            userInput.disabled = true;
            sendBtn.disabled = true;
            userInput.placeholder = "Please upload a file to start.";
        }
    });

    function setStatus(message, type) {
        uploadStatusDiv.textContent = message;
        uploadStatusDiv.className = type; 
    }

    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            handleSendMessage();
        }
    });

    async function handleSendMessage() {
        const question = userInput.value.trim();
        if (!question) return;

        addMessage(question, 'user');
        userInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question })
            });
            
            removeTypingIndicator();
            const data = await response.json();
            
            if (response.ok) {
                addBotMessage(data.answer);
            } else {
                throw new Error(data.error || "An unknown error occurred.");
            }

        } catch (error) {
            removeTypingIndicator();
            addBotMessage(`Error: ${error.message}`);
        }
    }

    function addMessage(content, type) {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message', `${type}-message`);
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.innerHTML = content; 
        
        messageWrapper.appendChild(messageContent);
        chatBox.appendChild(messageWrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addBotMessage(content) {
        addMessage(content, 'bot');
    }

    function showTypingIndicator() {
        const indicator = `
            <div class="message bot-message" id="typing-indicator">
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        chatBox.insertAdjacentHTML('beforeend', indicator);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
});
