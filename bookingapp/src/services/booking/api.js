import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/flightapp/'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.message);
    if (error.code === 'ERR_NETWORK') {
      console.error('Backend server is not running. Please start the Django server.');
    }
    return Promise.reject(error);
  }
);

export default api