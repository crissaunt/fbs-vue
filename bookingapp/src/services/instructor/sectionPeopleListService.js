import api from '../api/axios';

export const sectionPeopleListService = {
    async getEnrolledStudents(sectionId) {
        const response = await api.get(`api/instructor/sections/${sectionId}/students/`);
        return response.data;
    }
};
