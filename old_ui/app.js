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
    const loadingOverlay = document.getElementById('loadingOverlay');
    const attachBtn = document.getElementById('attachBtn');
    const toolToggleBtn = document.getElementById('toolToggleBtn');
    const toolPanel = document.getElementById('toolPanel');
    const appTitle = document.getElementById('appTitle');
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

    // Debug Panel Initialization
    const debugPanel = document.getElementById('debug-panel');
    const debugContent = document.getElementById('debug-content');
    const originalConsoleLog = console.log;

    console.log = function(...args) {
        originalConsoleLog.apply(console, args);
        if (debugContent) {
            debugContent.value += `[LOG] ${args.join(' ')}\n`;
            debugContent.scrollTop = debugContent.scrollHeight;
        }
    };

    console.error = function(...args) {
        originalConsoleLog.apply(console, args);
        if (debugContent) {
            debugContent.value += `[ERROR] ${args.join(' ')}\n`;
            debugContent.scrollTop = debugContent.scrollHeight;
        }
    };

    console.warn = function(...args) {
        originalConsoleLog.apply(console, args);
        if (debugContent) {
            debugContent.value += `[WARN] ${args.join(' ')}\n`;
            debugContent.scrollTop = debugContent.scrollHeight;
        }
    };

    async function init() {
        console.log('init(): Application initialization started.');
        setupEventListeners();
        setupTextareaAutoResize();
        await fetchAppSettings();
        await fetchLLMs();
        console.log('init(): Connecting WebSocket immediately...');
        connectWebSocket(); // Connect WebSocket immediately
        updateSendButtonState();
        console.log('init(): Application initialization finished.');
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
            const isClickOnToolArea = e.target.closest('.tool-selector') || 
                                     e.target.closest('#tool-toggle-btn') ||
                                     e.target === toolToggleBtn;
            
            if (!isClickOnToolArea && toolPanel.classList.contains('open')) {
                closeToolPanel();
            }
        });

        // Action buttons (placeholder functionality)
        attachBtn.addEventListener('click', () => {
            showToast('File attachment coming soon!', 'info');
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
        updateSendButtonState();
    }

    // Update send button state
    function updateSendButtonState() {
        const hasText = messageInput.value.trim().length > 0;
        const isNotTooLong = messageInput.value.length <= 4000;
        sendMessageBtn.disabled = !hasText || !isNotTooLong || isTyping;
    }

    // Handle tool panel toggle
    function handleToolToggle(e) {
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
        toolPanel.classList.add('open');
        toolToggleBtn.classList.add('open');
    }

    // Close tool panel
    function closeToolPanel() {
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
                
                // Add default placeholder option
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = 'Select AI Model';
                defaultOption.disabled = true;
                llmSelect.appendChild(defaultOption);
                
                llmConfigs.forEach(llmConfig => {
                    const option = document.createElement('option');
                    option.value = llmConfig.name;
                    option.textContent = llmConfig.name;
                    llmSelect.appendChild(option);
                });
                
                // Set first LLM as default if available
                if (llmConfigs.length > 0) {
                    llmSelect.value = llmConfigs[0].name;
                    showToast(`Selected AI Model: ${llmConfigs[0].name}`, 'info', 2000);
                } else {
                    llmSelect.value = '';
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
        // Reset session state first
        sessionId = null;
        
        // Clear the UI
        clearChat();
        
        // Create new session
        createChatSession();
        showToast('Starting new chat session...', 'info');
    }

    // Handle download chat session
    function handleDownloadChat() {
        if (sessionId) {
            window.open(`/chat/${sessionId}/download`, '_blank');
        }
        else {
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
    function connectWebSocket() {
        console.log(`connectWebSocket(): Attempting to connect WebSocket.`);
        if (ws) {
            console.log('connectWebSocket(): Existing WebSocket found, closing it.');
            ws.close();
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`; // Connect to generic /ws initially
        console.log(`connectWebSocket(): WebSocket URL: ${wsUrl}`);
        
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            isConnected = true;
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Connected';
            showToast('Connected to chat server', 'success');
            console.log('connectWebSocket(): WebSocket connection opened.');
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
            console.log(`connectWebSocket(): WebSocket connection closed. Code: ${event.code}, Reason: ${event.reason}`);
            
            if (event.code !== 1000) { // Not a normal closure
                console.log('connectWebSocket(): Abnormal closure, attempting to reconnect in 3 seconds...');
                showToast('Connection lost. Attempting to reconnect...', 'warning');
                setTimeout(() => {
                    connectWebSocket(); // Reconnect without session ID
                }, 3000);
            }
        };

        ws.onerror = (error) => {
            console.error('connectWebSocket(): WebSocket error:', error);
            showToast('Connection error occurred', 'error');
        };
    }

    // Handle WebSocket messages
    function handleWebSocketMessage(data) {
        switch (data.type) {
            case 'session_id':
                sessionId = data.session_id;
                console.log(`WebSocket received session_id: ${sessionId}`);
                showToast(`Session ID received: ${sessionId}`, 'success');
                break;
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
        console.log('createChatSession(): Attempting to create new chat session.');
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
                console.log(`createChatSession(): Session created successfully. Session ID: ${sessionId}`);
                statusText.textContent = 'Connected';
                showToast(`New session created`, 'success');
                // Send session_id to backend via WebSocket if connected
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'session_init', session_id: sessionId }));
                }
            } else {
                console.error(`createChatSession(): Failed to create session. Status: ${response.status}, Detail: ${data.detail}`);
                throw new Error(data.detail || 'Failed to create session');
            }
        } catch (error) {
            console.error('createChatSession(): Error creating chat session:', error);
            showToast(`Failed to create session: ${error.message}`, 'error');
            statusText.textContent = 'Connection failed';
        } finally {
            showLoading(false);
            console.log('createChatSession(): Finished session creation attempt.');
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
