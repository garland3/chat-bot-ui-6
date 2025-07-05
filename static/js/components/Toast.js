import { utils } from '../utils/utils.js';

// Toast Notification System
export class ToastManager {
    constructor() {
        // Try to find the container - could be Alpine managed or traditional
        this.container = document.getElementById('toastContainer') || 
                        document.querySelector('.toast-container');
        this.toasts = new Map();
    }

    show(message, type = 'info', duration = 5000) {
        // If Alpine toast is available, use it
        if (window.alpineShowToast) {
            return window.alpineShowToast(message, type, duration);
        }

        // Fallback to traditional toast system
        if (!this.container) {
            console.warn('Toast container not found, using console log instead');
            console.log(`Toast [${type}]: ${message}`);
            return;
        }

        const toast = this.createToast(message, type);
        const toastId = utils.generateId();
        
        toast.id = toastId;
        this.toasts.set(toastId, toast);
        
        this.container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Auto remove
        setTimeout(() => this.remove(toastId), duration);
        
        return toastId;
    }

    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        toast.innerHTML = `
            <div class="toast-header">
                <span class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</span>
                <button class="toast-close" data-action="close">&times;</button>
            </div>
            <div class="toast-body">${message}</div>
        `;

        // Add event listener for close button
        const closeBtn = toast.querySelector('[data-action="close"]');
        closeBtn.addEventListener('click', () => {
            this.remove(toast.id);
        });

        return toast;
    }

    remove(toastId) {
        const toast = this.toasts.get(toastId);
        if (toast && toast.parentNode) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
                this.toasts.delete(toastId);
            }, 250);
        }
    }

    clear() {
        this.toasts.forEach((toast, id) => this.remove(id));
    }
}

// Global instance
export const toastManager = new ToastManager();

// Legacy function for backward compatibility
export function showToast(message, type = 'info', duration = 5000) {
    return toastManager.show(message, type, duration);
}

export function removeToast(toastId) {
    return toastManager.remove(toastId);
}
