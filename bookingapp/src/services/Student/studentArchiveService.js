import api from '../api/axios';

export const studentArchiveService = {
    // GET: Fetch all archived sections the student was enrolled in
    async getArchivedSections() {
        try {
            const response = await api.get('api/student/archived-sections/');
            return response.data;
        } catch (error) {
            throw error;
        }
    }
};
