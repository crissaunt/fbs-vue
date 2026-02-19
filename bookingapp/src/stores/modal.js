import { defineStore } from 'pinia';

export const useModalStore = defineStore('modal', {
    state: () => ({
        isOpen: false,
        type: 'confirm', // 'confirm', 'alert', 'custom'
        title: '',
        message: '',
        confirmText: 'Confirm',
        cancelText: 'Cancel',
        resolvePromise: null,
    }),

    actions: {
        /**
         * Show a confirmation modal
         * @param {Object} options - { title, message, confirmText, cancelText }
         * @returns {Promise<boolean>}
         */
        confirm(options = {}) {
            this.isOpen = true;
            this.type = 'confirm';
            this.title = options.title || 'Confirm Action';
            this.message = options.message || 'Are you sure you want to proceed?';
            this.confirmText = options.confirmText || 'Confirm';
            this.cancelText = options.cancelText || 'Cancel';

            return new Promise((resolve) => {
                this.resolvePromise = resolve;
            });
        },

        /**
         * Close the modal and resolve with a value
         * @param {any} value 
         */
        close(value = false) {
            this.isOpen = false;
            if (this.resolvePromise) {
                this.resolvePromise(value);
                this.resolvePromise = null;
            }
        }
    }
});
