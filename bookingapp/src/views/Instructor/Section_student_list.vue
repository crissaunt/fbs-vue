<template>
  <div class="flex flex-col h-screen bg-[#FDFCF7] font-sans">
    <div class="bg-gradient-to-r from-pink-500 to-pink-400 text-white px-6 py-2.5 flex items-center justify-between shadow-sm z-20 border-b border-pink-400">
      <div class="flex items-center gap-4">
        <button @click="toggleSidebar" class="p-1.5 hover:bg-pink-600 rounded-md transition-colors focus:outline-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-xl shadow-inner">🎓</div>
          <div>
            <h1 class="text-[10px] font-bold uppercase tracking-widest text-white/90">Cabagan State University</h1>
            <p class="text-[9px] uppercase tracking-tighter opacity-60">Faculty Portal</p>
          </div>
        </div>
      </div>

      <div class="relative">
        <button @click="toggleDropdown" class="flex items-center gap-2 hover:bg-pink-600 p-1.5 rounded-md transition-colors focus:outline-none">
          <span class="text-xs font-medium">{{ userFullName }}</span>
          <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center overflow-hidden border border-pink-300">
             <div class="w-full h-full bg-gray-300 rounded-full flex items-center justify-center text-gray-600 text-xs font-bold uppercase">{{ initials }}</div>
          </div>
        </button>
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
           <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium">Logout</button>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <div :class="['bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg border-r border-pink-400/20', sidebarOpen ? 'w-56' : 'w-16']">
        <div class="flex flex-col h-full overflow-y-auto">
           <button @click="$router.push('/instructor/dashboard')" class="flex items-center py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/20 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
             </svg>
             <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Home</span>
           </button>

           <button @click="$router.push('/instructor/logs')" class="flex items-center py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/20 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
             </svg>
             <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Activity Logs</span>
           </button>
           <div 
             v-for="sidebarSection in sidebarSections" 
             :key="sidebarSection.id" 
             @click="goToSection(sidebarSection.id)" 
             :class="[
               'flex items-center py-2.5 hover:bg-pink-600 cursor-pointer transition-colors border-b border-pink-400/10',
               sidebarOpen ? 'px-5' : 'justify-center',
               route.params.id == sidebarSection.id ? 'bg-pink-700' : ''
             ]"
           >
              <div class="w-7 h-7 rounded-full bg-white text-pink-500 flex items-center justify-center font-bold text-[10px] flex-shrink-0 shadow-sm uppercase">
                {{ sidebarSection.section_name.charAt(0) }}
              </div>
              <span v-show="sidebarOpen" class="ml-3 truncate text-[11px] font-bold tracking-wider uppercase text-white">{{ sidebarSection.section_name }}</span>
           </div>
        </div>
      </div>

      <div class="flex-1 overflow-auto bg-[#FDFCF7]">
        <div class="p-8">
          <div>
            <h2 class="text-2xl font-light text-gray-900 tracking-wide">
              {{ section?.section_code }} - {{ section?.section_name }}
            </h2><br>
          </div>

          <div class="flex items-center gap-8 border-b border-gray-300 mb-8 px-2 relative">
            <button @click="$router.push(`/instructor/section/${route.params.id}`)" class="pb-3 text-sm font-bold uppercase text-gray-400 hover:text-gray-600 tracking-wider">Assessments</button>
            <button class="pb-3 text-sm font-bold uppercase border-b-4 border-[#0E8028] text-gray-800 tracking-wider">Student</button>
            <button class="pb-3 text-sm font-bold uppercase text-gray-400 hover:text-gray-600 tracking-wider">Section Settings</button>
            
            <div class="ml-auto flex items-center gap-3 mb-2">
              <input type="file" ref="fileInput" @change="handleCSVUpload" accept=".csv" class="hidden">
              
              <button @click="triggerFileUpload" class="bg-blue-600 text-white px-5 py-2.5 rounded-lg font-bold text-xs uppercase tracking-widest shadow-md hover:bg-blue-700 active:scale-95 transition-all flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Import CSV
              </button>

              <button @click="handleClearAll" class="bg-red-500 text-white px-5 py-2.5 rounded-lg font-bold text-xs uppercase tracking-widest shadow-md hover:bg-red-600 active:scale-95 transition-all flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Clear All
              </button>

              <button @click="openEnrollModal" class="bg-[#F4D03F] text-[#0A3D16] px-6 py-2.5 rounded-lg font-bold text-xs uppercase tracking-widest shadow-md hover:translate-y-[-1px] active:scale-95 transition-all">Enroll Student</button>
            </div>
          </div>

          <div class="max-w-6xl mx-auto space-y-12">
  
            <section>
              <div class="flex items-center justify-between border-b-2 border-green-700 pb-2 mb-4">
                <h3 class="text-xl font-bold text-green-800 uppercase tracking-wide">Instructor</h3>
              </div>
              
              <div class="flex items-center gap-4 px-4 py-3 bg-white rounded-lg border border-gray-100 shadow-sm">
                <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center border border-gray-200">
                  <span class="text-gray-500 font-bold text-sm">{{ initials }}</span>
                </div>
                <div>
                  <p class="font-semibold text-gray-900 leading-tight">{{ userFullName }}</p>
                  <p class="text-[11px] text-gray-500 uppercase tracking-wider">Instructor in Charge</p>
                </div>
              </div>
            </section>

            <section>
              <div class="flex items-center justify-between border-b-2 border-green-700 pb-2 mb-0">
                <h3 class="text-xl font-bold text-green-800 uppercase tracking-wide">Students</h3>
                <span class="text-sm font-medium text-gray-500">{{ enrolledStudents.length }} enrolled</span>
              </div>
              
              <div class="bg-white rounded-b-lg shadow-sm border border-gray-100 divide-y divide-gray-100">
                <div v-for="student in enrolledStudents" :key="student.id" 
                    class="group flex items-center justify-between p-4 px-6 hover:bg-gray-50 transition-colors">
                  
                  <div class="flex items-center gap-4">
                    <div class="w-9 h-9 bg-pink-50 rounded-full flex items-center justify-center text-pink-600 font-bold text-xs border border-pink-100">
                      {{ student.first_name.charAt(0) }}
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 items-center">
                      <p class="font-medium text-gray-900">{{ student.first_name }} {{ student.last_name }}</p>
                      <p class="text-xs text-gray-400 font-mono hidden md:block">#{{ student.student_number }}</p>
                    </div>
                  </div>

                  <div class="flex items-center gap-6">
                    <span class="text-[11px] text-gray-400 font-medium uppercase tracking-tight hidden sm:block">
                      Joined {{ student.enrolled_at }}
                    </span>
                    <button @click="removeStudent(student)" title="Unenroll Student" class="text-gray-300 hover:text-red-500 transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                <div v-if="enrolledStudents.length === 0" class="p-12 text-center">
                  <p class="text-gray-400 text-sm italic">No students currently enrolled in this section.</p>
                </div>
              </div>
            </section>

          </div>

          </div>
        </div>
      </div>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-[#FF579A] p-4 text-white flex justify-between items-center">
          <h3 class="text-xs font-bold tracking-widest uppercase">Enroll Student</h3>
          <button @click="isModalOpen = false" class="hover:text-pink-100 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-8">
          <div class="mb-6">
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Enter Student Number</label>
            <input 
              v-model="studentNumberInput"
              type="text" 
              placeholder="e.g. 21-0001"
              class="w-full p-3 border-2 border-gray-100 rounded-lg focus:border-pink-500 outline-none transition-all text-sm font-medium"
            />
          </div>
          <div class="flex gap-4">
            <button @click="isModalOpen = false" class="flex-1 py-3 text-gray-400 font-bold hover:bg-gray-50 rounded-xl transition-colors uppercase text-xs tracking-widest">Cancel</button>
            <button @click="submitEnrollment" :disabled="loading" class="flex-1 py-3 bg-[#0E8028] text-white font-bold rounded-xl shadow-lg hover:bg-green-700 transition-colors uppercase text-xs tracking-widest">
              {{ loading ? 'Enrolling...' : 'Enroll Student' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Result Summary Modal -->
    <div v-if="showResultModal" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-blue-600 p-4 text-white flex justify-between items-center">
          <h3 class="text-xs font-bold tracking-widest uppercase">Import Results</h3>
          <button @click="showResultModal = false" class="hover:text-blue-100 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div v-if="importResults.enrolled_count > 0" class="flex items-center gap-3 p-3 bg-green-50 text-green-700 rounded-lg border border-green-100">
            <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center font-bold text-sm">✓</div>
            <p class="text-sm font-semibold">Successfully enrolled {{ importResults.enrolled_count }} students.</p>
          </div>

          <div v-if="importResults.not_found?.length > 0" class="space-y-2">
            <p class="text-xs font-bold text-red-600 uppercase tracking-widest flex items-center gap-2">
               <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
               Not in Student Master List
            </p>
            <div class="bg-red-50/50 border border-red-100 rounded-lg p-3 max-h-40 overflow-y-auto">
              <ul class="grid grid-cols-2 gap-2">
                <li v-for="id in importResults.not_found" :key="id" class="text-xs font-mono text-red-700 bg-white p-1.5 rounded border border-red-100 shadow-sm">{{ id }}</li>
              </ul>
            </div>
            <p class="text-[10px] text-gray-400 italic">These IDs do not exist in the system's student model. Only registered students can be enrolled.</p>
          </div>

          <div v-if="importResults.already_enrolled?.length > 0" class="space-y-2">
            <p class="text-xs font-bold text-orange-600 uppercase tracking-widest">Already Enrolled Elsewhere</p>
            <div class="bg-orange-50/50 border border-orange-100 rounded-lg p-3 max-h-32 overflow-y-auto">
              <ul class="space-y-1">
                <li v-for="item in importResults.already_enrolled" :key="item.id" class="text-xs text-orange-800">
                  <span class="font-bold">{{ item.id }}</span> is in section <span class="italic font-semibold">'{{ item.section }}'</span>
                </li>
              </ul>
            </div>
          </div>

          <button @click="showResultModal = false" class="w-full py-3 bg-gray-100 text-gray-600 font-bold rounded-xl hover:bg-gray-200 transition-colors uppercase text-xs tracking-widest">Close Results</button>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/axios'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { sectionPeopleListService } from '@/services/instructor/sectionPeopleListService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useModalStore } from '@/stores/modal'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const modalStore = useModalStore()

// Data State
const section = ref(null)
const sidebarSections = ref([])
const enrolledStudents = ref([])
const sidebarOpen = ref(false)
const dropdownOpen = ref(false)

// Modal State
const isModalOpen = ref(false)
const studentNumberInput = ref('')
const loading = ref(false)
const fileInput = ref(null)
const showResultModal = ref(false)
const importResults = ref({ enrolled_count: 0, not_found: [], already_enrolled: [] })

// Logic: Modals
const openEnrollModal = () => {
  studentNumberInput.value = ''
  isModalOpen.value = true
}

const submitEnrollment = async () => {
  if (!studentNumberInput.value) {
    notificationStore.warn("Please enter a student number")
    return
  }
  
  loading.value = true
  try {
    const sectionId = route.params.id
    const token = localStorage.getItem('auth_token')
    
    const response = await api.post(`api/instructor/sections/${sectionId}/enroll/`, 
      { student_number: studentNumberInput.value }
    )
    
    notificationStore.success(response.data.message)
    isModalOpen.value = false
    await fetchAllData() // Refresh student list
  } catch (error) {
    notificationStore.error(error.response?.data?.error || "Failed to enroll student")
  } finally {
    loading.value = false
  }
}

const removeStudent = async (student) => {
  const confirmed = await modalStore.confirm({
    title: 'Unenroll Student',
    message: `Are you sure you want to unenroll ${student.first_name} ${student.last_name}?`,
    confirmText: 'Unenroll',
    cancelText: 'Cancel'
  })
  if (!confirmed) return
  
  loading.value = true
  try {
    const sectionId = route.params.id
    const response = await sectionPeopleListService.unenrollStudent(sectionId, student.id)
    notificationStore.success(response.message || "Student successfully unenrolled.")
    await fetchAllData() // Refresh student list
  } catch (error) {
    notificationStore.error(error.response?.data?.error || "Failed to unenroll student")
  } finally {
    loading.value = false
  }
}

// Logic: Bulk Actions
const triggerFileUpload = () => {
    fileInput.value.click()
}

const handleCSVUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    // Check if it's a CSV
    if (!file.name.endsWith('.csv')) {
        notificationStore.error("Please upload a .csv file")
        return
    }

    loading.value = true
    try {
        const sectionId = route.params.id
        const response = await sectionPeopleListService.bulkEnrollStudents(sectionId, file)
        importResults.value = response
        showResultModal.value = true
        await fetchAllData()
    } catch (error) {
        notificationStore.error(error.response?.data?.error || "Failed to process bulk enrollment")
    } finally {
        loading.value = false
        event.target.value = '' // Reset input
    }
}

const handleClearAll = async () => {
    if (enrolledStudents.value.length === 0) {
        notificationStore.warn("There are no students to clear.")
        return
    }

    const confirmed = await modalStore.confirm({
        title: 'Clear All Students',
        message: 'Are you sure you want to unenroll ALL students from this section? This action cannot be undone.',
        confirmText: 'Clear Everything',
        cancelText: 'Cancel',
        danger: true
    })

    if (!confirmed) return

    loading.value = true
    try {
        const sectionId = route.params.id
        const response = await sectionPeopleListService.clearEnrolledStudents(sectionId)
        notificationStore.success(response.message)
        await fetchAllData()
    } catch (error) {
        notificationStore.error(error.response?.data?.error || "Failed to clear section")
    } finally {
        loading.value = false
    }
}

// Logic: UI Toggles
const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

// Logic: Computed Props
const userFullName = computed(() => userStore.userFullName || "Instructor")
const initials = computed(() => userStore.userInitials)

// Logic: Auth/Nav
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
const goToSection = (id) => { router.push(`/instructor/section/${id}`) }

// Logic: Data Fetching
const fetchAllData = async () => {
  try {
    const id = route.params.id;
    // 1. Fetch Section Details
    section.value = await sectionDetailsService.getSectionDetails(id);
    // 2. Fetch Enrolled Students from Django API
    enrolledStudents.value = await sectionPeopleListService.getEnrolledStudents(id);
    // 3. Fetch Sidebar Navigation
    const dashData = await instructorDashboardService.getDashboard();
    sidebarSections.value = dashData.sections;
    
    // 4. Ensure user data is loaded in store
    await userStore.ensureUserLoaded();
  } catch (error) { 
    console.error("Failed to load people data", error) 
  }
}

watch(() => route.params.id, () => { fetchAllData() })
onMounted(fetchAllData)
</script>