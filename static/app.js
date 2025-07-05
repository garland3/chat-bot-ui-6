// Application State
class AppState {
    constructor() {
        this.ws = null;
        this.sessionId = null;
        this.isConnected = false;
        this.isTyping = false;
        this.currentStreamingMessage = null;
        this.selectedTools = new Set();
        this.selectedDataSources = new Set();
        this.availableDataSources = [];
        this.selectedLLM = null;
        this.availableLLMs = [];
        this.userEmail = null;
        this.messageHistory = [];
        this.debugMode = window.appConfig?.enableDebug || false;
    }
}

// Global state instance
const appState = new AppState();

// DOM Elements
const elements = {
    // Header elements
    connectionStatus: document.getElementById('connectionStatus'),
    statusIndicator: document.getElementById('statusIndicator'),
    statusText: document.getElementById('statusText'),
    newChatBtn: document.getElementById('newChatBtn'),
    toolsDropdown: document.getElementById('toolsDropdown'),
    toolsBtn: document.getElementById('toolsBtn'),
    toolsMenu: document.getElementById('toolsMenu'),
    toolsCount: document.getElementById('toolsCount'),
    dataSourcesDropdown: document.getElementById('dataSourcesDropdown'),
    dataSourcesBtn: document.getElementById('dataSourcesBtn'),
    dataSourcesMenu: document.getElementById('dataSourcesMenu'),
    dataSourcesCount: document.getElementById('dataSourcesCount'),
    llmDropdown: document.getElementById('llmDropdown'),
    llmBtn: document.getElementById('llmBtn'),
    llmMenu: document.getElementById('llmMenu'),
    selectedModel: document.getElementById('selectedModel'),
    downloadBtn: document.getElementById('downloadBtn'),
    userInfo: document.getElementById('userInfo'),
    userEmail: document.getElementById('userEmail'),
    
    // Chat elements
    chatContainer: document.getElementById('chatContainer'),
    welcomeScreen: document.getElementById('welcomeScreen'),
    messagesContainer: document.getElementById('messagesContainer'),
    
    // Input elements
    messageInput: document.getElementById('messageInput'),
    attachBtn: document.getElementById('attachBtn'),
    sendBtn: document.getElementById('sendBtn'),
    typingIndicator: document.getElementById('typingIndicator'),
    
    // UI elements
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer')
};

// Utility Functions
const utils = {
    formatTime: (date = new Date()) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    escapeHtml: (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    generateId: () => {
        return Math.random().toString(36).substr(2, 9);
    },
    
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            showToast('Copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            showToast('Failed to copy text', 'error');
        }
    }
};

