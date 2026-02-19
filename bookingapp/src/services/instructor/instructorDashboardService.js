import api from '../api/axios';

const BASE_URL = 'api/instructor/dashboard/';

export const instructorDashboardService = {
    // GET: Fetch all sections and instructor profile details
    async getDashboard() {
        try {
            const response = await api.get(BASE_URL);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // POST: Create a new academic section
    async createSection(payload) {
        try {
            const response = await api.post(BASE_URL, payload);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // DELETE: Remove a section by ID
    async deleteSection(id) {
        try {
            const response = await api.delete(`${BASE_URL}${id}/`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }
};
