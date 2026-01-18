import api from './api';

export const seatService = {
  /**
   * Fetches all seats for a specific flight schedule
   * @param {Number|String} scheduleId 
   */
  async getSeatsBySchedule(scheduleId) {
    try {
      // Using the 'api' instance already configured in your project
      const response = await api.get('api/seats/', {
        params: { schedule: scheduleId }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching seats for schedule ${scheduleId}:`, error);
      throw error;
    }
  }
};