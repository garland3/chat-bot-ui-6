import { utils } from '../utils/utils.js';
import { appState } from '../state/AppState.js';

export class ChatManager {
    constructor() {
        this.elements = this.initElements();
        this.setupEventListeners();
        
        // Listen to state changes
        appState.addListener('typing', (isTyping) => this.setTypingIndicator(isTyping));
    }

    initElements() {
        return {
            chatContainer: document.getElementById('chatContainer'),
            welcomeScreen: document.getElementById('welcomeScreen'),
            messagesContainer: document.getElementById('messagesContainer'),
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            typingIndicator: document.getElementById('typingIndicator')
        };
    }

    setupEventListeners() {
        // Message input handling
        this.elements.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.elements.sendBtn.disabled = 
                this.elements.messageInput.value.trim() === '' || 
                this.elements.messageInput.disabled;
        });
        
        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!this.elements.sendBtn.disabled) {
                    this.sendMessage();
                }
            }
        });
        
        this.elements.sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Suggested prompts
        this.elements.welcomeScreen.addEventListener('click', (e) => {
            if (e.target.classList.contains('prompt-suggestion')) {
                const prompt = e.target.dataset.prompt;
                this.elements.messageInput.value = prompt;
                this.autoResizeTextarea();
                this.elements.messageInput.focus();
            }
        });
    }

    async sendMessage() {
        const content = this.elements.messageInput.value.trim();
        if (!content || !appState.sessionId) return;

        try {
            this.disableInput();
            
            // Clear input
            this.elements.messageInput.value = '';
            this.autoResizeTextarea();
            
            // Add user message to UI
            const userMessage = this.createMessageElement('user', content);
            this.elements.messagesContainer.appendChild(userMessage);
            appState.addMessage({
                role: 'user',
                content: content,
                timestamp: new Date()
            });
            
            this.hideWelcomeScreen();
            this.scrollToBottom();
            
            // Send message via API service
            const { apiService } = await import('../services/ApiService.js');
            
            // Validate required data
            if (!appState.selectedLLM) {
                console.error('Chat: No LLM selected, cannot send message');
                const { showToast } = await import('../components/Toast.js');
                showToast('Please select an AI model first', 'error');
                this.enableInput();
                return;
            }
            
            console.log('Chat: Sending message with data:', {
                sessionId: appState.sessionId,
                content: content,
                selectedTools: Array.from(appState.selectedTools),
                selectedDataSources: Array.from(appState.selectedDataSources),
                selectedLLM: appState.selectedLLM
            });
            
            await apiService.sendMessage(
                appState.sessionId,
                content,
                appState.selectedTools,
                appState.selectedDataSources,
                appState.selectedLLM
            );
            
            // Response will come through WebSocket
            appState.setTyping(true);
            
        } catch (error) {
            console.error('Error sending message:', error);
            const { showToast } = await import('../components/Toast.js');
            showToast('Failed to send message', 'error');
            this.enableInput();
        }
    }

    createMessageElement(role, content, isStreaming = false) {
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
                this.addCopyButtonsToCodeBlocks(bubble);
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

    addCopyButtonsToCodeBlocks(container) {
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

    addToolCallToMessage(messageElement, toolData) {
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

    setTypingIndicator(show) {
        this.elements.typingIndicator.style.display = show ? 'block' : 'none';
    }

    hideWelcomeScreen() {
        this.elements.welcomeScreen.style.display = 'none';
    }

    clearChat() {
        this.elements.messagesContainer.innerHTML = '';
        this.elements.welcomeScreen.style.display = 'flex';
        appState.messageHistory = [];
        appState.currentStreamingMessage = null;
        this.setTypingIndicator(false);
    }

    scrollToBottom() {
        this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
    }

    enableInput() {
        this.elements.messageInput.disabled = false;
        this.elements.sendBtn.disabled = this.elements.messageInput.value.trim() === '';
        this.elements.messageInput.focus();
    }

    disableInput() {
        this.elements.messageInput.disabled = true;
        this.elements.sendBtn.disabled = true;
    }

    autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }

    // Handle streaming messages
    handleMessageStart() {
        const messageElement = this.createMessageElement('assistant', '', true);
        this.elements.messagesContainer.appendChild(messageElement);
        appState.currentStreamingMessage = messageElement;
        this.hideWelcomeScreen();
        this.scrollToBottom();
        return messageElement;
    }

    handleMessageChunk(content) {
        if (appState.currentStreamingMessage) {
            const bubble = appState.currentStreamingMessage.querySelector('.message-bubble');
            const currentContent = bubble.textContent || '';
            bubble.textContent = currentContent + (content || '');
            this.scrollToBottom();
        }
    }

    handleMessageComplete(content) {
        if (appState.currentStreamingMessage) {
            const bubble = appState.currentStreamingMessage.querySelector('.message-bubble');
            
            // Convert markdown to HTML
            if (content) {
                bubble.innerHTML = marked.parse(content);
                this.addCopyButtonsToCodeBlocks(bubble);
            }
            
            // Remove streaming class
            appState.currentStreamingMessage.classList.remove('streaming');
            appState.currentStreamingMessage = null;
            
            // Add to message history
            appState.addMessage({
                role: 'assistant',
                content: content,
                timestamp: new Date()
            });
        }
        
        appState.setTyping(false);
        this.enableInput();
        this.scrollToBottom();
    }
}

// Global instance
export const chatManager = new ChatManager();
