import api from './api';

export const addonService = {
  // Pass airlineId to filter results on the server
  getBaggageOptions(airlineId) {
    return api.get('api/baggage-options/', { params: { airline: airlineId } });
  },
  getMealOptions(airlineId) {
    return api.get('api/meal-options/', { params: { airline: airlineId } });
  },
  getAssistanceServices(airlineId) {
    return api.get('api/assistance-services/', { params: { airline: airlineId } });
  }
};