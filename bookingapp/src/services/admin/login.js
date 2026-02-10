import axios from 'axios'

export async function adminLogin(username, password) {
  const response = await axios.post(
    'http://127.0.0.1:8000/api/admin/login/',
    { username, password },
    { withCredentials: true }
  )

  return response.data
}
