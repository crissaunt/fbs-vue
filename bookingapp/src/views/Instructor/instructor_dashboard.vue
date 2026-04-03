<template>
  <div class="p-4 lg:p-8 max-w-7xl mx-auto">
    <!-- Welcome and Breadcrumbs -->
    <div class="mb-2">
      <h2 class="text-xl font-bold text-slate-800 tracking-tight">Instructor Dashboard</h2>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
      <div class="bg-white p-4 rounded-md shadow-sm flex items-center gap-3 transition-all hover:shadow-md">
        <div class="w-10 h-10 bg-pink-50 rounded-md flex items-center justify-center text-pink-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Total Sections</p>
          <h4 class="text-xl font-bold text-slate-700">{{ sections?.length || 0 }}</h4>
        </div>
      </div>

      <div class="bg-white p-4 rounded-md shadow-sm flex items-center gap-3 transition-all hover:shadow-md">
        <div class="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center text-emerald-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Total Students</p>
          <h4 class="text-xl font-bold text-slate-700">{{ totalStudents }}</h4>
        </div>
      </div>

      <div class="bg-white p-4 rounded-md shadow-sm flex items-center gap-3 transition-all hover:shadow-md">
        <div class="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Active Activities</p>
          <h4 class="text-xl font-bold text-slate-700">{{ totalActivities }}</h4>
        </div>
      </div>

      <div class="bg-white p-4 rounded-md shadow-sm flex items-center gap-3 transition-all hover:shadow-md">
        <div class="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center text-amber-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Last Update</p>
          <h4 class="text-sm font-bold text-slate-700">{{ lastSyncTime }}</h4>
        </div>
      </div>
    </div>

    <!-- Section Controls -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
      <h3 class="text-lg font-bold text-slate-700">Academic Sections</h3>
      
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <div class="relative flex-1 sm:w-64">
          <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search sections..." 
            class="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/20 focus:border-pink-500 transition-all shadow-sm"
          >
        </div>
        <button 
          @click="showModal = true"
          class="bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 shadow-sm transition-all active:scale-95 whitespace-nowrap"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Register New
        </button>
      </div>
    </div>

    <!-- Grid View -->
    <div v-if="!searchQuery || filteredSections.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <!-- Register New Section Card -->
      <div 
        v-if="!searchQuery"
        @click="showModal = true"
        class="group border-2 border-dashed border-slate-200 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer hover:border-pink-500 hover:bg-pink-50 transition-all duration-300 min-h-[260px] bg-white shadow-sm hover:shadow-md"
      >
        <div class="w-16 h-16 bg-slate-50 border-2 border-dashed border-slate-200 rounded-full flex items-center justify-center mb-4 group-hover:border-pink-500 group-hover:bg-white transition-all duration-300">
          <span class="text-3xl text-slate-300 group-hover:text-pink-500 transition-colors">+</span>
        </div>
        <p class="text-slate-500 font-bold uppercase text-xs tracking-widest group-hover:text-pink-600 transition-colors text-center">Register New Section</p>
      </div>

      <div 
        v-for="section in filteredSections" 
        :key="section.id" 
        @click="goToSection(section.id)" 
        class="group bg-white rounded-xl shadow-sm hover:shadow-xl border border-slate-100 overflow-hidden transition-all duration-300 cursor-pointer flex flex-col h-full"
      >
        <div class="p-1">
          <div class="bg-gradient-to-br from-pink-600 to-pink-500 text-white p-4 rounded-lg relative overflow-hidden">
            <div class="absolute -right-4 -top-4 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
            
            <div class="flex justify-between items-start relative z-10">
              <div>
                <span class="text-[10px] font-bold uppercase tracking-[0.2em] text-pink-400 mb-1 block">Course Code</span>
                <h3 class="text-lg font-bold">{{ section.section_code }}</h3>
              </div>
              <div class="flex items-center gap-1">
                <span v-if="!section.is_active" class="bg-red-500/20 text-red-200 text-[10px] px-2 py-0.5 rounded border border-red-500/30 font-bold uppercase">Inactive</span>
                <button @click.stop="editSection(section)" class="p-1.5 hover:bg-white/10 rounded-md transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="mt-4 flex items-center gap-3 relative z-10">
              <div class="w-10 h-10 rounded-full bg-slate-100/10 flex items-center justify-center font-bold text-sm text-pink-400">
                {{ section.section_name.charAt(0) }}
              </div>
              <div>
                <p class="text-sm font-medium text-slate-100 leading-none mb-1">{{ section.section_name }}</p>
                <div v-if="section.schedule" class="flex flex-wrap gap-1 mt-1">
                  <template v-if="Array.isArray(parsedSectionSchedule(section.schedule))">
                     <span v-for="(s, i) in parsedSectionSchedule(section.schedule).slice(0, 2)" :key="i" class="text-[9px] bg-white/10 text-white/90 px-1.5 py-0.5 rounded border border-white/10 backdrop-blur-sm font-bold">
                       {{ s.day.substring(0, 2) }} {{ formatTimeOnly(s.start_time) }}
                     </span>
                     <span v-if="parsedSectionSchedule(section.schedule).length > 2" class="text-[9px] text-white/40 self-center font-bold ml-1">+{{ parsedSectionSchedule(section.schedule).length - 2 }} more</span>
                  </template>
                  <p v-else class="text-[11px] text-slate-200 font-medium">{{ formatSchedule(section.schedule) }}</p>
                </div>
                <p v-else class="text-[11px] text-white/70 font-medium">No schedule set</p>
              </div>
            </div>
          </div>
        </div>

        <div class="p-5 flex-1 flex flex-col justify-between">
          <div>
            <p class="text-sm text-slate-500 leading-relaxed line-clamp-2 italic mb-4">
              {{ section.description || 'Provide a detailed overview of this section to help organize your curriculum.' }}
            </p>
          </div>

          <div class="pt-4 border-t border-slate-50 flex items-center justify-end">
            <div class="text-right">
              <p class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{{ section.semester }}</p>
              <p class="text-[10px] font-black text-slate-600">{{ section.activity_count || 0 }} Activities</p>
            </div>
          </div>
        </div>
        
        <div class="bg-slate-50/50 px-5 py-3 flex items-center justify-between group-hover:bg-pink-50 transition-colors">
          <span class="text-[10px] font-bold text-slate-500 group-hover:text-pink-600 transition-colors flex items-center gap-1.5 uppercase">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Manage Console
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-300 group-hover:text-pink-500 transition-all transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="searchQuery && filteredSections.length === 0" class="bg-white rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center">
      <div class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h3 class="text-lg font-bold text-slate-700 mb-1">No sections found</h3>
      <p class="text-slate-500 text-sm max-w-xs mx-auto mb-6">
        We couldn't find any sections matching "{{ searchQuery }}".
      </p>
      <button 
        @click="searchQuery = ''"
        class="text-pink-500 font-bold text-sm hover:underline"
      >
        Clear search results
      </button>
    </div>

    <!-- Create Section Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] px-4">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-gradient-to-r from-pink-600 to-pink-500 text-white px-6 py-3 flex justify-between items-center rounded-t-lg">
          <h3 class="text-xs font-bold uppercase tracking-widest">Register New Academic Section</h3>
          <button @click="showModal = false" class="text-white hover:text-pink-100 text-2xl transition-colors">&times;</button>
        </div>

        <form @submit.prevent="submitSection" class="p-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-1.5">Section Designation <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.section_name" type="text" placeholder="e.g., BSIT 3A" class="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm font-medium" required>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Section Code <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.section_code" type="text" placeholder="e.g., IT311" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Semester <span class="text-red-500 font-bold">*</span></label>
              <select v-model="form.semester" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
                <option value="" disabled>Select Semester</option>
                <option value="1st Semester">1st Semester</option>
                <option value="2nd Semester">2nd Semester</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Academic Year <span class="text-red-500 font-bold">*</span></label>
              <select v-model="form.academic_year" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
                <option value="" disabled>Select Year</option>
                <option value="2024-2025">2024-2025</option>
                <option value="2025-2026">2025-2026</option>
                <option value="2026-2027">2026-2027</option>
                <option value="2027-2028">2027-2028</option>
                <option value="2029-2030">2029-2030</option>
              </select>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-2">Schedule(s)</label>
            <div v-for="(sched, index) in form.schedules" :key="index" class="flex gap-2 mb-2 items-center">
              <select v-model="sched.day" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
                <option value="" disabled>Day</option>
                <option value="Monday">Monday</option>
                <option value="Tuesday">Tuesday</option>
                <option value="Wednesday">Wednesday</option>
                <option value="Thursday">Thursday</option>
                <option value="Friday">Friday</option>
                <option value="Saturday">Saturday</option>
                <option value="Sunday">Sunday</option>
              </select>
              <input v-model="sched.start_time" type="time" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
              <span class="text-gray-400 text-xs">-</span>
              <input v-model="sched.end_time" type="time" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
              <button v-if="form.schedules.length > 1" type="button" @click="removeSchedule(index)" class="text-red-400 hover:text-red-500 p-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <button type="button" @click="addSchedule" class="text-pink-500 text-[10px] font-bold uppercase tracking-widest hover:text-pink-600 flex items-center gap-1 mt-1 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
              </svg>
              Add Another Schedule
            </button>
          </div>

          <div class="mb-6">
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Enter course details..." class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none resize-none bg-gray-50"></textarea>
          </div>

          <div class="flex justify-end gap-4 border-t pt-6">
            <button type="button" @click="showModal = false" class="text-gray-400 font-bold uppercase text-xs hover:text-gray-600 transition-colors">Cancel</button>
            <button type="submit" class="px-8 py-3 bg-pink-500 text-white rounded-lg font-black uppercase text-xs shadow-lg active:scale-95 transition-all">Create Section</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { useNotificationStore } from '@/stores/notification'

