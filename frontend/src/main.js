import Alpine from 'alpinejs'

// Make Alpine available globally for debugging
window.Alpine = Alpine

// Chat App Alpine.js Component
document.addEventListener('alpine:init', () => {
    Alpine.data('chatApp', () => ({
        // State
        messages: [],
        currentMessage: '',
        selectedModel: '',
        selectedTools: [],
        selectedDataSources: [],
        availableModels: [],
        isStreaming: false,
        websocket: null,
        sessionId: null,

        // Initialize component
        init() {
            this.fetchAvailableModels()
            this.connectWebSocket()
        },

        // Fetch available models from backend
        async fetchAvailableModels() {
            try {
                const response = await fetch('/api/llm-configs')
                if (response.ok) {
                    const data = await response.json()
                    this.availableModels = data.llms || []
                    // Set default model if available
                    if (this.availableModels.length > 0) {
                        this.selectedModel = this.availableModels[0].name
                    }
                }
            } catch (error) {
                console.error('Failed to fetch models:', error)
            }
        },

        // Connect to WebSocket for real-time updates
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
            const wsUrl = `${protocol}//${window.location.host}/ws`
            
            this.websocket = new WebSocket(wsUrl)
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected')
            }
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data)
                this.handleWebSocketMessage(data)
            }
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected')
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000)
            }
        },

        // Handle WebSocket messages
        handleWebSocketMessage(data) {
            if (data.type === 'status') {
                // Handle status updates
                console.log('Status:', data.message)
            } else if (data.type === 'tool_selected') {
                // Handle tool selection feedback
                this.addMessage('system', `Tool selected: ${data.tool}`)
            }
        },

        // Send message to chat API
        async sendMessage() {
            if (!this.currentMessage.trim() || this.isStreaming) return

            const userMessage = this.currentMessage.trim()
            this.addMessage('user', userMessage)
            this.currentMessage = ''
            this.isStreaming = true

            try {
                // Ensure we have a session
                if (!this.sessionId) {
                    await this.createSession()
                }

                const response = await fetch(`/api/chat/${this.sessionId}/message`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: userMessage,
                        llm_name: this.selectedModel,
                        selected_tools: this.selectedTools,
                        selected_data_sources: this.selectedDataSources
                    })
                })

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`)
                }

                // Handle streaming response
                const reader = response.body.getReader()
                const decoder = new TextDecoder()
                let assistantMessage = this.addMessage('assistant', '')

                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunk = decoder.decode(value, { stream: true })
                    const lines = chunk.split('\n')

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6)
                            if (data === '[DONE]') {
                                this.isStreaming = false
                                return
                            }

                            try {
                                const parsed = JSON.parse(data)
                                if (parsed.content) {
                                    assistantMessage.content += parsed.content
                                    this.scrollToBottom()
                                } else if (parsed.type === 'tool_selected') {
                                    this.addMessage('system', `Tool selected: ${parsed.tool}`)
                                } else if (parsed.type === 'data_source_selected') {
                                    this.addMessage('system', `Data source selected: ${parsed.data_source}`)
                                }
                            } catch (e) {
                                // Ignore parsing errors for incomplete chunks
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Chat error:', error)
                this.addMessage('system', `Error: ${error.message}`)
            } finally {
                this.isStreaming = false
            }
        },

        // Create a new chat session
        async createSession() {
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })

                if (response.ok) {
                    const data = await response.json()
                    this.sessionId = data.session_id
                } else {
                    throw new Error(`Failed to create session: ${response.status}`)
                }
            } catch (error) {
                console.error('Failed to create session:', error)
                throw error
            }
        },

        // Add message to chat
        addMessage(role, content) {
            const message = {
                id: Date.now() + Math.random(),
                role: role,
                content: content,
                timestamp: new Date()
            }
            this.messages.push(message)
            this.scrollToBottom()
            return message
        },

        // Scroll to bottom of messages
        scrollToBottom() {
            this.$nextTick(() => {
                const messagesContainer = document.getElementById('messages')
                if (messagesContainer) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight
                }
            })
        }
    }))
})

// Start Alpine
Alpine.start()