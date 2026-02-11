import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    // ✅ Check both possible token keys
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
    
    if (token) {
      config.headers.Authorization = `Token ${token}`;
      console.log('🔑 Adding auth token to request');
      console.log('📡 Full Request URL:', config.baseURL + config.url);
    } else {
      console.warn('⚠️ No auth token found in localStorage');
    }
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      status: response.status,
      url: response.config.url,
      dataKeys: Object.keys(response.data || {})
    });
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('❌ API Error Response:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        url: error.config?.url
      });
    } else if (error.request) {
      console.error('❌ No response from server - Is Django running?');
      console.error('🔌 Attempted URL:', error.config?.baseURL + error.config?.url);
    } else {
      console.error('❌ Request setup error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default {
  /**
   * Get detailed information about a specific activity
   * ✅ FIXED: Correct endpoint matching Django URL pattern
   * Django expects: /api/student/activities/<id>/details/
   * @param {number} activityId - The ID of the activity
   * @returns {Promise} Activity details
   */
  getActivityDetails(activityId) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`📡 API CALL: Get Activity Details`);
    console.log(`${'='.repeat(60)}`);
    console.log(`Activity ID: ${activityId}`);
    console.log(`Full URL: ${API_URL}/student/activities/${activityId}/details/`);
    console.log(`Token exists: ${!!(localStorage.getItem('token') || localStorage.getItem('auth_token'))}`);
    console.log(`${'='.repeat(60)}\n`);
    
    // ✅ CORRECTED: Changed from /student/activity/ to /student/activities/{id}/details/
    return apiClient.get(`/student/activities/${activityId}/details/`);
  },

  /**
   * Submit activity completion data
   * @param {number} activityId - The ID of the activity
   * @param {object} submissionData - Data to submit
   * @returns {Promise} Submission response
   */
  submitActivity(activityId, submissionData) {
    console.log(`📤 Submitting activity ${activityId}`);
    return apiClient.post(`/student/activities/${activityId}/submit/`, submissionData);
  },

  /**
   * Update activity status
   * @param {number} activityId - The ID of the activity
   * @param {string} status - New status (assigned, in_progress, submitted, graded)
   * @returns {Promise} Update response
   */
  updateActivityStatus(activityId, status) {
    console.log(`🔄 Updating activity ${activityId} status to: ${status}`);
    return apiClient.patch(`/student/activities/${activityId}/status/`, { status });
  },

  /**
   * Get student's submission for an activity
   * @param {number} activityId - The ID of the activity
   * @returns {Promise} Submission data
   */
  getActivitySubmission(activityId) {
    console.log(`📥 Fetching submission for activity: ${activityId}`);
    return apiClient.get(`/student/activities/${activityId}/submission/`);
  },

  /**
   * Save draft of activity progress
   * @param {number} activityId - The ID of the activity
   * @param {object} draftData - Draft data to save
   * @returns {Promise} Save response
   */
  saveDraft(activityId, draftData) {
    console.log(`💾 Saving draft for activity ${activityId}`);
    return apiClient.post(`/student/activities/${activityId}/draft/`, draftData);
  }
};