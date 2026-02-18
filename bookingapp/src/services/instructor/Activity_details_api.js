// src/services/instructor/Activity_details_api.js
import api from '../api/axios';

export const Activity_details_api = {
  /**
   * Get activity details by ID
   * @param {number} id - Activity ID
   * @returns {Promise} Activity data
   */
  async getActivity(id) {
    try {
      const response = await api.get(`api/instructor/activities/${id}/`);
      return response.data;
    } catch (error) {
      // Handled by global interceptor
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
      const response = await api.post(`api/instructor/activity/${activityId}/activate/`, {});
      return response.data;
    } catch (error) {
      // Handled by global interceptor
      throw error;
    }
  },

  /**
   * Get all student submissions for an activity
   * @param {number} activityId - Activity ID
   * @returns {Promise} Submissions data
   */
  async getSubmissions(activityId) {
    try {
      const response = await api.get(`api/instructor/activities/${activityId}/submissions/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};