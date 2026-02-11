// src/services/instructor/section_details_api.js
import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000/api/instructor/sections/';

/**
 * Helper to get headers with the current token
 */
const getHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  };
};

export const section_details_api = {
  /**
   * GET: Fetch data for a specific section
   * URL format: /api/instructor/sections/5/
   */
  async getSectionDetails(sectionId) {
    try {
      const response = await axios.get(`${BASE_URL}${sectionId}/`, { 
        headers: getHeaders() 
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching section details:", error);
      throw error;
    }
  }
  
  // You can add updateSection or deleteSection here later
};