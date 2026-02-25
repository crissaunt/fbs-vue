import api from '../api/axios';

export const activityService = {
    createActivity: (sectionId, formData) => {
        return api.post(
            `api/instructor/sections/${sectionId}/activities/create/`,
            formData
        );
    }
};
