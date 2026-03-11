import api from '../api/axios';

export const activityDetailsService = {
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
            throw error;
        }
    },

    /**
     * Activate an activity and generate/reuse activity code, 
     * optionally assigning it to specific students.
     * @param {number} activityId - Activity ID to activate
     * @param {Array<number>} studentIds - Array of student IDs to assign the activity to
     * @returns {Promise} Activation response with activity code
     */
    async activateActivity(activityId, studentIds = []) {
        try {
            const response = await api.post(`api/instructor/activity/${activityId}/activate/`, {
                student_ids: studentIds
            });
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    /**
     * Get students who are eligible to receive this activity (enrolled but not yet assigned)
     * @param {number} activityId - Activity ID
     * @returns {Promise} List of eligible students
     */
    async getEligibleStudents(activityId) {
        try {
            const response = await api.get(`api/instructor/activity/${activityId}/eligible-students/`);
            return response.data;
        } catch (error) {
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
    },

    /**
     * Save a grade for a student submission
     * @param {number} activityId - Activity ID
     * @param {number} studentId - Student ID
     * @param {object} data - Grade data {grade, feedback}
     */
    async saveGrade(activityId, studentId, data) {
        try {
            const response = await api.post(`api/instructor/activities/${activityId}/submissions/${studentId}/grade/`, data);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    /**
     * Release all scores for an activity
     * @param {number} activityId - Activity ID
     * @returns {Promise} Release response
     */
    async releaseGrades(activityId) {
        try {
            const response = await api.post(`api/instructor/activities/${activityId}/release-grades/`, {});
            return response.data;
        } catch (error) {
            throw error;
        }
    }
};
