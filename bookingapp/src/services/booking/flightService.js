import api from './api';

export default {
  getSchedules(params) {
    return api.get('api/schedules/', { params });
  },
  
  getSeatClassFeatures() {
    return api.get('seat-class-features/');
  }
};