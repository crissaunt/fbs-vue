// src/services/instructor/section_details_api.js
import api from '../api/axios';

export const section_details_api = {
  /**
   * GET: Fetch data for a specific section
   * URL format: /api/instructor/sections/5/
   */
  async getSectionDetails(sectionId) {
    try {
      const response = await api.get(`api/instructor/sections/${sectionId}/`);
      return response.data;
    } catch (error) {
      // Handled by global interceptor
      throw error;
    }
  }

  // You can add updateSection or deleteSection here later
};