// src/services/instructor/Instructor_Dashboard_api.js
import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000/api/instructor/dashboard/';

/**
 * Helper to retrieve the current auth token and set headers
 */
const getHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
};

export const Instructor_Dashboard_api = {
  // GET: Fetch all sections and instructor profile details
  async getDashboard() {
    try {
      const response = await axios.get(BASE_URL, { headers: getHeaders() });
      return response.data;
    } catch (error) {
      console.error("API Error (GET):", error);
      throw error;
    }
  },

  // POST: Create a new academic section
  async createSection(payload) {
    try {
      const response = await axios.post(BASE_URL, payload, { headers: getHeaders() });
      return response.data;
    } catch (error) {
      console.error("API Error (POST):", error);
      throw error;
    }
  },

  // DELETE: Remove a section by ID
  async deleteSection(id) {
    try {
      const response = await axios.delete(`${BASE_URL}${id}/`, { headers: getHeaders() });
      return response.data;
    } catch (error) {
      console.error("API Error (DELETE):", error);
      throw error;
    }
  }
};