import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000/api/auth/'

export async function login(username, password) {
  try {
    // 1️⃣ Login to get token
    const loginRes = await axios.post(`${API_URL}token/login/`, { username, password })
    const token = loginRes.data.auth_token
    localStorage.setItem('auth_token', token)

    // 2️⃣ Set token for future requests
    axios.defaults.headers.common['Authorization'] = `Token ${token}`

    // 3️⃣ Get current user info
    const userRes = await axios.get(`${API_URL}users/me/`)
    const user = userRes.data

    return { token, user }
  } catch (error) {
    throw error
  }
}