// Toast Notification System
function showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const toastId = utils.generateId();
    toast.innerHTML = `
        <div class="toast-header">
            <span class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</span>
            <button class="toast-close" onclick="removeToast('${toastId}')">&times;</button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    toast.id = toastId;
    elements.toastContainer.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove
    setTimeout(() => removeToast(toastId), duration);
}

function removeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 250);
    }
}

// Debug Functions
function updateDebugInfo() {
    // Debug info now only in console
    if (!appState.debugMode) return;
    
    console.log('Debug Info:', {
        connected: appState.isConnected,
        sessionId: appState.sessionId,
        wsReadyState: appState.ws?.readyState,
        selectedTools: Array.from(appState.selectedTools),
        selectedDataSources: Array.from(appState.selectedDataSources),
        selectedLLM: appState.selectedLLM,
        messageCount: appState.messageHistory.length
    });
}

function debugThemeColors() {
    if (!appState.debugMode) return;
    
    const root = document.documentElement;
    const computedStyle = getComputedStyle(root);
    
    console.log('=== THEME DEBUG INFO ===');
    console.log('Applied CSS Custom Properties (via style.setProperty):');
    const appliedProps = {
        '--bg-primary': root.style.getPropertyValue('--bg-primary'),
        '--bg-secondary': root.style.getPropertyValue('--bg-secondary'),
        '--bg-tertiary': root.style.getPropertyValue('--bg-tertiary'),
        '--bg-hover': root.style.getPropertyValue('--bg-hover'),
        '--bg-active': root.style.getPropertyValue('--bg-active'),
        '--accent-primary': root.style.getPropertyValue('--accent-primary'),
        '--accent-secondary': root.style.getPropertyValue('--accent-secondary'),
        '--text-primary': root.style.getPropertyValue('--text-primary'),
        '--text-secondary': root.style.getPropertyValue('--text-secondary'),
        '--text-muted': root.style.getPropertyValue('--text-muted'),
        '--text-accent': root.style.getPropertyValue('--text-accent'),
        '--border-color': root.style.getPropertyValue('--border-color')
    };
    Object.entries(appliedProps).forEach(([prop, value]) => {
        console.log(`  ${prop}: ${value || 'NOT SET'}`);
    });
    
    console.log('Computed CSS Values (what browser actually uses):');
    const computedProps = {
        '--bg-primary': computedStyle.getPropertyValue('--bg-primary').trim(),
        '--bg-secondary': computedStyle.getPropertyValue('--bg-secondary').trim(),
        '--bg-tertiary': computedStyle.getPropertyValue('--bg-tertiary').trim(),
        '--bg-hover': computedStyle.getPropertyValue('--bg-hover').trim(),
        '--bg-active': computedStyle.getPropertyValue('--bg-active').trim(),
        '--accent-primary': computedStyle.getPropertyValue('--accent-primary').trim(),
        '--accent-secondary': computedStyle.getPropertyValue('--accent-secondary').trim(),
        '--text-primary': computedStyle.getPropertyValue('--text-primary').trim(),
        '--text-secondary': computedStyle.getPropertyValue('--text-secondary').trim(),
        '--text-muted': computedStyle.getPropertyValue('--text-muted').trim(),
        '--text-accent': computedStyle.getPropertyValue('--text-accent').trim(),
        '--border-color': computedStyle.getPropertyValue('--border-color').trim()
    };
    Object.entries(computedProps).forEach(([prop, value]) => {
        console.log(`  ${prop}: ${value || 'NOT FOUND'}`);
    });
    console.log('========================');
}

// Connection Management
function initializeWebSocket() {
    const wsUrl = window.appConfig.wsUrl;
    
    try {
        appState.ws = new WebSocket(wsUrl);
        
        appState.ws.onopen = () => {
            console.log('WebSocket connected');
            appState.isConnected = true;
            updateConnectionStatus();
            updateDebugInfo();
        };
        
        appState.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        appState.ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            appState.isConnected = false;
            updateConnectionStatus();
            updateDebugInfo();
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                if (!appState.isConnected) {
                    console.log('Attempting to reconnect...');
                    initializeWebSocket();
                }
            }, 3000);
        };
        
        appState.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            showToast('Connection error occurred', 'error');
        };
        
    } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
        showToast('Failed to connect to server', 'error');
    }
}

function handleWebSocketMessage(data) {
    if (appState.debugMode) {
        console.log('WebSocket message received:', data);
    }
    
    switch (data.type) {
        case 'session_id':
            appState.sessionId = data.session_id;
            elements.downloadBtn.disabled = false;
            updateDebugInfo();
            break;
            
        case 'status':
            handleStatusMessage(data);
            break;
            
        case 'thinking':
            handleThinkingMessage(data);
            break;
            
        case 'tool_call':
            handleToolCallMessage(data);
            break;
            
        case 'message_start':
            handleMessageStart(data);
            break;
            
        case 'message_chunk':
            handleMessageChunk(data);
            break;
            
        case 'message_complete':
            handleMessageComplete(data);
            break;
            
        case 'error':
            handleErrorMessage(data);
            break;
            
        default:
            console.log('Unknown message type:', data.type);
    }
}

function handleStatusMessage(data) {
    if (data.status === 'typing') {
        setTypingIndicator(true);
    } else if (data.status === 'complete') {
        setTypingIndicator(false);
    }
}

function handleThinkingMessage(data) {
    // Show thinking indicator or update existing one
    showToast(`AI is thinking: ${data.message}`, 'info', 3000);
}

function handleToolCallMessage(data) {
    // Add tool call indicator to the current streaming message
    if (appState.currentStreamingMessage) {
        addToolCallToMessage(appState.currentStreamingMessage, data);
    }
}

function handleMessageStart(data) {
    const messageElement = createMessageElement('assistant', '', true);
    elements.messagesContainer.appendChild(messageElement);
    appState.currentStreamingMessage = messageElement;
    hideWelcomeScreen();
    scrollToBottom();
}

function handleMessageChunk(data) {
    if (appState.currentStreamingMessage) {
        const bubble = appState.currentStreamingMessage.querySelector('.message-bubble');
        const currentContent = bubble.textContent || '';
        bubble.textContent = currentContent + (data.content || '');
        scrollToBottom();
    }
}

function handleMessageComplete(data) {
    if (appState.currentStreamingMessage) {
        const bubble = appState.currentStreamingMessage.querySelector('.message-bubble');
        
        // Convert markdown to HTML
        if (data.content) {
            bubble.innerHTML = marked.parse(data.content);
            addCopyButtonsToCodeBlocks(bubble);
        }
        
        // Remove streaming class
        appState.currentStreamingMessage.classList.remove('streaming');
        appState.currentStreamingMessage = null;
        
        // Add to message history
        appState.messageHistory.push({
            role: 'assistant',
            content: data.content,
            timestamp: new Date()
        });
    }
    
    setTypingIndicator(false);
    enableInput();
    scrollToBottom();
}

function handleErrorMessage(data) {
    showToast(data.message || 'An error occurred', 'error');
    setTypingIndicator(false);
    enableInput();
    
    if (appState.currentStreamingMessage) {
        const bubble = appState.currentStreamingMessage.querySelector('.message-bubble');
        bubble.innerHTML = '<em>Sorry, an error occurred while processing your message.</em>';
        appState.currentStreamingMessage.classList.remove('streaming');
        appState.currentStreamingMessage = null;
    }
}

function updateConnectionStatus() {
    if (appState.isConnected) {
        elements.statusIndicator.className = 'status-indicator connected';
        elements.statusText.textContent = 'Connected';
    } else {
        elements.statusIndicator.className = 'status-indicator disconnected';
        elements.statusText.textContent = 'Disconnected';
    }
}

// Session Management
async function createNewSession() {
    try {
        showLoading(true);
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        appState.sessionId = data.session_id;
        
        // Clear chat
        clearChat();
        elements.downloadBtn.disabled = false;
        
        showToast('New chat session started', 'success');
        
    } catch (error) {
        console.error('Error creating new session:', error);
        showToast('Failed to create new session', 'error');
    } finally {
        showLoading(false);
    }
}

// Message Handling
async function sendMessage(content) {
    if (!content.trim() || !appState.sessionId) return;
    
    try {
        disableInput();
        
        // Add user message to UI
        const userMessage = createMessageElement('user', content);
        elements.messagesContainer.appendChild(userMessage);
        appState.messageHistory.push({
            role: 'user',
            content: content,
            timestamp: new Date()
        });
        
        hideWelcomeScreen();
        scrollToBottom();
        
        // Send message to backend
        const response = await fetch(`/chat/${appState.sessionId}/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: content,
                tools: Array.from(appState.selectedTools),
                data_sources: Array.from(appState.selectedDataSources),
                llm_config: appState.selectedLLM
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Response will come through WebSocket
        setTypingIndicator(true);
        
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('Failed to send message', 'error');
        enableInput();
    }
}

