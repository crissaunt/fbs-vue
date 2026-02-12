import api from './api';

export default {
  getSchedules(params) {
    return api.get('api/schedules/', { params });
  },
  
  getSeatClassFeatures() {
    return api.get('seat-class-features/');
  },
  getPricePrediction(flightData) {
    return api.post('api/predict-price/', flightData);
  }
};