const props = defineProps({
  sections: Array
})

const emit = defineEmits(['refresh-data'])

const router = useRouter()
const notificationStore = useNotificationStore()

const searchQuery = ref('')
const showModal = ref(false)
const lastSyncTime = ref(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))

// Form state for creating a new section
const form = ref({
  section_name: '',
  section_code: '',
  semester: '',
  academic_year: '',
  schedules: [{ day: '', start_time: '', end_time: '' }],
  description: ''
})

const addSchedule = () => {
  form.value.schedules.push({ day: '', start_time: '', end_time: '' })
}

const removeSchedule = (index) => {
  form.value.schedules.splice(index, 1)
}

const formatTimeOnly = (t) => {
  if (!t) return ''
  const [h, m] = t.split(':')
  const hour = parseInt(h)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const h12 = hour % 12 || 12
  return `${h12}:${m} ${ampm}`
}

const parsedSectionSchedule = (scheduleData) => {
  if (!scheduleData) return null
  try {
    const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
    if (Array.isArray(schedules) && schedules.length > 0) return schedules
  } catch (e) {}
  return null
}

const formatSchedule = (scheduleData) => {
  if (!scheduleData) return 'No schedule set'
  try {
    const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
    if (Array.isArray(schedules)) {
      if (schedules.length === 0) return 'No schedule set'
      return schedules.map(s => {
        const dayShort = s.day.substring(0, 3)
        return `${dayShort} ${formatTimeOnly(s.start_time)}-${formatTimeOnly(s.end_time)}`
      }).join(', ')
    }
  } catch (e) {}
  return scheduleData
}