function createMessageElement(role, content, isStreaming = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}${isStreaming ? ' streaming' : ''}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'AI';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    if (content) {
        if (role === 'assistant') {
            bubble.innerHTML = marked.parse(content);
            addCopyButtonsToCodeBlocks(bubble);
        } else {
            bubble.textContent = content;
        }
    }
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = utils.formatTime();
    
    contentDiv.appendChild(bubble);
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    return messageDiv;
}

function addCopyButtonsToCodeBlocks(container) {
    const codeBlocks = container.querySelectorAll('pre code');
    codeBlocks.forEach(codeBlock => {
        const pre = codeBlock.parentElement;
        if (pre.querySelector('.code-copy-btn')) return; // Already has button
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'code-copy-btn';
        copyBtn.textContent = 'Copy';
        copyBtn.onclick = () => utils.copyToClipboard(codeBlock.textContent);
        
        pre.style.position = 'relative';
        pre.appendChild(copyBtn);
    });
}

function addToolCallToMessage(messageElement, toolData) {
    const contentDiv = messageElement.querySelector('.message-content');
    const bubble = contentDiv.querySelector('.message-bubble');
    
    const toolCall = document.createElement('div');
    toolCall.className = 'tool-call';
    toolCall.innerHTML = `
        <div class="tool-call-header">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
            Using ${toolData.tool_name}
        </div>
        <div class="tool-call-content">${utils.escapeHtml(JSON.stringify(toolData.arguments, null, 2))}</div>
    `;
    
    contentDiv.insertBefore(toolCall, bubble);
}

function setTypingIndicator(show) {
    appState.isTyping = show;
    elements.typingIndicator.style.display = show ? 'block' : 'none';
}

function hideWelcomeScreen() {
    elements.welcomeScreen.style.display = 'none';
}

function clearChat() {
    elements.messagesContainer.innerHTML = '';
    elements.welcomeScreen.style.display = 'flex';
    appState.messageHistory = [];
    appState.currentStreamingMessage = null;
    setTypingIndicator(false);
}

function scrollToBottom() {
    elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
}

// Input Management
function enableInput() {
    elements.messageInput.disabled = false;
    elements.sendBtn.disabled = elements.messageInput.value.trim() === '';
    elements.messageInput.focus();
}

