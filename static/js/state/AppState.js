// Application State Management
export class AppState {
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

    // State update methods
    setConnected(connected) {
        console.log('AppState: setConnected called with:', connected);
        this.isConnected = connected;
        this.notifyStateChange('connection', connected);
    }

    setTyping(typing) {
        this.isTyping = typing;
        this.notifyStateChange('typing', typing);
    }

    setSessionId(sessionId) {
        this.sessionId = sessionId;
        this.notifyStateChange('session', sessionId);
    }

    addMessage(message) {
        this.messageHistory.push(message);
        this.notifyStateChange('messages', this.messageHistory);
    }

    // Simple event system for state changes
    _listeners = new Map();

    addListener(event, callback) {
        if (!this._listeners.has(event)) {
            this._listeners.set(event, []);
        }
        this._listeners.get(event).push(callback);
    }

    removeListener(event, callback) {
        if (this._listeners.has(event)) {
            const callbacks = this._listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    notifyStateChange(event, data) {
        console.log(`AppState: Notifying ${event} listeners with data:`, data, 'Listeners count:', this._listeners.get(event)?.length || 0);
        if (this._listeners.has(event)) {
            this._listeners.get(event).forEach(callback => callback(data));
        }
    }

    // Debug helper
    getDebugInfo() {
        return {
            connected: this.isConnected,
            sessionId: this.sessionId,
            wsReadyState: this.ws?.readyState,
            selectedTools: Array.from(this.selectedTools),
            selectedDataSources: Array.from(this.selectedDataSources),
            selectedLLM: this.selectedLLM,
            messageCount: this.messageHistory.length
        };
    }
}

// Export global instance
export const appState = new AppState();
