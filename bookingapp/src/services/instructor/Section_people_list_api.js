import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000/api/instructor';

export const Section_people_list_api = {
  async getEnrolledStudents(sectionId) {
    const token = localStorage.getItem('auth_token');
    const response = await axios.get(`${BASE_URL}/sections/${sectionId}/students/`, {
      headers: { 'Authorization': `Token ${token}` }
    });
    return response.data;
  }
};