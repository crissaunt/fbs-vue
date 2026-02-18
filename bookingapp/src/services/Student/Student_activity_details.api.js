import api from '../api/axios';

export default {
  /**
   * Get detailed information about a specific activity
   * Django expects: /api/student/activities/<id>/details/
   * @param {number} activityId - The ID of the activity
   * @returns {Promise} Activity details
   */
  getActivityDetails(activityId) {
    return api.get(`api/student/activities/${activityId}/details/`);
  },

  /**
   * Submit activity completion data
   * @param {number} activityId - The ID of the activity
   * @param {object} submissionData - Data to submit
   * @returns {Promise} Submission response
   */
  submitActivity(activityId, submissionData) {
    return api.post(`api/student/activities/${activityId}/submit/`, submissionData);
  },

  /**
   * Update activity status
   * @param {number} activityId - The ID of the activity
   * @param {string} status - New status (assigned, in_progress, submitted, graded)
   * @returns {Promise} Update response
   */
  updateActivityStatus(activityId, status) {
    return api.patch(`api/student/activities/${activityId}/status/`, { status });
  },

  /**
   * Get student's submission for an activity
   * @param {number} activityId - The ID of the activity
   * @returns {Promise} Submission data
   */
  getActivitySubmission(activityId) {
    return api.get(`api/student/activities/${activityId}/submission/`);
  },

  /**
   * Save draft of activity progress
   * @param {number} activityId - The ID of the activity
   * @param {object} draftData - Draft data to save
   * @returns {Promise} Save response
   */
  saveDraft(activityId, draftData) {
    return api.post(`api/student/activities/${activityId}/draft/`, draftData);
  }
};