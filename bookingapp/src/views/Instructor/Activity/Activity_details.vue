<template>
  <div class="flex flex-col h-screen bg-gray-50 font-sans">
    <!-- Header -->
    <div class="bg-gradient-to-r from-pink-500 to-pink-400 text-white px-6 py-4 flex items-center justify-between shadow-md z-20">
      <div class="flex items-center gap-4">
        <button @click="toggleSidebar" class="p-2 hover:bg-pink-600 rounded-lg transition-colors focus:outline-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-2xl shadow-inner">🎓</div>
          <div>
            <h1 class="text-sm font-bold uppercase tracking-tight">CABAGAN STATE UNIVERSITY</h1>
            <p class="text-[10px] opacity-90">Cabagan City</p>
          </div>
        </div>
      </div>

      <div class="relative">
        <button @click="toggleDropdown" class="flex items-center gap-3 hover:bg-pink-600 p-2 rounded-lg transition-colors focus:outline-none">
          <span class="text-sm font-medium">{{ fullName }}</span>
          <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center overflow-hidden border-2 border-pink-300">
            <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-bold uppercase">{{ initials }}</div>
          </div>
        </button>
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
          <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Logout</button>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar -->
      <div :class="['bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg', sidebarOpen ? 'w-64' : 'w-20']">
        <div class="flex flex-col h-full overflow-y-auto">
          <button @click="router.push('/instructor/dashboard')" class="flex items-center py-4 hover:bg-pink-600 transition-colors border-b border-pink-400 justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
            <span v-show="sidebarOpen" class="text-lg font-medium ml-3">Home</span>
          </button>
          <div v-for="section in sections" :key="section.id" @click="goToSection(section.id)" class="flex items-center py-3 px-6 hover:bg-pink-600 cursor-pointer transition-colors border-b border-pink-400/20">
            <div class="w-8 h-8 rounded-full bg-white text-pink-500 flex items-center justify-center font-black text-xs flex-shrink-0 shadow-sm uppercase">
              {{ section.section_name ? section.section_name.charAt(0) : 'S' }}
            </div>
            <span v-show="sidebarOpen" class="ml-3 truncate text-sm font-bold tracking-wide uppercase">{{ section.section_name }}</span>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto bg-[#FDFBF7] p-8">
        <div class="max-w-5xl mx-auto">
          
          <div class="flex justify-between items-center mb-6">
            <button @click="router.back()" class="flex items-center text-gray-500 hover:text-black font-bold text-sm uppercase">
              <span class="mr-2">←</span> BACK
            </button>
            <div class="flex gap-6 text-[11px] font-bold uppercase tracking-widest">
              <span class="text-green-700 border-b-2 border-green-700 pb-1">Instruction/s</span>
              <span class="text-gray-400 cursor-pointer hover:text-gray-600">Student work</span>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-10">
            <!-- Loading State -->
            <div v-if="loading" class="text-center py-20 text-gray-400 font-bold animate-pulse uppercase tracking-widest">
              Loading activity details...
            </div>
            
            <!-- Activity Content -->
            <div v-else-if="activity">
              <div class="flex justify-between items-start mb-8">
                <div>
                  <h1 class="text-4xl font-serif font-bold text-gray-900">{{ activity.title || 'Untitled Activity' }}</h1>
                  <p class="text-sm text-gray-400 font-bold mt-2 uppercase">
                    {{ activity.section_code }} - {{ activity.section_name }}
                  </p>
                  <div class="flex gap-2 mt-3">
                    <span class="px-2 py-1 bg-blue-50 text-blue-600 text-[9px] font-black rounded uppercase border border-blue-100">Flight Booking</span>
                    <span class="px-2 py-1 bg-green-50 text-green-600 text-[9px] font-black rounded uppercase border border-green-100">
                      {{ activity.is_code_active ? 'Active' : 'Inactive' }}
                    </span>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-[10px] font-bold text-gray-400 mb-2 uppercase">
                    Due: {{ activity.due_date || 'No due date' }}
                  </p>
                  <div v-if="activity.is_code_active" class="bg-green-100 text-green-700 px-4 py-2 rounded-lg text-xs font-black border border-green-200">
                    Active Code: {{ activity.activity_code }}
                  </div>
                  <div v-else class="bg-gray-100 text-gray-400 px-4 py-2 rounded-lg text-xs font-black">
                    Activity code: Not yet Activated
                  </div>
                </div>
              </div>

              <hr class="mb-8 border-gray-100" />

              <!-- Instructions -->
              <div class="mb-10">
                <h3 class="text-xs font-black uppercase text-gray-800 mb-4 tracking-widest">Instructions</h3>
                <div class="border border-gray-100 bg-gray-50/50 p-6 rounded-xl italic text-gray-600 text-sm leading-relaxed whitespace-pre-wrap">
                  {{ activity.instructions || 'No instructions provided.' }}
                </div>
              </div>

              <!-- Flight Requirements -->
              <div class="mb-10">
                <h3 class="text-sm font-bold mb-4 text-gray-800">Flight Requirements</h3>
                <div class="flex gap-2 mb-6">
                  <span class="bg-[#FFC145] px-6 py-1.5 rounded-full text-[10px] font-black uppercase">
                    {{ activity.required_trip_type || 'N/A' }}
                  </span>
                  <span class="bg-[#0D3111] text-white px-6 py-1.5 rounded-full text-[10px] font-black uppercase">
                    {{ activity.required_travel_class || 'N/A' }}
                  </span>
                </div>

                <div class="border border-yellow-200 rounded-3xl py-6 px-10 flex items-center justify-between bg-white relative overflow-hidden">
                  <div class="text-center">
                    <p class="text-[9px] text-gray-400 uppercase font-bold tracking-widest">From</p>
                    <p class="text-xl font-black text-gray-900">{{ activity.required_origin || '-' }}</p>
                  </div>
                  <div class="text-center">
                    <p class="text-[9px] text-gray-400 uppercase font-bold tracking-widest">To</p>
                    <p class="text-xl font-black text-gray-900">{{ activity.required_destination || '-' }}</p>
                  </div>
                  <div class="h-10 w-[1px] bg-gray-200 mx-2"></div>
                  <div class="text-center">
                    <p class="text-[9px] text-gray-400 uppercase font-bold tracking-widest">Depart</p>
                    <p class="text-sm font-bold text-gray-800">{{ activity.required_departure_date || 'N/A' }}</p>
                  </div>
                  <div class="text-center">
                    <p class="text-[9px] text-gray-400 uppercase font-bold tracking-widest">Return</p>
                    <p class="text-sm font-bold text-gray-800">{{ activity.required_return_date || 'N/A' }}</p>
                  </div>
                  <div class="h-10 w-[1px] bg-gray-200 mx-2"></div>
                  <div class="text-center">
                    <p class="text-[9px] text-gray-400 uppercase font-bold tracking-widest">Passenger</p>
                    <p class="text-[10px] text-gray-700">
                      Adult: <b>{{ activity.required_passengers || 0 }}</b> 
                      child: <b>{{ activity.required_children || 0 }}</b> 
                      infant: <b>{{ activity.required_infants || 0 }}</b>
                    </p>
                  </div>
                </div>
              </div>

              <!-- Passenger Information -->
              <div class="border border-gray-200 rounded-xl p-8 bg-white">
                <h3 class="text-lg font-bold mb-8 text-gray-800">Passenger Information</h3>
                <div v-if="activity.passengers && activity.passengers.length > 0">
                  <div v-for="(p, index) in activity.passengers" :key="index" class="mb-10 last:mb-0 border-b border-gray-50 pb-8 last:border-0">
                    <div class="flex justify-between items-center mb-6">
                      <h4 class="font-black text-sm text-gray-900 uppercase tracking-tight">
                        Passenger {{ index + 1 }} ({{ p.type || 'Adult' }})
                      </h4>
                      <span v-if="p.seat_preference" class="text-[10px] font-bold uppercase tracking-widest text-gray-800">
                        seat preference: <span class="text-gray-400">{{ p.seat_preference }}</span>
                      </span>
                    </div>
                    
                    <!-- Dynamic Passenger Fields Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                      <!-- Gender -->
                      <div v-if="hasValue(p.gender)">
                        <label class="text-[9px] font-black text-red-500 uppercase">Gender*</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                          {{ p.gender }}
                        </div>
                      </div>
                      
                      <!-- First Name -->
                      <div v-if="hasValue(p.first_name)">
                        <label class="text-[9px] font-black text-red-500 uppercase">First Name*</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                          {{ p.first_name }}
                        </div>
                      </div>
                      
                      <!-- Middle Name -->
                      <div v-if="hasValue(p.middle_name)">
                        <label class="text-[9px] font-black text-gray-400 uppercase">Middle Name</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                          {{ p.middle_name }}
                        </div>
                      </div>
                      
                      <!-- Last Name -->
                      <div v-if="hasValue(p.last_name)">
                        <label class="text-[9px] font-black text-red-500 uppercase">Last Name*</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                          {{ p.last_name }}
                        </div>
                      </div>
                      
                      <!-- Date of Birth -->
                      <div v-if="hasValue(p.date_of_birth)">
                        <label class="text-[9px] font-black text-red-500 uppercase">Date of Birth*</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                          {{ formatDate(p.date_of_birth) }}
                        </div>
                      </div>
                      
                      <!-- Nationality -->
                      <div v-if="hasValue(p.nationality)">
                        <label class="text-[9px] font-black text-red-500 uppercase">Nationality*</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                          {{ p.nationality }}
                        </div>
                      </div>
                      
                      <!-- Passport Number -->
                      <div v-if="hasValue(p.passport_number)">
                        <label class="text-[9px] font-black text-red-500 uppercase">Passport Number*</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                          {{ p.passport_number }}
                        </div>
                      </div>
                      
                      <!-- Email -->
                      <div v-if="hasValue(p.email)">
                        <label class="text-[9px] font-black text-gray-400 uppercase">Email</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                          {{ p.email }}
                        </div>
                      </div>
                      
                      <!-- Phone -->
                      <div v-if="hasValue(p.phone)">
                        <label class="text-[9px] font-black text-gray-400 uppercase">Phone</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                          {{ p.phone }}
                        </div>
                      </div>
                      
                      <!-- Special Requirements -->
                      <div v-if="hasValue(p.special_requirements)" class="md:col-span-4">
                        <label class="text-[9px] font-black text-gray-400 uppercase">Special Requirements</label>
                        <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                          {{ p.special_requirements }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-10 text-gray-400">
                  No passenger information available.
                </div>
              </div>

              <!-- Activate Button -->
              <div class="mt-12 flex justify-center">
                <button 
                  @click="handleActivation"
                  :disabled="activity.is_code_active || activating"
                  class="w-full max-w-lg bg-[#FFC145] hover:bg-yellow-500 disabled:bg-gray-200 disabled:text-gray-400 py-4 rounded-xl font-black text-sm uppercase tracking-widest transition-all shadow-md active:scale-95 disabled:cursor-not-allowed"
                >
                  {{ activating ? 'Activating...' : (activity.is_code_active ? 'Already Activated' : 'Activate') }}
                </button>
              </div>
            </div>

            <!-- Error State -->
            <div v-else class="text-center py-20">
              <p class="text-red-400 font-bold uppercase mb-2">Failed to load activity details.</p>
              <p class="text-gray-400 text-xs italic mb-4">{{ errorMessage }}</p>
              <button 
                @click="fetchData" 
                class="px-6 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-white p-10 rounded-2xl text-center shadow-2xl max-w-sm w-full">
        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">✅</div>
        <h2 class="text-xl font-black mb-2 uppercase text-gray-900">Activity Activated</h2>
        <p class="text-gray-500 text-xs mb-6 leading-relaxed">Share this code with your students to begin the activity:</p>
        <div class="bg-gray-100 text-4xl font-mono font-black py-4 rounded-xl tracking-widest text-pink-600 border-2 border-dashed border-gray-200 mb-8 uppercase">
          {{ activity?.activity_code }}
        </div>
        <button @click="showSuccessModal = false" class="w-full bg-black text-white py-3 rounded-lg font-bold uppercase text-xs tracking-widest">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Instructor_Dashboard_api } from '@/services/instructor/Instructor_Dashboard_api'
import { Activity_details_api } from '@/services/instructor/Activity_details_api'

const router = useRouter()
const route = useRoute()

// --- UI State ---
const sidebarOpen = ref(false) 
const dropdownOpen = ref(false)
const showSuccessModal = ref(false)
const loading = ref(true)
const activating = ref(false)
const errorMessage = ref('')

// --- Data State ---
const sections = ref([])
const user = ref({ first_name: '', last_name: '', username: '' })
const activity = ref(null)

// --- Computed ---
const fullName = computed(() => {
  if (user.value.first_name && user.value.last_name) return `${user.value.first_name} ${user.value.last_name}`
  return user.value.username || 'Instructor'
})

const initials = computed(() => {
  const u = user.value.username || 'I'
  return u[0]?.toUpperCase() || 'I'
})

// --- Helper Functions ---
const hasValue = (value) => {
  return value !== null && value !== undefined && value !== '' && value !== '-'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return dateString
  }
}

