import api from '../api/axios';

export const Section_people_list_api = {
  async getEnrolledStudents(sectionId) {
    const response = await api.get(`api/instructor/sections/${sectionId}/students/`);
    return response.data;
  }
};