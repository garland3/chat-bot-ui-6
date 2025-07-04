// static/app.js

document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const chatMessages = document.getElementById('chatMessages');
    const statusIndicator = document.getElementById('statusIndicator');
    const toolSelect = document.getElementById('toolSelect');
    const toastContainer = document.getElementById('toastContainer');

    let sessionId = null;
    let ws = null;

    // Function to display toast notifications
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.classList.add('toast', type);
        toast.textContent = message;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        setTimeout(() => {
            toast.classList.remove('show');
            toast.addEventListener('transitionend', () => toast.remove());
        }, 3000);
    }

    // Function to add a message to the chat window
    function addMessage(message, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.textContent = message;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to connect to WebSocket
    function connectWebSocket(sId) {
        if (ws) ws.close();

        ws = new WebSocket(`ws://localhost:8000/ws/${sId}`);

        ws.onopen = () => {
            statusIndicator.classList.add('connected');
            showToast('Connected to chat', 'success');
        };

        ws.onmessage = (event) => {
            // Handle real-time updates from WebSocket
            console.log('WebSocket message received:', event.data);
            // Example: showToast(event.data, 'info');
        };

        ws.onclose = () => {
            statusIndicator.classList.remove('connected');
            showToast('Disconnected from chat', 'error');
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            showToast('WebSocket error', 'error');
        };
    }

    // Function to create a new chat session
    async function createChatSession() {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-EMAIL-USER': 'test@example.com' // For testing, replace with actual auth
                }
            });
            const data = await response.json();
            if (response.ok) {
                sessionId = data.session_id;
                showToast(`Session created: ${sessionId}`, 'info');
                connectWebSocket(sessionId);
            } else {
                showToast(`Failed to create session: ${data.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error creating chat session:', error);
            showToast('Network error creating session', 'error');
        }
    }

    // Function to send a message
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        messageInput.value = '';

        if (!sessionId) {
            showToast('No active session. Creating one...', 'info');
            await createChatSession();
            if (!sessionId) {
                showToast('Could not create session. Message not sent.', 'error');
                return;
            }
        }

        try {
            const response = await fetch(`/chat/${sessionId}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-EMAIL-USER': 'test@example.com' // For testing, replace with actual auth
                },
                body: JSON.stringify({ content: message })
            });

            if (response.ok) {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let botResponse = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    botResponse += decoder.decode(value, { stream: true });
                    // Update UI with partial response
                    // For simplicity, we'll just update the last bot message
                    // In a real app, you'd stream into a new message element
                    if (chatMessages.lastChild && chatMessages.lastChild.classList.contains('bot')) {
                        chatMessages.lastChild.textContent = botResponse;
                    } else {
                        addMessage(botResponse, 'bot');
                    }
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            } else {
                const errorData = await response.json();
                showToast(`Error: ${errorData.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            showToast('Network error sending message', 'error');
        }
    }

    sendMessageBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Initial session creation on page load
    createChatSession();
});