const filteredSections = computed(() => {
  if (!searchQuery.value) return props.sections || []
  const query = searchQuery.value.toLowerCase()
  return (props.sections || []).filter(s => 
    s.section_name.toLowerCase().includes(query) || 
    s.section_code.toLowerCase().includes(query)
  )
})

const totalStudents = computed(() => {
  return (props.sections || []).reduce((acc, s) => acc + (s.student_count || 0), 0)
})

const totalActivities = computed(() => {
  return (props.sections || []).reduce((acc, s) => acc + (s.activity_count || 0), 0)
})

const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

const editSection = (section) => {
  router.push(`/instructor/section/${section.id}/settings`)
}

const submitSection = async () => {
  try {
    const payload = {
      ...form.value,
      schedule: JSON.stringify(form.value.schedules)
    }
    await instructorDashboardService.createSection(payload);
    showModal.value = false;
    form.value = { 
      section_name: '', section_code: '', semester: '', 
      academic_year: '', schedules: [{ day: '', start_time: '', end_time: '' }], description: '' 
    };
    emit('refresh-data');
    notificationStore.success("Section created successfully!");
    lastSyncTime.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (error) {
    const serverMessage = error.response?.data?.error || "Check if Section Code is unique.";
    notificationStore.error("Backend Error: " + serverMessage);
  }
};
</script>
