document.addEventListener('alpine:init', () => {
    Alpine.data('chatApp', () => ({
        messages: [],
        currentMessage: '',
        selectedModel: '',
        selectedTools: [],
        selectedDataSources: [],
        availableModels: [],
        isStreaming: false,
        ws: null,
        sessionId: null,

        init() {
            this.fetchAvailableModels();
            this.connectWebSocket();
        },

        fetchAvailableModels() {
            fetch('/llms')
                .then(response => response.json())
                .then(data => {
                    this.availableModels = data.llms;
                    if (this.availableModels.length > 0) {
                        this.selectedModel = this.availableModels[0].name;
                    }
                });
        },

        connectWebSocket() {
            const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.createSession();
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'session_id') {
                    this.sessionId = data.session_id;
                }
            };
        },

        createSession() {
            fetch('/chat', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    // The session_id will be received via WebSocket
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
    }));
});