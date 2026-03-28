<template>
  <div class="flex flex-col h-screen bg-gray-50 font-sans">
    <LoadingOverlay :loading="isLoading" />
    
    <!-- Header (Same as Dashboard) -->
    <div class="bg-gradient-to-r from-pink-500 to-pink-400 text-white px-6 py-2.5 flex items-center justify-between shadow-sm z-20 border-b border-pink-400">
      <div class="flex items-center gap-4">
        <button 
          @click="toggleSidebar" 
          class="p-1.5 hover:bg-pink-600 rounded-md transition-colors focus:outline-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-[#0E8028] rounded-full flex items-center justify-center text-xl shadow-inner">🎓</div>
          <div>
            <h1 class="text-[10px] font-bold uppercase tracking-widest font-sans text-white/90">Cabagan State University</h1>
            <p class="text-[9px] uppercase tracking-tighter opacity-60">Faculty Portal</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4 relative">
        <div class="relative">
          <button 
            @click="toggleDropdown" 
            class="flex items-center gap-2 hover:bg-pink-600 p-1.5 rounded-md transition-colors focus:outline-none"
          >
            <span class="text-xs font-medium">{{ userStore.userFullName || 'Instructor' }}</span>
            <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center overflow-hidden border border-pink-300">
               <div class="w-full h-full bg-gray-300 rounded-full flex items-center justify-center text-gray-600 text-xs font-bold uppercase">{{ initials }}</div>
            </div>
          </button>

          <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
             <button @click="router.push('/profile')" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">My Profile</button>
             <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Logout</button>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar (Same as Dashboard) -->
      <div 
        :class="[
          'bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg border-r border-pink-400/20', 
          sidebarOpen ? 'w-56' : 'w-16'
        ]"
      >
        <div class="flex flex-col h-full overflow-y-auto">
           <button @click="router.push('/instructor/dashboard')" class="flex items-center py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/20 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
             </svg>
             <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Home</span>
           </button>

           <!-- LOGS NAV ITEM -->
           <button @click="router.push('/instructor/logs')" class="flex items-center py-3 bg-pink-700 hover:bg-pink-600 transition-colors border-b border-pink-400/20 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
             </svg>
             <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Activity Logs</span>
           </button>

           <div v-if="sidebarOpen" class="px-5 py-2 text-[10px] font-black uppercase tracking-widest text-pink-200 mt-4 opacity-70">Sections</div>
           
           <div 
             v-for="section in sections" 
             :key="section.id" 
             @click="goToSection(section.id)" 
             :class="[
               'flex items-center py-2.5 hover:bg-pink-600 cursor-pointer transition-colors border-b border-pink-400/10',
               sidebarOpen ? 'px-5' : 'justify-center'
             ]"
           >
              <div class="w-7 h-7 rounded-full bg-white text-pink-500 flex items-center justify-center font-bold text-[10px] flex-shrink-0 shadow-sm uppercase">
                {{ section.section_name.charAt(0) }}
              </div>
              <span v-show="sidebarOpen" class="ml-3 truncate text-[11px] font-bold tracking-wider uppercase text-white">{{ section.section_name }}</span>
           </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="flex-1 overflow-auto bg-[#F8FAFC]">
        <div class="p-4 lg:p-8 max-w-7xl mx-auto">
          <!-- Title Section -->
          <div class="mb-8">
            <h2 class="text-2xl font-bold text-slate-800 tracking-tight">Instructor Activity Logs</h2>
            <div class="flex items-center gap-2 text-sm text-slate-500 mt-1">
              <span>Main Console</span>
              <span class="text-slate-300">•</span>
              <span class="text-pink-500 font-medium">Audit Trail</span>
            </div>
          </div>

          <!-- Logs Table -->
          <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-slate-50/50 border-b border-slate-100">
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Timestamp</th>
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Action</th>
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">User Involved</th>
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Details</th>
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Location/Device</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-50">
                  <tr v-for="log in logs" :key="log.id" class="hover:bg-slate-50/50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-[11px] font-bold text-slate-700">{{ formatDate(log.timestamp) }}</div>
                      <div class="text-[10px] text-slate-400">{{ formatTime(log.timestamp) }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <span :class="getActionClass(log.action_type)" class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-widest border">
                        {{ log.action_type.replace('_', ' ') }}
                      </span>
                    </td>
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-3">
                        <div class="w-7 h-7 bg-slate-100 rounded-full flex items-center justify-center text-[10px] font-bold text-slate-500 border border-slate-200">
                          {{ log.actor_role === 'student' ? '🎓' : '👨‍🏫' }}
                        </div>
                        <div>
                          <div class="text-[11px] font-bold text-slate-800">{{ log.actor_name }}</div>
                          <div class="text-[9px] text-slate-400 uppercase tracking-tighter">{{ log.actor_role }}</div>
                          <div v-if="log.student_number" class="text-[9px] font-bold text-pink-500">ID: {{ log.student_number }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-[11px] text-slate-600 max-w-md">
                        {{ log.details }}
                        <div v-if="log.section_name" class="mt-1">
                          <span class="text-[9px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded border border-slate-200 font-bold uppercase">{{ log.section_name }}</span>
                          <span v-if="log.activity_name" class="ml-1 text-[9px] bg-indigo-50 text-indigo-500 px-1.5 py-0.5 rounded border border-indigo-100 font-bold uppercase">{{ log.activity_name }}</span>
                        </div>
                        <div v-if="log.login_time || log.logout_time" class="mt-1 flex gap-2">
                           <span v-if="log.login_time" class="text-[9px] text-emerald-600 font-bold">In: {{ formatTime(log.login_time) }}</span>
                           <span v-if="log.logout_time" class="text-[9px] text-red-500 font-bold">Out: {{ formatTime(log.logout_time) }}</span>
                        </div>
                        <div v-if="log.is_csv" class="mt-1">
                          <span class="text-[9px] bg-amber-50 text-amber-600 px-1.5 py-0.5 rounded border border-amber-100 font-black uppercase tracking-tighter italic">Imported via CSV/Excel</span>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-[10px] font-medium text-slate-500 flex items-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <span class="truncate max-w-[150px]" :title="log.device">{{ log.device }}</span>
                      </div>
                      <div class="text-[9px] font-bold text-slate-400 tracking-widest mt-0.5">{{ log.ip_address }}</div>
                    </td>
                  </tr>
                  <tr v-if="logs.length === 0 && !isLoading">
                    <td colspan="5" class="px-6 py-20 text-center">
                      <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-100">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <p class="text-sm font-bold text-slate-400 uppercase tracking-widest">No activity logs recorded yet</p>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import LoadingOverlay from '@/components/instructor/LoadingOverlay.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const isLoading = ref(false)
const sidebarOpen = ref(false)
const dropdownOpen = ref(false)
const logs = ref([])
const sections = ref([])

const initials = computed(() => {
  const u = userStore.user?.username || userStore.user?.first_name || 'I'
  return u[0].toUpperCase()
})

const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

const fetchLogs = async () => {
  isLoading.value = true
  try {
    const [logsData, dashData] = await Promise.all([
      instructorDashboardService.getLogs(),
      instructorDashboardService.getDashboard()
    ])
    logs.value = logsData
    sections.value = dashData.sections
  } catch (error) {
    console.error('Failed to fetch logs:', error)
  } finally {
    isLoading.value = false
  }
}

const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatTime = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const getActionClass = (type) => {
  switch (type) {
    case 'LOGIN': return 'bg-emerald-50 text-emerald-600 border-emerald-100'
    case 'LOGOUT': return 'bg-slate-100 text-slate-500 border-slate-200'
    case 'SECTION_CREATED': return 'bg-blue-50 text-blue-600 border-blue-100'
    case 'SECTION_DELETED': return 'bg-red-50 text-red-600 border-red-100'
    case 'ACTIVITY_CREATED': return 'bg-indigo-50 text-indigo-600 border-indigo-100'
    case 'ACTIVITY_DELETED': return 'bg-rose-50 text-rose-600 border-rose-100'
    case 'STUDENT_ENROLLED': return 'bg-pink-50 text-pink-600 border-pink-100'
    case 'STUDENT_UNENROLLED': return 'bg-orange-50 text-orange-600 border-orange-100'
    case 'ACTIVITY_TAKEN': return 'bg-amber-50 text-amber-600 border-amber-100'
    case 'GRADES_RELEASED': return 'bg-violet-50 text-violet-600 border-violet-100'
    case 'REPORT_PRINTED': return 'bg-cyan-50 text-cyan-600 border-cyan-100'
    default: return 'bg-gray-50 text-gray-500 border-gray-100'
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
/* Optional styling */
</style>