// --- Actions ---
const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

const handleLogout = () => {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user_data')
  router.push('/login')
}

const fetchData = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    // 1. Fetch Dashboard data for sidebar sections and user info
    const dashData = await Instructor_Dashboard_api.getDashboard()
    sections.value = dashData.sections || []
    user.value = dashData.user || { first_name: '', last_name: '', username: '' }

    // 2. Fetch Activity details
    const activityId = route.params.activityId 
    
    if (!activityId) {
      errorMessage.value = "No activity ID found in URL"
      console.error("No activityId found in route parameters")
      activity.value = null
      return
    }

    console.log('Fetching activity with ID:', activityId)
    const data = await Activity_details_api.getActivity(activityId)
    console.log('Activity data received:', data)
    activity.value = data
    
  } catch (error) {
    console.error("Fetch Error:", error)
    errorMessage.value = error.response?.data?.error || error.response?.data?.detail || error.message || 'Unknown error occurred'
    activity.value = null
  } finally {
    loading.value = false
  }
}

const handleActivation = async () => {
  if (!activity.value || activating.value) return
  
  activating.value = true
  
  try {
    console.log('Activating activity:', activity.value.id)
    const res = await Activity_details_api.activateActivity(activity.value.id)
    
    console.log('Activation response:', res)
    
    // Update activity data with the response
    activity.value.activity_code = res.activity_code
    activity.value.is_code_active = true
    
    showSuccessModal.value = true
  } catch (error) {
    console.error("Activation error:", error)
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Failed to activate activity.'
    alert(errorMsg)
  } finally {
    activating.value = false
  }
}

onMounted(() => {
  console.log('Component mounted, route params:', route.params)
  fetchData()
})
</script>