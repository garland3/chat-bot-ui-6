import Alpine from 'alpinejs'
import { marked } from 'marked'

// Configure marked for safe rendering
marked.setOptions({
    breaks: true,
    gfm: true,
    sanitize: false,
    smartLists: true,
    smartypants: false
})

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
        availableTools: [],
        availableDataSources: [],
        isStreaming: false,
        websocket: null,
        sessionId: null,
        loadingModels: true,
        loadingTools: true,
        loadingDataSources: true,
        appName: 'Chat Bot UI 6', // Default fallback
        appConfig: null,
        websocketConnected: false,

        // Initialize component
        init() {
            this.fetchAppConfig()
            this.fetchAvailableModels()
            this.fetchAvailableTools()
            this.fetchAvailableDataSources()
            this.connectWebSocket()
        },

        // Fetch app configuration
        async fetchAppConfig() {
            try {
                const response = await fetch('/api/config')
                if (response.ok) {
                    const config = await response.json()
                    console.log('📡 Loaded app config:', config)
                    console.log('🏷️ App name from backend:', config.app_name)
                    this.appConfig = config
                    this.appName = config.app_name || this.appName
                    
                    // Update document title
                    document.title = this.appName
                }
            } catch (error) {
                console.error('Failed to fetch app config:', error)
            }
        },

        // Fetch available models from backend
        async fetchAvailableModels() {
            try {
                this.loadingModels = true
                const response = await fetch('/llms')
                if (response.ok) {
                    const data = await response.json()
                    console.log('📡 Loaded LLM models from API:', data)
                    
                    // Handle new LLM config format from YAML
                    if (Array.isArray(data)) {
                        this.availableModels = data.map(llm => ({
                            name: llm.name,
                            display_name: llm.name,
                            provider: llm.provider,
                            model: llm.model,
                            description: llm.description
                        }))
                    } else {
                        // Legacy format fallback
                        this.availableModels = data.llms || []
                    }
                    
                    console.log('📋 Processed available models:', this.availableModels)
                    
                    // Set default model if available
                    if (this.availableModels.length > 0) {
                        this.selectedModel = this.availableModels[0].name
                    }
                }
            } catch (error) {
                console.error('Failed to fetch models:', error)
            } finally {
                this.loadingModels = false
            }
        },

        // Fetch available tools from backend
        async fetchAvailableTools() {
            try {
                this.loadingTools = true
                const response = await fetch('/api/tools')
                if (response.ok) {
                    const data = await response.json()
                    this.availableTools = data.tools || []
                }
            } catch (error) {
                console.error('Failed to fetch tools:', error)
            } finally {
                this.loadingTools = false
            }
        },

        // Fetch available data sources from backend
        async fetchAvailableDataSources() {
            try {
                this.loadingDataSources = true
                const response = await fetch('/api/data-sources')
                if (response.ok) {
                    const data = await response.json()
                    this.availableDataSources = data.data_sources || []
                }
            } catch (error) {
                console.error('Failed to fetch data sources:', error)
            } finally {
                this.loadingDataSources = false
            }
        },

        // Connect to WebSocket for real-time updates
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
            const wsUrl = `${protocol}//${window.location.host}/ws`
            
            this.websocket = new WebSocket(wsUrl)
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected')
                this.websocketConnected = true
            }
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data)
                this.handleWebSocketMessage(data)
            }
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected')
                this.websocketConnected = false
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
            console.log('🚀 sendMessage called, currentMessage:', this.currentMessage)
            if (!this.currentMessage.trim() || this.isStreaming) {
                console.log('❌ Aborting sendMessage: empty message or already streaming')
                return
            }

            const userMessage = this.currentMessage.trim()
            console.log('👤 Adding user message:', userMessage)
            this.addMessage('user', userMessage)
            this.currentMessage = ''
            this.isStreaming = true
            console.log('🔄 Set isStreaming to true')

            try {
                // Ensure we have a session
                if (!this.sessionId) {
                    console.log('🆔 No session ID, creating new session')
                    await this.createSession()
                    console.log('🆔 Session created:', this.sessionId)
                }

                const requestBody = {
                    content: userMessage,
                    llm_name: this.selectedModel,
                    selected_tools: this.selectedTools,
                    selected_data_sources: this.selectedDataSources
                }
                console.log('📤 Sending request to:', `/chat/${this.sessionId}/message`)
                console.log('📤 Request body:', requestBody)

                const response = await fetch(`/chat/${this.sessionId}/message`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                })

                console.log('📥 Response status:', response.status, response.statusText)
                console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()))

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`)
                }

                // Handle streaming response
                const reader = response.body.getReader()
                const decoder = new TextDecoder()
                let assistantMessage = this.addMessage('assistant', '')
                console.log('🤖 Created assistant message:', assistantMessage)

                while (true) {
                    const { done, value } = await reader.read()
                    if (done) {
                        console.log('📡 Stream complete')
                        break
                    }

                    const chunk = decoder.decode(value, { stream: true })
                    console.log('📦 Received chunk:', chunk)
                    const lines = chunk.split('\n')

                    for (const line of lines) {
                        console.log('📄 Processing line:', line)
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6)
                            console.log('💾 Extracted data:', data)
                            
                            if (data === '[DONE]') {
                                console.log('✅ Stream finished with [DONE]')
                                this.isStreaming = false
                                return
                            }

                            try {
                                const parsed = JSON.parse(data)
                                console.log('🔍 Parsed data:', parsed)
                                
                                if (parsed.content) {
                                    console.log('💬 Adding content to message:', parsed.content)
                                    console.log('🔄 Message before update:', assistantMessage.content)
                                    
                                    // Update the message in the messages array to trigger Alpine reactivity
                                    const messageIndex = this.messages.findIndex(m => m.id === assistantMessage.id)
                                    if (messageIndex !== -1) {
                                        this.messages[messageIndex].content += parsed.content
                                        assistantMessage = this.messages[messageIndex] // Keep reference in sync
                                        console.log('🔄 Updated message in array at index:', messageIndex)
                                    } else {
                                        // Fallback - direct update
                                        assistantMessage.content += parsed.content
                                        console.log('⚠️ Fallback: Updated message directly')
                                    }
                                    
                                    console.log('🔄 Message after update:', assistantMessage.content)
                                    console.log('📝 Current messages array:', this.messages)
                                    this.scrollToBottom()
                                } else if (parsed.type === 'tool_selected') {
                                    console.log('🔧 Tool selected:', parsed.tool)
                                    this.addMessage('system', `Tool selected: ${parsed.tool}`)
                                } else if (parsed.type === 'data_source_selected') {
                                    console.log('🗃️ Data source selected:', parsed.data_source)
                                    this.addMessage('system', `Data source selected: ${parsed.data_source}`)
                                } else {
                                    console.log('❓ Unknown parsed data structure:', parsed)
                                }
                            } catch (e) {
                                console.log('⚠️ JSON parse error (ignoring):', e, 'Data:', data)
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
                const response = await fetch('/chat', {
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
            console.log('➕ Adding message:', { role, content, id: message.id })
            this.messages.push(message)
            console.log('📋 Messages array now has', this.messages.length, 'messages')
            console.log('📋 Full messages array:', this.messages)
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
        },

        // Format markdown content
        formatMarkdown(content) {
            try {
                let html = marked.parse(content || '')
                
                // Add copy buttons to code blocks
                html = html.replace(/<pre><code([^>]*)>([\s\S]*?)<\/code><\/pre>/g, (match, attributes, code) => {
                    // Generate a unique ID for this code block
                    const codeId = 'code-' + Math.random().toString(36).substr(2, 9)
                    // Decode HTML entities in the code content
                    const decodedCode = code
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>')
                        .replace(/&amp;/g, '&')
                        .replace(/&quot;/g, '"')
                        .replace(/&#39;/g, "'")
                    
                    return `
                        <div class="code-block-container">
                            <pre><code${attributes} id="${codeId}">${code}</code></pre>
                            <button class="copy-button" onclick="copyCodeToClipboard('${codeId}', this)" title="Copy code">
                                Copy
                            </button>
                        </div>
                    `
                })
                
                return html
            } catch (error) {
                console.error('Markdown parsing error:', error)
                return content || ''
            }
        }
    }))
})

// Global function for copying code to clipboard
window.copyCodeToClipboard = async function(codeId, buttonElement) {
    try {
        const codeElement = document.getElementById(codeId)
        if (!codeElement) {
            console.error('Code element not found:', codeId)
            return
        }
        
        // Get the text content and decode HTML entities
        let codeText = codeElement.textContent || codeElement.innerText
        
        // Copy to clipboard
        await navigator.clipboard.writeText(codeText)
        
        // Update button appearance
        const originalText = buttonElement.textContent
        buttonElement.textContent = 'Copied!'
        buttonElement.classList.add('copied')
        
        // Reset button after 2 seconds
        setTimeout(() => {
            buttonElement.textContent = originalText
            buttonElement.classList.remove('copied')
        }, 2000)
        
    } catch (error) {
        console.error('Failed to copy code:', error)
        
        // Fallback for older browsers
        const codeElement = document.getElementById(codeId)
        if (codeElement) {
            const range = document.createRange()
            range.selectNodeContents(codeElement)
            const selection = window.getSelection()
            selection.removeAllRanges()
            selection.addRange(range)
            
            try {
                document.execCommand('copy')
                buttonElement.textContent = 'Copied!'
                buttonElement.classList.add('copied')
                
                setTimeout(() => {
                    buttonElement.textContent = 'Copy'
                    buttonElement.classList.remove('copied')
                }, 2000)
                
            } catch (fallbackError) {
                console.error('Fallback copy failed:', fallbackError)
                buttonElement.textContent = 'Failed'
                setTimeout(() => {
                    buttonElement.textContent = 'Copy'
                }, 2000)
            }
            
            selection.removeAllRanges()
        }
    }
}

// Start Alpine
Alpine.start()