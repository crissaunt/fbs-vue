import api from './api/axios';

export const registerService = {
  register(formData) {
    // This sends all data: username, email, password, first_name, last_name, id_number, role
    return api.post('api/register/', formData);
  }
};