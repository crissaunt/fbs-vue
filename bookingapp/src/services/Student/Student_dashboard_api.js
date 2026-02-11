import axios from 'axios';

// Create axios instance with correct base URL
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor - adds token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    console.log('📤 API Request:', config.method.toUpperCase(), config.url);
    console.log('🔑 Token:', token ? 'Present' : 'Missing');
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - ONLY logs, does NOT redirect
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    console.log('📦 Response Data:', response.data);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('❌ API Error:', error.response.status);
      console.error('📋 Error Details:', error.response.data);
      console.error('🔗 Failed URL:', error.config.url);
      
      // Log different error types but DON'T auto-redirect
      if (error.response.status === 401) {
        console.error('🔒 Unauthorized - Invalid or expired token');
      } else if (error.response.status === 403) {
        console.error('🚫 Forbidden - Access denied (wrong role or permissions)');
      } else if (error.response.status === 404) {
        console.error('❓ Not Found - Endpoint does not exist');
      } else if (error.response.status === 500) {
        console.error('💥 Server Error');
      }
    } else if (error.request) {
      console.error('📡 No Response - Server may be down');
      console.error('Request details:', error.request);
    } else {
      console.error('⚠️ Error:', error.message);
    }
    
    // Return the error so component can handle it
    return Promise.reject(error);
  }
);

export default {
  /**
   * Get student dashboard data
   * URL: GET /api/student/dashboard/data/
   */
  getStudentDashboard() {
    console.log('🎯 Calling: GET /student/dashboard/data/');
    return apiClient.get('/student/dashboard/data/');
  },

  /**
   * Get specific section details
   * URL: GET /api/student/section/{id}/
   */
  getSectionDetails(sectionId) {
    return apiClient.get(`/student/section/${sectionId}/`);
  },

  /**
   * Get specific activity details
   * URL: GET /api/student/activity/{id}/
   */
  getActivityDetails(activityId) {
    return apiClient.get(`/student/activity/${activityId}/`);
  },

  /**
   * Submit activity work
   * URL: POST /api/student/activity/{id}/submit/
   */
  submitActivity(activityId, data) {
    return apiClient.post(`/student/activity/${activityId}/submit/`, data);
  }
};