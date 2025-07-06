Alpine.data('chatApp', () => ({
    messages: [],
    currentMessage: '',
    selectedModel: '',
    selectedTools: [],
    selectedDataSources: [],
    availableModels: [],
    isStreaming: false,
    sessionId: null,

    init() {
        this.fetchAvailableModels();
        // Listen for session ID from connectionStatus component
        this.$root.addEventListener('session-id-received', (event) => {
            this.sessionId = event.detail;
            console.log('Session ID received:', this.sessionId);
        });
    },

    fetchAvailableModels() {
        fetch('/llms')
            .then(response => response.json())
            .then(data => {
                this.availableModels = data; // Assuming /llms returns a list of LLM names directly
                if (this.availableModels.length > 0) {
                    this.selectedModel = this.availableModels[0];
                }
            });
    },

    sendMessage() {
        if (!this.currentMessage.trim() || !this.sessionId) return;

        const messagePayload = {
            content: this.currentMessage,
            llm_name: this.selectedModel,
            selected_tools: this.selectedTools,
            selected_data_sources: this.selectedDataSources
        };

        this.messages.push({ role: 'user', content: this.currentMessage });
        this.currentMessage = '';
        this.isStreaming = true;

        const assistantMessage = { role: 'assistant', content: '' };
        this.messages.push(assistantMessage);

        fetch(`/chat/${this.sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(messagePayload)
        })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            reader.read().then(function processText({ done, value }) {
                if (done) {
                    this.isStreaming = false;
                    return;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n').filter(line => line.trim());

                lines.forEach(line => {
                    if (line.startsWith('tool:selected')) {
                        const toolName = line.split(' ')[1];
                        this.messages.push({ role: 'system', content: `Tool selected: ${toolName}` });
                    } else {
                        assistantMessage.content += line;
                    }
                });

                return reader.read().then(processText.bind(this));
            }.bind(this));
        });
    }
})), Alpine.data('connectionStatus', () => ({
    isConnected: false,
    statusText: 'Disconnected',
    ws: null,

    init() {
        this.connectWebSocket();
    },

    connectWebSocket() {
        const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.isConnected = true;
            this.statusText = 'Connected';
            console.log('WebSocket connected');
            // Send session_init message to backend
            this.ws.send(JSON.stringify({"type": "session_init"}));
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'session_id') {
                this.$dispatch('session-id-received', data.session_id);
            } else if (data.type === 'status') {
                // Handle status messages if needed
            } else if (data.type === 'error') {
                this.$dispatch('show-toast', { message: data.message || 'An error occurred', type: 'error' });
            }
        };

        this.ws.onclose = (event) => {
            this.isConnected = false;
            this.statusText = 'Disconnected';
            console.log('WebSocket disconnected:', event.code, event.reason);
            setTimeout(() => {
                if (!this.isConnected) {
                    console.log('Attempting to reconnect...');
                    this.connectWebSocket();
                }
            }, 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.$dispatch('show-toast', { message: 'Connection error occurred', type: 'error' });
        };
    }
})), Alpine.data('toolsDropdown', () => ({
    isOpen: false,
    selectedTools: Alpine.raw(Alpine.store('chatApp').selectedTools), // Reference chatApp's selectedTools
    
    init() {
        this.$watch('$store.chatApp.selectedTools', (newTools) => {
            this.selectedTools = Alpine.raw(newTools);
        });
    },

    toggle() {
        this.isOpen = !this.isOpen;
    },

    close() {
        this.isOpen = false;
    },

    toggleTool(toolName) {
        const chatApp = Alpine.store('chatApp');
        if (chatApp.selectedTools.includes(toolName)) {
            chatApp.selectedTools = chatApp.selectedTools.filter(t => t !== toolName);
        } else {
            chatApp.selectedTools.push(toolName);
        }
    },

    isToolSelected(toolName) {
        return Alpine.store('chatApp').selectedTools.includes(toolName);
    },

    get selectedCount() {
        return Alpine.store('chatApp').selectedTools.length > 0 ? `(${Alpine.store('chatApp').selectedTools.length})` : '';
    }
})), Alpine.data('dataSourcesDropdown', () => ({
    isOpen: false,
    dataSources: [], // This should be fetched from backend or defined
    selectedDataSources: Alpine.raw(Alpine.store('chatApp').selectedDataSources),

    init() {
        this.fetchDataSources();
        this.$watch('$store.chatApp.selectedDataSources', (newSources) => {
            this.selectedDataSources = Alpine.raw(newSources);
        });
    },

    fetchDataSources() {
        // Mock data for now, replace with actual API call
        this.dataSources = [
            { name: 'UserDatabase' },
            { name: 'ProductCatalog' },
            { name: 'SalesData' }
        ];
    },

    toggle() {
        this.isOpen = !this.isOpen;
    },

    close() {
        this.isOpen = false;
    },

    toggleSource(sourceName) {
        const chatApp = Alpine.store('chatApp');
        if (chatApp.selectedDataSources.includes(sourceName)) {
            chatApp.selectedDataSources = chatApp.selectedDataSources.filter(s => s !== sourceName);
        } else {
            chatApp.selectedDataSources.push(sourceName);
        }
    },

    isSourceSelected(sourceName) {
        return Alpine.store('chatApp').selectedDataSources.includes(sourceName);
    },

    get selectedCount() {
        return Alpine.store('chatApp').selectedDataSources.length > 0 ? `(${Alpine.store('chatApp').selectedDataSources.length})` : '';
    }
})), Alpine.data('llmDropdown', () => ({
    isOpen: false,
    availableLLMs: Alpine.raw(Alpine.store('chatApp').availableModels),
    selectedModelName: '',

    init() {
        this.$watch('$store.chatApp.availableModels', (newModels) => {
            this.availableLLMs = Alpine.raw(newModels);
            if (this.availableLLMs.length > 0 && !Alpine.store('chatApp').selectedModel) {
                Alpine.store('chatApp').selectedModel = this.availableLLMs[0];
            }
            this.updateSelectedModelName();
        });
        this.$watch('$store.chatApp.selectedModel', () => {
            this.updateSelectedModelName();
        });
        this.updateSelectedModelName(); // Initial set
    },

    toggle() {
        this.isOpen = !this.isOpen;
    },

    close() {
        this.isOpen = false;
    },

    selectLLM(llm) {
        Alpine.store('chatApp').selectedModel = llm;
        this.close();
    },

    isLLMSelected(llmName) {
        return Alpine.store('chatApp').selectedModel === llmName;
    },

    updateSelectedModelName() {
        this.selectedModelName = Alpine.store('chatApp').selectedModel || 'Loading...';
    }
})), Alpine.data('toastManager', () => ({
    toasts: [],
    idCounter: 0,

    init() {
        this.$root.addEventListener('show-toast', (event) => {
            this.showToast(event.detail.message, event.detail.type);
        });
    },

    showToast(message, type = 'info', duration = 5000) {
        const id = this.idCounter++;
        this.toasts.push({ id, message, type, show: false });
        this.$nextTick(() => {
            const newToast = this.toasts.find(toast => toast.id === id);
            if (newToast) {
                newToast.show = true;
            }
        });
        setTimeout(() => this.removeToast(id), duration);
    },

    removeToast(id) {
        const toast = this.toasts.find(t => t.id === id);
        if (toast) {
            toast.show = false;
            setTimeout(() => {
                this.toasts = this.toasts.filter(t => t.id !== id);
            }, 250); // Match CSS transition duration
        }
    }
})), // Initialize Alpine Store for global state management
Alpine.store('chatApp', {
    messages: [],
    currentMessage: '',
    selectedModel: '',
    selectedTools: [],
    selectedDataSources: [],
    availableModels: [],
    isStreaming: false,
    sessionId: null,
});