function disableInput() {
    elements.messageInput.disabled = true;
    elements.sendBtn.disabled = true;
}


function autoResizeTextarea() {
    const textarea = elements.messageInput;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}





async function loadLLMConfigs() {
    try {
        console.log('Loading LLM configs from /api/llm_configs...');
        const response = await fetch('/api/llm_configs');
        console.log('LLM configs response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('LLM configs data received:', data);
        
        // Handle different possible response structures
        if (Array.isArray(data)) {
            appState.availableLLMs = data;
        } else if (data.llms && Array.isArray(data.llms)) {
            appState.availableLLMs = data.llms;
        } else {
            console.error('Unexpected LLM config response structure:', data);
            appState.availableLLMs = [];
        }
        
        console.log('Available LLMs:', appState.availableLLMs);
        
        // Set default LLM if none selected
        if (appState.availableLLMs.length > 0 && !appState.selectedLLM) {
            appState.selectedLLM = appState.availableLLMs[0];
            console.log('Selected default LLM:', appState.selectedLLM);
        }
        
        updateLLMDisplay();
        
    } catch (error) {
        console.error('Error loading LLM configs:', error);
        showToast('Failed to load AI models', 'error');
        elements.selectedModel.textContent = 'Error loading models';
    }
}

function updateLLMDisplay() {
    // Update selected model display
    if (appState.selectedLLM) {
        elements.selectedModel.textContent = appState.selectedLLM.name;
    } else {
        elements.selectedModel.textContent = 'No model selected';
    }
    
    // Update dropdown menu
    elements.llmMenu.innerHTML = '<div class="dropdown-header">Select AI Model</div>';
    
    appState.availableLLMs.forEach(llm => {
        const item = document.createElement('div');
        item.className = `radio-item${appState.selectedLLM?.name === llm.name ? ' selected' : ''}`;
        item.textContent = llm.name;
        item.onclick = () => selectLLM(llm);
        elements.llmMenu.appendChild(item);
    });
}

function selectLLM(llm) {
    appState.selectedLLM = llm;
    updateLLMDisplay();
    closeDropdown(elements.llmDropdown);
    updateDebugInfo();
}

// User Info
async function loadUserInfo() {
    try {
        // User info comes from backend authentication
        // For now, we'll use a placeholder
        appState.userEmail = 'user@example.com';
        elements.userEmail.textContent = appState.userEmail;
    } catch (error) {
        console.error('Error loading user info:', error);
        elements.userEmail.textContent = 'Unknown user';
    }
}

// Download Chat
async function downloadChat() {
    if (!appState.sessionId) {
        showToast('No active session to download', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/chat/${appState.sessionId}/download`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-${appState.sessionId}-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showToast('Chat downloaded successfully', 'success');
        
    } catch (error) {
        console.error('Error downloading chat:', error);
        showToast('Failed to download chat', 'error');
    }
}

// UI Utilities
function showLoading(show) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

function toggleDropdown(dropdown) {
    const isActive = dropdown.classList.contains('active');
    
    // Close all dropdowns
    document.querySelectorAll('.dropdown.active').forEach(d => {
        d.classList.remove('active');
    });
    
    // Toggle current dropdown
    if (!isActive) {
        dropdown.classList.add('active');
    }
}

function closeDropdown(dropdown) {
    dropdown.classList.remove('active');
}

function closeAllDropdowns() {
    document.querySelectorAll('.dropdown.active').forEach(d => {
        d.classList.remove('active');
    });
}

// Event Listeners
function setupEventListeners() {
    // Header controls
    elements.newChatBtn.addEventListener('click', createNewSession);
    elements.downloadBtn.addEventListener('click', downloadChat);
    
    // Dropdown toggles
    elements.toolsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleDropdown(elements.toolsDropdown);
    });
    
    elements.llmBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleDropdown(elements.llmDropdown);
    });

    elements.dataSourcesBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleDropdown(elements.dataSourcesDropdown);
    });
    
    // Tool selection
    elements.toolsMenu.addEventListener('click', (e) => {
        if (e.target.type === 'checkbox') {
            toggleTool(e.target.value);
        }
        e.stopPropagation();
    });

    elements.dataSourcesMenu.addEventListener('click', (e) => {
        if (e.target.type === 'checkbox') {
            toggleDataSource(e.target.value);
        }
        e.stopPropagation();
    });
    
    // Message input
    elements.messageInput.addEventListener('input', () => {
        autoResizeTextarea();
        elements.sendBtn.disabled = elements.messageInput.value.trim() === '' || elements.messageInput.disabled;
    });
    
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!elements.sendBtn.disabled) {
                const content = elements.messageInput.value.trim();
                elements.messageInput.value = '';
                autoResizeTextarea();
                sendMessage(content);
            }
        }
    });
    
    elements.sendBtn.addEventListener('click', () => {
        const content = elements.messageInput.value.trim();
        elements.messageInput.value = '';
        autoResizeTextarea();
        sendMessage(content);
    });
    
    // Suggested prompts
    elements.welcomeScreen.addEventListener('click', (e) => {
        if (e.target.classList.contains('prompt-suggestion')) {
            const prompt = e.target.dataset.prompt;
            elements.messageInput.value = prompt;
            autoResizeTextarea();
            elements.messageInput.focus();
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', closeAllDropdowns);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter for new chat
        if (e.ctrlKey && e.key === 'Enter') {
            createNewSession();
        }
        
        // Escape to close dropdowns
        if (e.key === 'Escape') {
            closeAllDropdowns();
        }
    });
}

// Theme Management
async function loadThemeConfig() {
    try {
        console.log('Loading theme config from /api/theme/config...');
        const response = await fetch('/api/theme/config');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const themeConfig = await response.json();
        console.log('Theme config received:', themeConfig);
        
        // Apply theme configuration to document title and app name
        if (themeConfig.app_name) {
            document.title = themeConfig.app_name;
            const appTitle = document.querySelector('.app-title');
            if (appTitle) {
                appTitle.textContent = themeConfig.app_name;
            }
            const welcomeTitle = document.querySelector('.welcome-content h2');
            if (welcomeTitle) {
                welcomeTitle.textContent = `Welcome to ${themeConfig.app_name}`;
            }
        }
        
        // Apply color configuration to CSS custom properties
        const root = document.documentElement;
        if (themeConfig.background_color) {
            root.style.setProperty('--bg-primary', themeConfig.background_color);
        }
        if (themeConfig.accent_primary) {
            root.style.setProperty('--accent-primary', themeConfig.accent_primary);
            root.style.setProperty('--text-accent', themeConfig.accent_primary);
        }
        if (themeConfig.accent_secondary) {
            root.style.setProperty('--accent-secondary', themeConfig.accent_secondary);
        }
        if (themeConfig.bg_secondary) {
            root.style.setProperty('--bg-secondary', themeConfig.bg_secondary);
        }
        if (themeConfig.bg_tertiary) {
            root.style.setProperty('--bg-tertiary', themeConfig.bg_tertiary);
        }
        if (themeConfig.bg_hover) {
            root.style.setProperty('--bg-hover', themeConfig.bg_hover);
        }
        if (themeConfig.bg_active) {
            root.style.setProperty('--bg-active', themeConfig.bg_active);
        }
        if (themeConfig.text_primary) {
            root.style.setProperty('--text-primary', themeConfig.text_primary);
        }
        if (themeConfig.text_secondary) {
            root.style.setProperty('--text-secondary', themeConfig.text_secondary);
        }
        if (themeConfig.text_muted) {
            root.style.setProperty('--text-muted', themeConfig.text_muted);
        }
        if (themeConfig.border_color) {
            root.style.setProperty('--border-color', themeConfig.border_color);
        }
        
        console.log('Theme configuration applied successfully');
        
        // Debug theme colors after applying them
        if (appState.debugMode) {
            debugThemeColors();
        }
        
    } catch (error) {
        console.error('Error loading theme config:', error);
        showToast('Failed to load theme configuration', 'error');
    }
}

// Initialization
async function initialize() {
    console.log('Initializing Galaxy Chat...');
    
    try {
        // Setup event listeners
        setupEventListeners();
        
        // Initialize WebSocket connection
        initializeWebSocket();
        
        // Load initial data
        await Promise.all([
            loadThemeConfig(),
            loadLLMConfigs(),
            loadDataSources(),
            loadUserInfo()
        ]);
        
        // Debug theme colors after loading
        debugThemeColors();
        
        // Create initial session
        await createNewSession();
        
        // Initialize UI state
        updateToolsDisplay();
        enableInput();
        
        console.log('Galaxy Chat initialized successfully');
        
    } catch (error) {
        console.error('Error initializing application:', error);
        showToast('Failed to initialize application', 'error');
    }
}

// Start the application when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (appState.debugMode) {
        showToast(`Error: ${event.error.message}`, 'error');
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && !appState.isConnected) {
        console.log('Page became visible, attempting to reconnect...');
        initializeWebSocket();
    }
});

// Export for debugging
if (appState.debugMode) {
    window.appState = appState;
    window.appUtils = utils;
}
