import axios from 'axios';
import { useNotificationStore } from '@/stores/notification';
import router from '@/router';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/', // Use env variable with fallback
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Request Interceptor: Attach Auth Token
api.interceptors.request.use(
    (config) => {
        // Check both potential token names for compatibility
        const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Global Error Handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const notificationStore = useNotificationStore();
        let message = 'An unexpected error occurred';
        let type = 'error';

        if (!error.response) {
            // Network Error
            message = 'Network error: Please check if the backend server is running.';
            console.error('Network Error:', error);
        } else {
            const status = error.response.status;
            const data = error.response.data;

            switch (status) {
                case 400:
                    message = data.error || data.message || 'Invalid request';
                    break;
                case 401:
                    message = 'Session expired. Please login again.';
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    localStorage.removeItem('user_data');
                    if (router.currentRoute.value.path !== '/login') {
                        router.push('/login');
                    }
                    break;
                case 403:
                    message = 'You do not have permission to perform this action.';
                    break;
                case 404:
                    message = 'Resource not found.';
                    break;
                case 500:
                    message = 'Internal server error. Please try again later.';
                    break;
                default:
                    message = data.error || data.message || `Error ${status}: ${error.message}`;
            }
        }

        notificationStore.addNotification({ message, type });
        return Promise.reject(error);
    }
);

export default api;
