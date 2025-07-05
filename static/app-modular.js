// Modern Modular App Entry Point
import { appState } from './js/state/AppState.js';
import { webSocketService } from './js/services/WebSocketService.js';
import { apiService } from './js/services/ApiService.js';
import { chatManager } from './js/components/Chat.js';
import { showToast } from './js/components/Toast.js';

// Global app instance for easy access
window.app = {
    state: appState,
    websocket: webSocketService,
    api: apiService,
    chat: chatManager
};

class GalaxyChatApp {
    constructor() {
        this.elements = this.initElements();
        this.setupEventListeners();
        this.setupWebSocketHandlers();
    }

    initElements() {
        return {
            newChatBtn: document.getElementById('newChatBtn'),
            downloadBtn: document.getElementById('downloadBtn'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            
            // Alpine.js now handles these dropdowns:
            // toolsDropdown, dataSourcesDropdown, llmDropdown
            
            userEmail: document.getElementById('userEmail')
        };
    }

    setupEventListeners() {
        // Header controls
        this.elements.newChatBtn.addEventListener('click', () => this.createNewSession());
        this.elements.downloadBtn.addEventListener('click', () => this.downloadChat());
        
        // Note: All dropdown logic is now handled by Alpine.js components
        // Tools, data sources, and LLM dropdowns are managed by Alpine.js
        
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.createNewSession();
            }
            if (e.key === 'Escape') {
                this.closeAllDropdowns();
            }
        });

        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && !appState.isConnected) {
                console.log('Page became visible, attempting to reconnect...');
                webSocketService.connect(window.appConfig.wsUrl);
            }
        });

        // Global error handler
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            if (appState.debugMode) {
                // Use Alpine toast if available, fallback to import
                if (window.alpineShowToast) {
                    window.alpineShowToast(`Error: ${event.error.message}`, 'error');
                } else {
                    showToast(`Error: ${event.error.message}`, 'error');
                }
            }
        });
    }

    setupWebSocketHandlers() {
        // Register handlers for different message types
        webSocketService.addMessageHandler('tool_call', (data) => {
            if (appState.currentStreamingMessage) {
                chatManager.addToolCallToMessage(appState.currentStreamingMessage, data);
            }
        });

        webSocketService.addMessageHandler('message_start', (data) => {
            chatManager.handleMessageStart(data);
        });

        webSocketService.addMessageHandler('message_chunk', (data) => {
            chatManager.handleMessageChunk(data.content);
        });

        webSocketService.addMessageHandler('message_complete', (data) => {
            chatManager.handleMessageComplete(data.content);
        });
    }

    // Session Management
    async createNewSession() {
        try {
            this.showLoading(true);
            
            const data = await apiService.createSession();
            appState.setSessionId(data.session_id);
            
            // Clear chat
            chatManager.clearChat();
            this.elements.downloadBtn.disabled = false;
            
            showToast('New chat session started', 'success');
            
        } catch (error) {
            console.error('Error creating new session:', error);
            showToast('Failed to create new session', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async downloadChat() {
        if (!appState.sessionId) {
            showToast('No active session to download', 'warning');
            return;
        }
        
        await apiService.downloadChat(appState.sessionId);
    }

    // Configuration Loading
    async loadLLMConfigs() {
        try {
            const llms = await apiService.loadLLMConfigs();
            appState.availableLLMs = llms;
            
            // Set default LLM if none selected and Alpine.js components will handle the UI update
            if (appState.availableLLMs.length > 0 && !appState.selectedLLM) {
                appState.selectedLLM = appState.availableLLMs[0];
            }
            
            console.log('App: Loaded LLM configs:', llms);
            
        } catch (error) {
            console.error('Error loading LLM configs:', error);
            // Alpine.js components will handle displaying error state
        }
    }

    async loadThemeConfig() {
        try {
            const themeConfig = await apiService.loadThemeConfig();
            if (!themeConfig) return;
            
            console.log('Theme config received:', themeConfig);
            
            // Apply theme configuration
            if (themeConfig.app_name) {
                document.title = themeConfig.app_name;
                const appTitle = document.querySelector('.app-title');
                if (appTitle) appTitle.textContent = themeConfig.app_name;
                
                const welcomeTitle = document.querySelector('.welcome-content h2');
                if (welcomeTitle) welcomeTitle.textContent = `Welcome to ${themeConfig.app_name}`;
            }
            
            // Apply colors
            this.applyThemeColors(themeConfig);
            
            if (appState.debugMode) {
                this.debugThemeColors();
            }
            
        } catch (error) {
            console.error('Error loading theme config:', error);
        }
    }

    applyThemeColors(themeConfig) {
        const root = document.documentElement;
        const colorMappings = {
            background_color: '--bg-primary',
            accent_primary: '--accent-primary',
            accent_secondary: '--accent-secondary',
            bg_secondary: '--bg-secondary',
            bg_tertiary: '--bg-tertiary',
            bg_hover: '--bg-hover',
            bg_active: '--bg-active',
            text_primary: '--text-primary',
            text_secondary: '--text-secondary',
            text_muted: '--text-muted',
            border_color: '--border-color'
        };

        Object.entries(colorMappings).forEach(([configKey, cssVar]) => {
            if (themeConfig[configKey]) {
                root.style.setProperty(cssVar, themeConfig[configKey]);
            }
        });

        if (themeConfig.accent_primary) {
            root.style.setProperty('--text-accent', themeConfig.accent_primary);
        }
    }

    debugThemeColors() {
        if (!appState.debugMode) return;
        
        const root = document.documentElement;
        const computedStyle = getComputedStyle(root);
        
        console.log('=== THEME DEBUG INFO ===');
        const props = ['--bg-primary', '--bg-secondary', '--bg-tertiary', '--bg-hover', '--bg-active', 
                      '--accent-primary', '--accent-secondary', '--text-primary', '--text-secondary', 
                      '--text-muted', '--text-accent', '--border-color'];
        
        props.forEach(prop => {
            const applied = root.style.getPropertyValue(prop);
            const computed = computedStyle.getPropertyValue(prop).trim();
            console.log(`${prop}: applied="${applied}" computed="${computed}"`);
        });
        console.log('========================');
    }

    async loadDataSources() {
        try {
            const dataSources = await apiService.loadDataSources();
            appState.availableDataSources = dataSources;
            console.log('App: Loaded data sources:', dataSources);
        } catch (error) {
            console.error('Error loading data sources:', error);
        }
    }

    async loadUserInfo() {
        try {
            // User info would come from backend authentication
            appState.userEmail = 'user@example.com';
            this.elements.userEmail.textContent = appState.userEmail;
        } catch (error) {
            console.error('Error loading user info:', error);
            this.elements.userEmail.textContent = 'Unknown user';
        }
    }

    // Note: All dropdown UI management is now handled by Alpine.js components
    // LLM selection, data sources, and tools are managed by Alpine.js

    showLoading(show) {
        this.elements.loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    // Debug
    updateDebugInfo() {
        if (!appState.debugMode) return;
        console.log('Debug Info:', appState.getDebugInfo());
    }

    // Initialization
    async initialize() {
        console.log('Initializing Galaxy Chat...');
        
        try {
            // Initialize WebSocket connection
            webSocketService.connect(window.appConfig.wsUrl);
            
            // Load initial data
            await Promise.all([
                this.loadThemeConfig(),
                this.loadLLMConfigs(),
                this.loadDataSources(),
                this.loadUserInfo()
            ]);
            
            // Create initial session
            await this.createNewSession();
            
            console.log('Galaxy Chat initialized successfully');
            
        } catch (error) {
            console.error('Error initializing application:', error);
            showToast('Failed to initialize application', 'error');
        }
    }
}

// Initialize the application
const app = new GalaxyChatApp();

// Make app and services globally available for Alpine.js components
window.app = app;
window.app.state = appState;
window.app.apiService = apiService;

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Small delay to ensure Alpine.js components are registered
        setTimeout(() => app.initialize(), 50);
    });
} else {
    // Small delay to ensure Alpine.js components are registered
    setTimeout(() => app.initialize(), 50);
}

// Export for debugging
if (appState.debugMode) {
    window.galaxyApp = app;
}
