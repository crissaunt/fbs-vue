import api from '@/services/api/axios';

export const sectionSettingsService = {
    updateSectionSettings(sectionId, data) {
        return api.patch(`/instructor/sections/${sectionId}/update/`, data);
    }
};
