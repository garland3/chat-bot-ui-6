// Alpine.js Components
// Connection Status Component
function connectionStatus() {
    return {
        isConnected: false,
        statusText: 'Connecting...',
        checkInterval: null,
        listenerSetup: false, // Flag to prevent duplicate listeners
        
        init() {
            console.log('Alpine connectionStatus: Initializing component');
            // Start polling for app state until it's available
            this.startPolling();
            
            // Also try to set up listener immediately if app is already available
            this.setupStateListener();
        },

        startPolling() {
            // Check every 100ms until window.app is available
            this.checkInterval = setInterval(() => {
                if (window.app && window.app.state && !this.listenerSetup) {
                    console.log('Alpine connectionStatus: App state available, setting up listener');
                    this.setupStateListener();
                    this.updateFromGlobalState();
                    clearInterval(this.checkInterval);
                    this.checkInterval = null;
                }
            }, 100);
        },

        setupStateListener() {
            // Only set up listener once
            if (this.listenerSetup || !window.app || !window.app.state) {
                return;
            }
            
            console.log('Alpine connectionStatus: Setting up state listener');
            this.listenerSetup = true;
            
            // Create the update function
            const updateFn = (connected) => {
                console.log('Alpine connectionStatus: Received connection update:', connected);
                this.isConnected = connected;
                this.statusText = connected ? 'Connected' : 'Disconnected';
            };
            
            // Store the function for potential cleanup
            this.connectionUpdateFn = updateFn;
            window.app.state.addListener('connection', updateFn);
            
            // Also immediately check current state
            this.updateFromGlobalState();
        },

        updateFromGlobalState() {
            if (window.app && window.app.state) {
                const currentState = window.app.state.isConnected;
                console.log('Alpine connectionStatus: Updating from global state:', currentState);
                this.isConnected = currentState;
                this.statusText = currentState ? 'Connected' : 'Disconnected';
            }
        },

        destroy() {
            console.log('Alpine connectionStatus: Destroying component');
            
            // Cleanup interval if component is destroyed
            if (this.checkInterval) {
                clearInterval(this.checkInterval);
                this.checkInterval = null;
            }
            
            // Remove listener if we have the function reference
            if (this.connectionUpdateFn && window.app && window.app.state) {
                window.app.state.removeListener('connection', this.connectionUpdateFn);
                this.connectionUpdateFn = null;
            }
            
            this.listenerSetup = false;
        }
    };
}

// Tools Dropdown Component
function toolsDropdown() {
    return {
        isOpen: false,
        selectedCount: 0,
        tools: [],
        selectedTools: new Set(),

        init() {
            // Listen to global app state for tools
            if (window.app && window.app.state) {
                this.selectedTools = window.app.state.selectedTools;
                this.updateSelectedCount();
            }
        },

        toggle() {
            this.isOpen = !this.isOpen;
        },

        close() {
            this.isOpen = false;
        },

        toggleTool(toolValue) {
            if (this.selectedTools.has(toolValue)) {
                this.selectedTools.delete(toolValue);
            } else {
                this.selectedTools.add(toolValue);
            }
            this.updateSelectedCount();
            
            // Update global state
            if (window.app && window.app.state) {
                window.app.state.selectedTools = this.selectedTools;
            }
        },

        updateSelectedCount() {
            this.selectedCount = this.selectedTools.size;
        },

        isToolSelected(toolValue) {
            return this.selectedTools.has(toolValue);
        }
    };
}

// Toast Manager Component
function toastManager() {
    return {
        toasts: [],

        init() {
            // Register global toast function that Alpine can use
            window.alpineShowToast = (message, type = 'info', duration = 5000) => {
                this.show(message, type, duration);
            };
        },

        show(message, type = 'info', duration = 5000) {
            const id = Math.random().toString(36).substr(2, 9);
            const toast = {
                id,
                message,
                type,
                show: false
            };

            this.toasts.push(toast);

            // Trigger show animation
            this.$nextTick(() => {
                const toastElement = this.toasts.find(t => t.id === id);
                if (toastElement) {
                    toastElement.show = true;
                }
            });

            // Auto remove
            setTimeout(() => {
                this.remove(id);
            }, duration);

            return id;
        },

        remove(toastId) {
            const toastIndex = this.toasts.findIndex(t => t.id === toastId);
            if (toastIndex > -1) {
                // Hide animation
                this.toasts[toastIndex].show = false;
                
                // Remove from array after animation
                setTimeout(() => {
                    const index = this.toasts.findIndex(t => t.id === toastId);
                    if (index > -1) {
                        this.toasts.splice(index, 1);
                    }
                }, 250);
            }
        }
    };
}

