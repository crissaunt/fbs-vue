import { defineStore } from 'pinia';

export const useNotificationStore = defineStore('notification', {
    state: () => ({
        notifications: []
    }),
    actions: {
        /**
         * Add a new notification
         * @param {Object} notification - { message, type, duration }
         * type: 'success', 'error', 'info', 'warning'
         */
        addNotification({ message, type = 'info', duration = 5000 }) {
            const id = Date.now() + Math.random();
            const notification = {
                id,
                message,
                type,
                duration
            };

            this.notifications.push(notification);

            if (duration > 0) {
                setTimeout(() => {
                    this.removeNotification(id);
                }, duration);
            }

            return id;
        },

        removeNotification(id) {
            const index = this.notifications.findIndex(n => n.id === id);
            if (index !== -1) {
                this.notifications.splice(index, 1);
            }
        }
    }
});
