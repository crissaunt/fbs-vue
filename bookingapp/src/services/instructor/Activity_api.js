// Activity_api.js
import api from '../api/axios';

export const ActivityService = {
  createActivity: (sectionId, formData) => {
    return api.post(
      `api/instructor/sections/${sectionId}/activities/create/`,
      formData
    );
  }
};