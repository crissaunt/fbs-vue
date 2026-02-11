// src/services/instructor/Activity_details_api.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Get authentication token from localStorage
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  };
};

export const Activity_details_api = {
  /**
   * Get activity details by ID
   * @param {number} id - Activity ID
   * @returns {Promise} Activity data
   */
  async getActivity(id) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/instructor/activities/${id}/`,
        { headers: getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching activity:', error);
      throw error;
    }
  },

  /**
   * Activate an activity and generate activity code
   * @param {number} activityId - Activity ID to activate
   * @returns {Promise} Activation response with activity code
   */
  async activateActivity(activityId) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/instructor/activity/${activityId}/activate/`,
        {},
        { headers: getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error activating activity:', error);
      throw error;
    }
  }
};