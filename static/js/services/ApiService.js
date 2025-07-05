import { showToast } from '../components/Toast.js';

export class ApiService {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    async request(url, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${url}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${url}:`, error);
            throw error;
        }
    }

    // Session management
    async createSession() {
        return this.request('/chat', {
            method: 'POST',
            body: JSON.stringify({})
        });
    }

    async sendMessage(sessionId, message, tools, dataSources, llmConfig) {
        return this.request(`/chat/${sessionId}/message`, {
            method: 'POST',
            body: JSON.stringify({
                message,
                tools: Array.from(tools),
                data_sources: Array.from(dataSources),
                llm_config: llmConfig
            })
        });
    }

    async downloadChat(sessionId) {
        try {
            const response = await fetch(`${this.baseUrl}/chat/${sessionId}/download`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat-${sessionId}-${new Date().toISOString().split('T')[0]}.txt`;
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

    // Configuration endpoints
    async loadLLMConfigs() {
        try {
            const data = await this.request('/api/llm_configs');
            
            // Handle different response structures
            if (Array.isArray(data)) {
                return data;
            } else if (data.llms && Array.isArray(data.llms)) {
                return data.llms;
            } else {
                console.error('Unexpected LLM config response structure:', data);
                return [];
            }
        } catch (error) {
            console.error('Error loading LLM configs:', error);
            showToast('Failed to load AI models', 'error');
            return [];
        }
    }

    async loadThemeConfig() {
        try {
            return await this.request('/api/theme/config');
        } catch (error) {
            console.error('Error loading theme config:', error);
            showToast('Failed to load theme configuration', 'error');
            return null;
        }
    }

    async loadDataSources() {
        try {
            return await this.request('/api/data/data-sources');
        } catch (error) {
            console.error('Error loading data sources:', error);
            showToast('Failed to load data sources', 'error');
            return [];
        }
    }
}

// Global instance
export const apiService = new ApiService(window.appConfig?.apiBaseUrl || '');
