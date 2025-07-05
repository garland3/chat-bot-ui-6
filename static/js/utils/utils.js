// Utility Functions
export const utils = {
    formatTime: (date = new Date()) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    escapeHtml: (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    generateId: () => {
        return Math.random().toString(36).substr(2, 9);
    },
    
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            // Import toast from components if needed
            const { showToast } = await import('../components/Toast.js');
            showToast('Copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            const { showToast } = await import('../components/Toast.js');
            showToast('Failed to copy text', 'error');
        }
    }
};