// Data Sources Dropdown Component
function dataSourcesDropdown() {
    return {
        isOpen: false,
        selectedCount: 0,
        dataSources: [],
        selectedDataSources: new Set(),

        init() {
            console.log('Alpine dataSourcesDropdown: Initializing component');
            this.loadDataSources();
            this.setupStateListener();
        },

        async loadDataSources() {
            try {
                if (window.app && window.app.apiService) {
                    console.log('Alpine dataSourcesDropdown: Loading data sources');
                    this.dataSources = await window.app.apiService.loadDataSources();
                    console.log('Alpine dataSourcesDropdown: Loaded data sources:', this.dataSources);
                } else {
                    // Wait for app to be available, but don't spam the console
                    if (!this._retryAttempts) this._retryAttempts = 0;
                    this._retryAttempts++;
                    
                    if (this._retryAttempts <= 3) {
                        console.log('Alpine dataSourcesDropdown: Waiting for API service...');
                    }
                    
                    setTimeout(() => this.loadDataSources(), 200);
                }
            } catch (error) {
                console.error('Alpine dataSourcesDropdown: Error loading data sources:', error);
            }
        },

        setupStateListener() {
            if (window.app && window.app.state) {
                console.log('Alpine dataSourcesDropdown: Setting up state listener');
                this.selectedDataSources = window.app.state.selectedDataSources;
                this.updateSelectedCount();
            } else {
                setTimeout(() => this.setupStateListener(), 100);
            }
        },

        toggle() {
            this.isOpen = !this.isOpen;
        },

        close() {
            this.isOpen = false;
        },

        toggleSource(sourceName) {
            if (this.selectedDataSources.has(sourceName)) {
                this.selectedDataSources.delete(sourceName);
            } else {
                this.selectedDataSources.add(sourceName);
            }
            this.updateSelectedCount();
            
            // Update global state
            if (window.app && window.app.state) {
                window.app.state.selectedDataSources = this.selectedDataSources;
            }
        },

        updateSelectedCount() {
            this.selectedCount = this.selectedDataSources.size;
        },

        isSourceSelected(sourceName) {
            return this.selectedDataSources.has(sourceName);
        }
    };
}

// LLM Dropdown Component
function llmDropdown() {
    return {
        isOpen: false,
        availableLLMs: [],
        selectedLLM: null,
        selectedModelName: 'Loading...',

        init() {
            console.log('Alpine llmDropdown: Initializing component');
            this.loadLLMs();
            this.setupStateListener();
        },

        async loadLLMs() {
            try {
                if (window.app && window.app.apiService) {
                    console.log('Alpine llmDropdown: Loading LLMs');
                    this.availableLLMs = await window.app.apiService.loadLLMConfigs();
                    console.log('Alpine llmDropdown: Loaded LLMs:', this.availableLLMs);
                    this.updateSelectedDisplay();
                } else {
                    // Wait for app to be available, but don't spam the console
                    if (!this._retryAttempts) this._retryAttempts = 0;
                    this._retryAttempts++;
                    
                    if (this._retryAttempts <= 3) {
                        console.log('Alpine llmDropdown: Waiting for API service...');
                    }
                    
                    setTimeout(() => this.loadLLMs(), 200);
                }
            } catch (error) {
                console.error('Alpine llmDropdown: Error loading LLMs:', error);
                this.selectedModelName = 'Error loading models';
            }
        },

        setupStateListener() {
            if (window.app && window.app.state) {
                console.log('Alpine llmDropdown: Setting up state listener');
                this.selectedLLM = window.app.state.selectedLLM;
                this.updateSelectedDisplay();
            } else {
                setTimeout(() => this.setupStateListener(), 100);
            }
        },

        toggle() {
            this.isOpen = !this.isOpen;
        },

        close() {
            this.isOpen = false;
        },

        selectLLM(llm) {
            console.log('Alpine llmDropdown: Selecting LLM:', llm);
            this.selectedLLM = llm;
            this.updateSelectedDisplay();
            this.close();
            
            // Update global state
            if (window.app && window.app.state) {
                window.app.state.selectedLLM = llm;
            }
        },

        updateSelectedDisplay() {
            if (this.selectedLLM) {
                this.selectedModelName = this.selectedLLM.name;
            } else if (this.availableLLMs.length > 0) {
                // Auto-select first LLM if none selected
                console.log('Alpine llmDropdown: Auto-selecting first LLM');
                this.selectLLM(this.availableLLMs[0]);
            } else {
                this.selectedModelName = 'No model selected';
            }
        },

        isLLMSelected(llmName) {
            return this.selectedLLM && this.selectedLLM.name === llmName;
        }
    };
}

// Make components globally available for Alpine.js
window.connectionStatus = connectionStatus;
window.toolsDropdown = toolsDropdown;
window.toastManager = toastManager;
window.dataSourcesDropdown = dataSourcesDropdown;
window.llmDropdown = llmDropdown;
window.dataSourcesDropdown = dataSourcesDropdown;
window.llmDropdown = llmDropdown;
