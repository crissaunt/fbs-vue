import axios from 'axios';

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://fbs-vue.onrender.com')) + '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Automatically add the Token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken'); // Assuming you save it here on login
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export default api;