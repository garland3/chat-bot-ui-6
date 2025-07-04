// Enhanced Chat Application JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const chatMessages = document.getElementById('chatMessages');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const toastContainer = document.getElementById('toastContainer');
    const newChatBtn = document.getElementById('newChatBtn');
    const charCount = document.getElementById('charCount');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const attachBtn = document.getElementById('attachBtn');
    const micBtn = document.getElementById('micBtn');
    const toolToggleBtn = document.getElementById('toolToggleBtn');
    const toolPanel = document.getElementById('toolPanel');
    const appTitle = document.getElementById('appTitle');
    const sidebarAppName = document.querySelector('.sidebar-header .logo span');
    const headerAppName = document.querySelector('.chat-header .header-left h1');
    const welcomeTitle = document.querySelector('.welcome-message h2');
    const llmSelect = document.getElementById('llmSelect');
    const downloadChatBtn = document.getElementById('downloadChatBtn');

    // Application State
    let sessionId = null;
    let ws = null;
    let isConnected = false;
    let isTyping = false;
    let currentStreamingMessage = null;

    // Initialize the application
    init();

    async function init() {
        setupEventListeners();
        setupTextareaAutoResize();
        await fetchAppSettings();
        await fetchLLMs();
        await createChatSession(); // Ensure session is created before connecting WS
        if (sessionId) {
            connectWebSocket(sessionId);
        }
        updateSendButtonState();
        // Remove initial 'Connecting...' status
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected';
    }

    // Event Listeners Setup
    function setupEventListeners() {
        console.log('Setting up event listeners...'); // Debug log
        // Send message events
        sendMessageBtn.addEventListener('click', handleSendMessage);
        messageInput.addEventListener('keydown', handleKeyDown);
        messageInput.addEventListener('input', handleInputChange);

        // New chat button
        newChatBtn.addEventListener('click', handleNewChat);

        // Suggested prompts
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('prompt-suggestion') || e.target.closest('.prompt-suggestion')) {
                const button = e.target.classList.contains('prompt-suggestion') ? e.target : e.target.closest('.prompt-suggestion');
                const prompt = button.getAttribute('data-prompt');
                if (prompt) {
                    messageInput.value = prompt;
                    updateCharacterCount();
                    updateSendButtonState();
                    messageInput.focus();
                }
            }
        });

        // Tool panel toggle
        toolToggleBtn.addEventListener('click', (e) => { handleToolToggle(e); }); // Modified to anonymous function
        
        // Tool checkbox changes
        document.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox' && e.target.closest('.tool-checkboxes')) {
                handleToolSelectionChange();
            }
        });

        // Close tool panel when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.tool-selector')) {
                closeToolPanel();
            }
        });

        // Action buttons (placeholder functionality)
        attachBtn.addEventListener('click', () => {
            showToast('File attachment coming soon!', 'info');
        });

        micBtn.addEventListener('click', () => {
            showToast('Voice input coming soon!', 'info');
        });

        // LLM selection change
        llmSelect.addEventListener('change', handleLLMSelectionChange);

        // Download chat button
        downloadChatBtn.addEventListener('click', handleDownloadChat);
    }

    // Textarea auto-resize functionality
    function setupTextareaAutoResize() {
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
        });
    }

    // Handle keyboard events
    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    }

    // Handle input changes
    function handleInputChange() {
        updateCharacterCount();
        updateSendButtonState();
    }

    // Update character count display
    function updateCharacterCount() {
        const count = messageInput.value.length;
        charCount.textContent = count;
        
        if (count > 3500) {
            charCount.style.color = 'var(--accent-warning)';
        } else if (count > 3800) {
            charCount.style.color = 'var(--accent-error)';
        } else {
            charCount.style.color = 'var(--text-tertiary)';
        }
    }

    // Update send button state
    function updateSendButtonState() {
        const hasText = messageInput.value.trim().length > 0;
        const isNotTooLong = messageInput.value.length <= 4000;
        sendMessageBtn.disabled = !hasText || !isNotTooLong || isTyping;
    }

    // Handle tool panel toggle
    function handleToolToggle(e) {
        console.log('handleToolToggle called'); // Debug log
        e.stopPropagation();
        const isOpen = toolPanel.classList.contains('open');
        if (isOpen) {
            closeToolPanel();
        } else {
            openToolPanel();
        }
    }

    // Open tool panel
    function openToolPanel() {
        console.log('openToolPanel called'); // Debug log
        toolPanel.classList.add('open');
        toolToggleBtn.classList.add('open');
    }

    // Close tool panel
    function closeToolPanel() {
        console.log('closeToolPanel called'); // Debug log
        toolPanel.classList.remove('open');
        toolToggleBtn.classList.remove('open');
    }

    // Handle tool selection changes
    function handleToolSelectionChange() {
        const selectedTools = getSelectedTools();
        const count = selectedTools.length;
        
        if (count > 0) {
            showToast(`Selected ${count} tool${count > 1 ? 's' : ''}: ${selectedTools.join(', ')}`, 'info');
        } else {
            showToast('No tools selected', 'info');
        }
    }

    // Get selected tools
    function getSelectedTools() {
        const checkboxes = document.querySelectorAll('.tool-checkboxes input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    // Handle LLM selection change
    function handleLLMSelectionChange() {
        const selectedLLM = llmSelect.value;
        showToast(`Selected LLM: ${selectedLLM}`, 'info');
    }

    // Fetch available LLMs and populate dropdown
    async function fetchLLMs() {
        try {
            const response = await fetch('/api/llm_configs');
            if (response.ok) {
                const llmConfigs = await response.json();
                llmSelect.innerHTML = ''; // Clear existing options
                llmConfigs.forEach(llmConfig => {
                    const option = document.createElement('option');
                    option.value = llmConfig.name;
                    option.textContent = llmConfig.name;
                    llmSelect.appendChild(option);
                });
                // Optionally set a default or previously selected LLM
                if (llmConfigs.length > 0) {
                    llmSelect.value = llmConfigs[0].name; // Set first as default
                }
            } else {
                console.error('Failed to fetch LLMs');
                showToast('Failed to load LLM options', 'error');
            }
        } catch (error) {
            console.error('Error fetching LLMs:', error);
            showToast('Error loading LLM options', 'error');
        }
    }

    // Handle new chat creation
    function handleNewChat() {
        if (confirm('Start a new chat? This will clear the current conversation.')) {
            clearChat();
            createChatSession();
        }
    }

    // Handle download chat session
    function handleDownloadChat() {
        if (sessionId) {
            window.open(`/chat/${sessionId}/download`, '_blank');
        } else {
            showToast('No active session to download.', 'warning');
        }
    }

    // Clear chat messages
    function clearChat() {
        // Clear existing content
        chatMessages.innerHTML = '';
        
        // Create welcome message structure
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        
        // Welcome icon
        const iconDiv = document.createElement('div');
        iconDiv.className = 'welcome-icon';
        const robotIcon = document.createElement('i');
        robotIcon.className = 'fas fa-robot';
        iconDiv.appendChild(robotIcon);
        
        // Welcome title
        const title = document.createElement('h2');
        title.textContent = 'Welcome to MCP Tools Chat';
        
        // Welcome description
        const description = document.createElement('p');
        description.textContent = "I'm your AI assistant with access to various tools and data sources. How can I help you today?";
        
        // Suggested prompts container
        const promptsDiv = document.createElement('div');
        promptsDiv.className = 'suggested-prompts';
        
        // Create prompt buttons
        const prompts = [
            { text: 'Calculate 15% of 250', icon: 'fas fa-calculator' },
            { text: 'Look up user information', icon: 'fas fa-search' },
            { text: 'Execute a simple Python script', icon: 'fas fa-code' }
        ];
        
        prompts.forEach(prompt => {
            const button = document.createElement('button');
            button.className = 'prompt-suggestion';
            button.setAttribute('data-prompt', prompt.text);
            
            const icon = document.createElement('i');
            icon.className = prompt.icon;
            
            button.appendChild(icon);
            button.appendChild(document.createTextNode(prompt.text));
            promptsDiv.appendChild(button);
        });
        
        // Assemble welcome message
        welcomeDiv.appendChild(iconDiv);
        welcomeDiv.appendChild(title);
        welcomeDiv.appendChild(description);
        welcomeDiv.appendChild(promptsDiv);
        
        chatMessages.appendChild(welcomeDiv);
    }

    // Toast notification system
    function showToast(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        toast.classList.add('toast', type);
        
        // Create container div
        const container = document.createElement('div');
        container.style.display = 'flex';
        container.style.alignItems = 'center';
        container.style.gap = '8px';
        
        // Add icon based on type
        const icon = document.createElement('i');
        icon.className = getToastIcon(type);
        
        // Add message span
        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;
        
        container.appendChild(icon);
        container.appendChild(messageSpan);
        toast.appendChild(container);
        
        toastContainer.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 250);
        }, duration);
    }

    function getToastIcon(type) {
        switch (type) {
            case 'success': return 'fas fa-check-circle';
            case 'error': return 'fas fa-exclamation-circle';
            case 'warning': return 'fas fa-exclamation-triangle';
            default: return 'fas fa-info-circle';
        }
    }

    // Add message to chat
    function addMessage(content, sender, isStreaming = false) {
        // Remove welcome message if it exists
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        if (isStreaming) {
            messageContent.textContent = content;
            const cursor = document.createElement('span');
            cursor.className = 'typing-cursor';
            cursor.textContent = '|';
            messageContent.appendChild(cursor);
            currentStreamingMessage = messageContent;
        } else {
            messageContent.innerHTML = marked.parse(content);
            addCopyButtonsToCodeBlocks(messageContent);
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageContent;
    }

    // Update streaming message
    function updateStreamingMessage(content) {
        if (currentStreamingMessage) {
            // Clear existing content
            currentStreamingMessage.textContent = content;
            
            // Add typing cursor as a separate element
            const cursor = document.createElement('span');
            cursor.className = 'typing-cursor';
            cursor.textContent = '|';
            currentStreamingMessage.appendChild(cursor);
            
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Finish streaming message
    function finishStreamingMessage(content) {
        if (currentStreamingMessage) {
            currentStreamingMessage.innerHTML = marked.parse(content);
            addCopyButtonsToCodeBlocks(currentStreamingMessage);
            currentStreamingMessage = null;
        }
    }

    // Add copy buttons to code blocks
    function addCopyButtonsToCodeBlocks(element) {
        element.querySelectorAll('pre > code').forEach(codeBlock => {
            const pre = codeBlock.parentNode;
            const button = document.createElement('button');
            button.className = 'copy-code-btn';
            button.textContent = 'Copy';
            button.onclick = () => {
                navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                    showToast('Copied to clipboard!', 'success', 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    showToast('Failed to copy code', 'error');
                });
            };
            pre.style.position = 'relative'; // Ensure position for absolute button
            pre.appendChild(button);
        });
    }

    // WebSocket connection management
    function connectWebSocket(sId) {
        if (ws) {
            ws.close();
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${sId}`;
        
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            isConnected = true;
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Connected';
            showToast('Connected to chat server', 'success');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.log('WebSocket message (text):', event.data);
            }
        };

        ws.onclose = (event) => {
            isConnected = false;
            statusIndicator.classList.remove('connected');
            statusText.textContent = 'Disconnected';
            
            if (event.code !== 1000) { // Not a normal closure
                showToast('Connection lost. Attempting to reconnect...', 'warning');
                setTimeout(() => {
                    if (sessionId) {
                        connectWebSocket(sessionId);
                    }
                }, 3000);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            showToast('Connection error occurred', 'error');
        };
    }

    // Handle WebSocket messages
    function handleWebSocketMessage(data) {
        switch (data.type) {
            case 'status':
                showToast(data.message, 'info');
                break;
            case 'thinking':
                showToast('AI is thinking...', 'info', 2000);
                break;
            case 'tool_call':
                showToast(`Using tool: ${data.tool_name}`, 'info');
                break;
            case 'error':
                showToast(data.message, 'error');
                break;
            default:
                console.log('Unknown WebSocket message type:', data);
        }
    }

    // Create new chat session
    async function createChatSession() {
        try {
            showLoading(true);
            statusText.textContent = 'Creating session...';
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-EMAIL-USER': 'test@example.com' // This should be replaced with actual auth
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                sessionId = data.session_id;
                showToast(`New session created`, 'success');
                connectWebSocket(sessionId);
            } else {
                throw new Error(data.detail || 'Failed to create session');
            }
        } catch (error) {
            console.error('Error creating chat session:', error);
            showToast(`Failed to create session: ${error.message}`, 'error');
            statusText.textContent = 'Connection failed';
        } finally {
            showLoading(false);
        }
    }

    // Send message handler
    async function handleSendMessage() {
        const message = messageInput.value.trim();
        if (!message || isTyping) return;

        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input and reset
        messageInput.value = '';
        messageInput.style.height = 'auto';
        updateCharacterCount();
        updateSendButtonState();

        // Check session
        if (!sessionId) {
            showToast('No active session. Creating one...', 'info');
            await createChatSession();
            if (!sessionId) {
                showToast('Could not create session. Message not sent.', 'error');
                return;
            }
        }

        try {
            isTyping = true;
            updateSendButtonState();
            
            const selectedTools = getSelectedTools();
            const requestBody = { 
                content: message,
                tools: selectedTools,
                llm_name: llmSelect.value
            };

            const response = await fetch(`/chat/${sessionId}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-EMAIL-USER': 'test@example.com' // This should be replaced with actual auth
                },
                body: JSON.stringify(requestBody)
            });

            if (response.ok) {
                await handleStreamingResponse(response);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            showToast(`Error: ${error.message}`, 'error');
            addMessage('Sorry, I encountered an error processing your message. Please try again.', 'assistant');
        } finally {
            isTyping = false;
            updateSendButtonState();
        }
    }

    // Handle streaming response
    async function handleStreamingResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botResponse = '';
        let messageElement = null;

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                botResponse += chunk;

                // Create or update the message element
                if (!messageElement) {
                    messageElement = addMessage(botResponse, 'assistant', true);
                } else {
                    updateStreamingMessage(botResponse);
                }
            }

            // Finish streaming
            if (messageElement) {
                finishStreamingMessage(botResponse);
            }
        } catch (error) {
            console.error('Error reading stream:', error);
            if (messageElement) {
                finishStreamingMessage(botResponse || 'Error receiving response');
            }
        }
    }

    // Loading overlay control
    function showLoading(show) {
        if (show) {
            loadingOverlay.classList.add('show');
        } else {
            loadingOverlay.classList.remove('show');
        }
    }

    // Fetch application settings
    async function fetchAppSettings() {
        const appName = window.appConfig.appName || 'Chat App';
        if (appTitle) appTitle.textContent = appName;
        if (sidebarAppName) sidebarAppName.textContent = appName;
        if (headerAppName) headerAppName.textContent = appName;
        if (welcomeTitle) welcomeTitle.textContent = `Welcome to ${appName} Chat`;
    }

    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && sessionId && !isConnected) {
            connectWebSocket(sessionId);
        }
    });

    // Handle window beforeunload
    window.addEventListener('beforeunload', () => {
        if (ws) {
            ws.close(1000, 'Page unloading');
        }
    });
});
