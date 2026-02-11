import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const registerService = {
  register(formData) {
    // This sends all data: username, email, password, first_name, last_name, id_number, role
    return axios.post(`${API_BASE_URL}/register/`, formData);
  }
};