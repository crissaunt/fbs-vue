// Activity_api.js
import axios from 'axios';

export const ActivityService = {
  createActivity: (sectionId, formData) => {
    const token = localStorage.getItem('auth_token');
    return axios.post(
      `http://127.0.0.1:8000/api/instructor/sections/${sectionId}/activities/create/`, 
      formData,
      {
        headers: {
          'Authorization': `Token ${token}`
        }
      }
    );
  }
};