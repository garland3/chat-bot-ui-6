import { appState } from '../state/AppState.js';
import { showToast } from '../components/Toast.js';

export class WebSocketService {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.messageHandlers = new Map();
    }

    connect(wsUrl) {
        try {
            this.ws = new WebSocket(wsUrl);
            appState.ws = this.ws;
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                appState.setConnected(true);
                this.updateConnectionStatus();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                appState.setConnected(false);
                this.updateConnectionStatus();
                
                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    setTimeout(() => {
                        if (!appState.isConnected) {
                            console.log(`Attempting to reconnect... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
                            this.reconnectAttempts++;
                            this.connect(wsUrl);
                        }
                    }, this.reconnectDelay);
                } else {
                    showToast('Connection lost. Please refresh the page.', 'error', 10000);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                showToast('Connection error occurred', 'error');
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            showToast('Failed to connect to server', 'error');
        }
    }

    // Register message handlers
    addMessageHandler(type, handler) {
        if (!this.messageHandlers.has(type)) {
            this.messageHandlers.set(type, []);
        }
        this.messageHandlers.get(type).push(handler);
    }

    removeMessageHandler(type, handler) {
        if (this.messageHandlers.has(type)) {
            const handlers = this.messageHandlers.get(type);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    handleMessage(data) {
        if (appState.debugMode) {
            console.log('WebSocket message received:', data);
        }

        // Call registered handlers
        if (this.messageHandlers.has(data.type)) {
            this.messageHandlers.get(data.type).forEach(handler => handler(data));
        }

        // Default message handling
        switch (data.type) {
            case 'session_id':
                appState.setSessionId(data.session_id);
                const downloadBtn = document.getElementById('downloadBtn');
                if (downloadBtn) downloadBtn.disabled = false;
                break;
                
            case 'status':
                this.handleStatusMessage(data);
                break;
                
            case 'thinking':
                showToast(`AI is thinking: ${data.message}`, 'info', 3000);
                break;
                
            case 'error':
                this.handleErrorMessage(data);
                break;
                
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    handleStatusMessage(data) {
        if (data.status === 'typing') {
            appState.setTyping(true);
        } else if (data.status === 'complete') {
            appState.setTyping(false);
        }
    }

    handleErrorMessage(data) {
        showToast(data.message || 'An error occurred', 'error');
        appState.setTyping(false);
    }

    updateConnectionStatus() {
        // Legacy DOM update for non-Alpine components (if they exist)
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        
        if (statusIndicator && statusText) {
            if (appState.isConnected) {
                statusIndicator.className = 'status-indicator connected';
                statusText.textContent = 'Connected';
            } else {
                statusIndicator.className = 'status-indicator disconnected';
                statusText.textContent = 'Disconnected';
            }
        }
        
        // Alpine.js components will automatically update via state listeners
        // No direct DOM manipulation needed for Alpine components
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket is not connected');
            showToast('Connection not available', 'error');
        }
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Global instance
export const webSocketService = new WebSocketService();
