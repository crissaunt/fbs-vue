import api from '../api/axios';

export async function login(username, password) {
  try {
    // 1️⃣ Login to get token
    // The centralized axios instance handles baseURL, so we use relative paths
    const loginRes = await api.post('api/auth/token/login/', { username, password })
    const token = loginRes.data.auth_token
    localStorage.setItem('auth_token', token)

    // 2️⃣ Get current user info
    // The request interceptor in centralized axios will automatically 
    // attach the 'Authorization' header for this and future requests.
    const userRes = await api.get('api/auth/users/me/')
    const user = userRes.data

    return { token, user }
  } catch (error) {
    // Error is caught and reported by the global interceptor, 
    // but we re-throw it so the component can handle local logic (e.g. loading state)
    throw error
  }
}
