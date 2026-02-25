<template>
  <div class="flex flex-col h-screen bg-[#FDFCF7] font-sans">
    <LoadingOverlay :loading="isFetching" />
    <!-- Header -->
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
      <!-- Sidebar -->
      <div :class="['bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg border-r border-pink-400/20', sidebarOpen ? 'w-56' : 'w-16']">
        <div class="flex flex-col h-full overflow-y-auto">
           <button @click="$router.push('/instructor/dashboard')" class="flex items-center py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/20 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
             </svg>
             <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Home</span>
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

      <!-- Main Content -->
      <div class="flex-1 overflow-auto bg-[#FDFCF7]">
        <div class="max-w-4xl mx-auto p-8">
          <div class="mb-8">
            <nav class="flex mb-4" aria-label="Breadcrumb">
              <ol class="inline-flex items-center space-x-1 md:space-x-3">
                <li class="inline-flex items-center">
                  <router-link :to="`/instructor/section/${route.params.id}`" class="text-sm text-gray-500 hover:text-pink-600 font-medium transition-colors">Section Details</router-link>
                </li>
                <li>
                  <div class="flex items-center">
                    <svg class="w-3 h-3 text-gray-400 mx-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 6 10">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 9 4-4-4-4"/>
                    </svg>
                    <span class="ml-1 text-sm font-bold text-gray-800 md:ml-2">Course Settings</span>
                  </div>
                </li>
              </ol>
            </nav>
            <h2 class="text-3xl font-light text-gray-900 tracking-wide">Course Settings</h2>
            <p class="text-sm text-gray-500 mt-1">Manage configurations and administrative controls for this course section.</p>
          </div>

          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="p-8">
              <form @submit.prevent="saveSettings">
                <div class="space-y-8">
                  <!-- Section Profile -->
                  <div>
                    <h3 class="text-xs font-black text-pink-500 uppercase tracking-widest mb-6 border-b border-pink-100 pb-2">Section Profile</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Section Name</label>
                        <input v-model="form.section_name" type="text" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Section Code</label>
                        <input v-model="form.section_code" type="text" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Semester</label>
                        <select v-model="form.semester" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                          <option value="1st Semester">1st Semester</option>
                          <option value="2nd Semester">2nd Semester</option>
                        </select>
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Academic Year</label>
                        <input v-model="form.academic_year" type="text" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                      </div>
                    </div>
                  </div>

                  <!-- Schedule & Description -->
                  <div>
                    <h3 class="text-xs font-black text-pink-500 uppercase tracking-widest mb-6 border-b border-pink-100 pb-2">Schedule & Description</h3>
                    <div class="space-y-6">
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Class Schedule</label>
                        <input v-model="form.schedule" type="text" placeholder="e.g. M-W-F 8:00 AM - 10:00 AM" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50">
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Course Description</label>
                        <textarea v-model="form.description" rows="4" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50 resize-none"></textarea>
                      </div>
                    </div>
                  </div>

                  <!-- Administrative Controls -->
                  <div class="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                    <h3 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-6">Administrative Controls</h3>
                    <div class="flex items-center justify-between">
                      <div class="pr-8">
                        <h4 class="text-sm font-bold text-gray-800">Lock Section</h4>
                        <p class="text-xs text-gray-500 mt-1">Preventing new students from enrolling in this section. Existing students are unaffected.</p>
                      </div>
                      <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" v-model="form.is_locked" class="sr-only peer">
                        <div class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-pink-500"></div>
                      </label>
                    </div>
                  </div>
                </div>

                <div class="mt-10 flex justify-end gap-4 border-t border-gray-100 pt-8">
                  <button 
                    type="button" 
                    @click="$router.push(`/instructor/section/${route.params.id}`)"
                    class="px-6 py-3 text-sm font-bold text-gray-400 hover:text-gray-600 uppercase tracking-widest transition-colors"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    :disabled="loading"
                    class="bg-pink-500 text-white px-10 py-3 rounded-xl font-bold text-xs uppercase tracking-widest shadow-lg hover:shadow-pink-200 active:scale-95 transition-all disabled:opacity-50"
                  >
                    {{ loading ? 'Saving...' : 'Save Changes' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { sectionSettingsService } from '@/services/instructor/sectionSettingsService'
import LoadingOverlay from '@/components/instructor/LoadingOverlay.vue'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

const sidebarOpen = ref(false)
const dropdownOpen = ref(false)
const isFetching = ref(false)
const loading = ref(false)
const sidebarSections = ref([])
const section = ref(null)

const form = ref({
  section_name: '',
  section_code: '',
  semester: '',
  academic_year: '',
  schedule: '',
  description: '',
  is_locked: false
})

const userFullName = computed(() => userStore.userFullName || 'Instructor')
const initials = computed(() => {
  const u = userStore.user?.username || 'I'
  return u[0].toUpperCase()
})

const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}

const fetchData = async () => {
  isFetching.value = true
  try {
    const sectionId = route.params.id
    const data = await sectionDetailsService.getSectionDetails(sectionId)
    section.value = data
    
    // Populate form
    form.value = {
      section_name: data.section_name || '',
      section_code: data.section_code || '',
      semester: data.semester || '',
      academic_year: data.academic_year || '',
      schedule: data.schedule || '',
      description: data.description || '',
      is_locked: data.is_locked || false
    }

    const dashboardData = await instructorDashboardService.getDashboard()
    sidebarSections.value = dashboardData.sections
  } catch (error) {
    notificationStore.error("Failed to load section settings.")
  } finally {
    isFetching.value = false
  }
}

const saveSettings = async () => {
  loading.value = true
  try {
    await sectionSettingsService.updateSectionSettings(route.params.id, form.value)
    notificationStore.success("Settings updated successfully!")
    router.push(`/instructor/section/${route.params.id}`)
  } catch (error) {
    const msg = error.response?.data?.error || "Failed to update settings."
    notificationStore.error(msg)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await userStore.ensureUserLoaded()
  await fetchData()
})
</script>

<style scoped>
.peer-checked\:bg-pink-500:checked ~ div {
  background-color: #ec4899;
}
</style>
