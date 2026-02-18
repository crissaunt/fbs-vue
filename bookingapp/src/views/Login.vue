<template>
  <div
    class="min-h-screen bg-cover bg-center bg-no-repeat"
    :style="backgroundStyle"
  >
    <div class="min-h-screen bg-black/20">
      <header class="px-6 py-4 flex items-center justify-between" style="background-color:whitesmoke ;">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background-color: #FF579A;">
            <span class="font-bold text-xl" style="color: #F9FAFB ;">CS</span>
          </div>
          <div style="color: #0E8028;">
            <div class="font-bold text-lg">CARAGA STATE UNIVERSITY</div>
            <div class="text-xs">CABADBARAN CITY</div>
          </div>
        </div>
        <div class="flex gap-3">
        <router-link to="/register">
          <button class="font-semibold px-6 py-2 rounded" style="background-color: #FF579A; color: #F9FAFB;">
            Register
          </button>
        </router-link>

        <button class="border-2 font-semibold px-6 py-2 rounded" style="border-color: #FF579A; background-color: transparent; color: #0E8028 ;">
          Contact Us
        </button>
      </div>
      </header>

      <div class="container mx-auto px-6 py-12">
        <div class="grid lg:grid-cols-3 gap-8 items-start">
          <div class="lg:col-span-2 space-y-8">
            <div style="color: #F9FAFB;">
              <h1 class="text-4xl lg:text-5xl font-bold mb-4 leading-tight">
                TourEd Academy: Flight Booking and Tourism Training Platform
              </h1>
              <p class="leading-relaxed">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
              </p>
            </div>
          </div>

          <div class="lg:col-span-1">
            <div class="rounded-lg shadow-2xl p-8" style="background-color: #F9FAFB;">
              <h2 class="text-2xl font-bold text-gray-800 mb-2 text-center">Login Here!</h2>
              <p class="text-gray-500 text-sm text-center mb-8">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit.
              </p>

              <div class="space-y-6">
                <div>
                  <label class="block text-gray-700 font-semibold mb-2">Username</label>
                  <input
                    v-model="username"
                    type="text"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none"
                    placeholder="Enter username"
                  />
                </div>

                <div>
                  <label class="block text-gray-700 font-semibold mb-2">Password</label>
                  <input
                    v-model="password"
                    type="password"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none"
                    placeholder="Enter password"
                    @keyup.enter="handleLogin"
                  />
                </div>

                <button
                  @click="handleLogin"
                  :disabled="loading"
                  class="w-full font-bold py-3 rounded-lg transition-opacity"
                  :class="loading ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-90'"
                  style="background-color: #FF579A; color: #F9FAFB;"
                >
                  <span v-if="loading">Logging in...</span>
                  <span v-else>Login</span>
                </button>

                <!-- Error Message -->
                <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p class="text-red-700 text-sm text-center">{{ error }}</p>
                </div>

                <!-- Success Message -->
                <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-lg p-3">
                  <p class="text-green-700 text-sm text-center">{{ successMessage }}</p>
                </div>

                <div class="text-center">
                  <a href="#" class="text-sm" style="color: #FF579A;">
                    forgot password?
                  </a>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import bgImage from '@/assets/image/bg-cthm.svg'
import api from '@/services/api/axios'

export default {
  name: 'InstructorLogin',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null,
      successMessage: ''
    }
  },
  computed: {
    backgroundStyle() {
      return {
        backgroundImage: `url(${bgImage})`
      }
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = null
      this.successMessage = ''

      try {
        console.log('🔐 Attempting login for:', this.username)
        
        // 1. Send Login Request
        const response = await api.post(
          'api/login/', 
          {
            username: this.username,
            password: this.password
          }
        )

        console.log("LOGIN SUCCESS:", response.data)

        // 2. Extract Data
        const { token, user, dashboard_route } = response.data
        
        // ✅ CRITICAL FIX: Store token with BOTH keys for compatibility
        if (token) {
          // Store with primary key (used by Student_dashboard_api.js)
          localStorage.setItem('token', token)
          // Also store with auth_token key (used by router)
          localStorage.setItem('auth_token', token)
          
          console.log('✅ Token stored successfully:', token)
          console.log('✅ Verification - token:', localStorage.getItem('token'))
          console.log('✅ Verification - auth_token:', localStorage.getItem('auth_token'))
        } else {
          console.error('❌ No token received from server!')
        }
        
        // 3. Save User Data
        if (user) {
          localStorage.setItem('user', JSON.stringify(user))
          localStorage.setItem('user_data', JSON.stringify(user)) // Keep for compatibility
          console.log('✅ User data stored:', user)
        }

        // 4. Show success message
        this.successMessage = 'Login successful! Redirecting...'

        // 5. Redirect after short delay to ensure storage is complete
        setTimeout(() => {
          if (dashboard_route) {
            console.log('🔄 Redirecting to:', dashboard_route)
            this.$router.push(dashboard_route)
          } else {
            console.error('❌ No dashboard route provided')
            this.error = "Unknown role or route."
          }
        }, 1000) // 1 second delay to show success message and ensure storage

      } catch (err) {
        console.error('❌ LOGIN ERROR:', err)
        
        if (err.response) {
          const data = err.response.data
          this.error = data.error || data.detail || data.message || "Invalid credentials."
          console.error('❌ Server error:', this.error)
        } else if (err.request) {
          this.error = "Unable to connect to the server. Please check if the server is running."
          console.error('❌ Network error - no response from server')
        } else {
          this.error = "An unexpected error occurred. Please try again."
          console.error('❌ Unexpected error:', err.message)
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>