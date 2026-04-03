<template>
  <div class="p-8 max-w-7xl mx-auto">
    <!-- Header/Breadcrumbs -->
    <div class="mb-6">
      <div class="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
        <router-link to="/instructor/dashboard" class="hover:text-pink-500 transition-colors">Dashboard</router-link>
        <span>/</span>
        <span class="text-slate-600">{{ section?.section_name }}</span>
      </div>
      <h2 class="text-2xl font-bold text-slate-800 tracking-tight">
        {{ section?.section_code }} - {{ section?.section_name }}
      </h2>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center gap-8 border-b border-slate-200 mb-8 px-2 relative">
      <router-link 
        :to="`/instructor/section/${route.params.id}`" 
        class="pb-3 text-sm font-bold uppercase text-slate-400 hover:text-slate-600 tracking-wider transition-all"
      >
        Assessments
      </router-link>
      <button class="pb-3 text-sm font-bold uppercase border-b-2 border-pink-500 text-pink-600 tracking-wider">
        Students
      </button>
      <router-link 
        :to="`/instructor/section/${route.params.id}/settings`" 
        class="pb-3 text-sm font-bold uppercase text-slate-400 hover:text-slate-600 tracking-wider transition-all"
      >
        Section Settings
      </router-link>
      
      <!-- Actions -->
      <div class="ml-auto flex items-center gap-3 mb-2">
        <input type="file" ref="fileInput" @change="handleCSVUpload" accept=".csv" class="hidden">
        
        <button @click="triggerFileUpload" class="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold text-[10px] uppercase tracking-widest shadow-sm hover:bg-blue-700 active:scale-95 transition-all flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Import CSV
        </button>

        <button @click="handleClearAll" class="bg-red-50 text-red-600 px-4 py-2 rounded-lg font-bold text-[10px] uppercase tracking-widest border border-red-100 hover:bg-red-100 active:scale-95 transition-all flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Clear
        </button>

        <button @click="openEnrollModal" class="bg-pink-500 text-white px-4 py-2 rounded-lg font-bold text-[10px] uppercase tracking-widest shadow-md hover:bg-pink-600 active:scale-95 transition-all">
          Enroll Student
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-5xl space-y-10">
      <!-- Instructor Info -->
      <section>
        <div class="flex items-center justify-between border-b border-slate-200 pb-2 mb-4">
          <h3 class="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Faculty In Charge</h3>
        </div>
        
        <div class="flex items-center gap-4 p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
          <div class="w-10 h-10 bg-pink-100 rounded-full flex items-center justify-center border border-pink-200 text-pink-600 font-bold">
            {{ userStore.userInitials }}
          </div>
          <div>
            <p class="font-bold text-slate-800 leading-tight">{{ userStore.userFullName || 'Instructor' }}</p>
            <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Assigned Instructor</p>
          </div>
        </div>
      </section>

      <!-- Students List -->
      <section>
        <div class="flex items-center justify-between border-b border-slate-200 pb-3 mb-4">
          <h3 class="text-xs font-black text-slate-400 uppercase tracking-[0.2em]">Enrolled Students</h3>
          <span class="text-[10px] font-black bg-slate-100 text-slate-500 px-2.5 py-1 rounded-full uppercase tracking-tighter">
            {{ enrolledStudents.length }} total
          </span>
        </div>
        
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
          <table class="w-full text-left">
             <thead class="bg-slate-50 border-b border-slate-100">
               <tr>
                 <th class="px-6 py-3 text-[10px] font-black text-slate-400 uppercase tracking-widest">Student Info</th>
                 <th class="px-6 py-3 text-[10px] font-black text-slate-400 uppercase tracking-widest hidden md:table-cell">Student ID</th>
                 <th class="px-6 py-3 text-[10px] font-black text-slate-400 uppercase tracking-widest hidden lg:table-cell">Enrolled Date</th>
                 <th class="px-6 py-3 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Actions</th>
               </tr>
             </thead>
             <tbody class="divide-y divide-slate-50">
               <tr v-for="student in enrolledStudents" :key="student.id" class="group hover:bg-slate-50/50 transition-colors">
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 bg-pink-50 rounded-lg flex items-center justify-center text-pink-500 font-bold text-[10px] border border-pink-100">
                        {{ student.first_name.charAt(0) }}
                      </div>
                      <p class="text-sm font-bold text-slate-700 capitalize">{{ student.first_name }} {{ student.last_name }}</p>
                    </div>
                  </td>
                  <td class="px-6 py-4 hidden md:table-cell">
                    <span class="text-xs font-mono text-slate-400">{{ student.student_number }}</span>
                  </td>
                  <td class="px-6 py-4 hidden lg:table-cell">
                    <span class="text-[11px] text-slate-400 font-medium">{{ student.enrolled_at }}</span>
                  </td>
                  <td class="px-6 py-4 text-right">
                    <div class="flex items-center justify-end gap-2">
                       <button @click="removeStudent(student)" class="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all" title="Unenroll">
                         <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                         </svg>
                       </button>
                    </div>
                  </td>
               </tr>
               <tr v-if="enrolledStudents.length === 0">
                 <td colspan="4" class="px-6 py-12 text-center">
                    <div class="w-12 h-12 bg-slate-50 rounded-xl flex items-center justify-center mx-auto mb-3">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                    </div>
                    <p class="text-xs font-bold text-slate-400 uppercase tracking-widest leading-loose">No students enrolled yet</p>
                    <button @click="openEnrollModal" class="text-pink-500 text-[10px] font-black uppercase hover:underline">Enroll student now</button>
                 </td>
               </tr>
             </tbody>
          </table>
        </div>
      </section>
    </div>

    <!-- Modals -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] px-4">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-pink-600 p-4 text-white flex justify-between items-center">
          <h3 class="text-[10px] font-black tracking-[0.2em] uppercase">Manual Enrollment</h3>
          <button @click="isModalOpen = false" class="hover:text-pink-100 transition-colors">&times;</button>
        </div>
        <div class="p-8">
          <div class="mb-6">
            <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Student Number</label>
            <input 
              v-model="studentNumberInput"
              type="text" 
              placeholder="e.g. 21-0001"
              class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-pink-500/20 focus:border-pink-500 outline-none transition-all text-sm font-bold"
            />
          </div>
          <div class="flex gap-4">
            <button @click="isModalOpen = false" class="flex-1 py-3 text-slate-400 font-bold uppercase text-[10px] tracking-widest hover:bg-slate-50 rounded-xl">Cancel</button>
            <button @click="submitEnrollment" :disabled="loading" class="flex-1 py-3 bg-slate-800 text-white font-bold rounded-xl shadow-lg hover:bg-slate-700 transition-all uppercase text-[10px] tracking-widest active:scale-95 disabled:opacity-50">
              {{ loading ? 'Processing...' : 'Enroll Student' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showResultModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] px-4">
      <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-blue-600 p-4 text-white flex justify-between items-center">
          <h3 class="text-[10px] font-black tracking-[0.2em] uppercase">Import Summary</h3>
          <button @click="showResultModal = false" class="hover:text-blue-100 transition-colors">&times;</button>
        </div>
        <div class="p-6 space-y-4">
          <div v-if="importResults.enrolled_count > 0" class="flex items-center gap-3 p-4 bg-emerald-50 text-emerald-700 rounded-xl border border-emerald-100">
            <div class="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center font-black text-sm">✓</div>
            <p class="text-xs font-bold uppercase tracking-tight">Successfully enrolled {{ importResults.enrolled_count }} students.</p>
          </div>

          <div v-if="importResults.not_found?.length > 0" class="space-y-2">
            <p class="text-[10px] font-black text-red-600 uppercase tracking-widest">Master List Rejections (Not Found)</p>
            <div class="bg-red-50 border border-red-100 rounded-xl p-3 max-h-40 overflow-y-auto">
              <ul class="grid grid-cols-2 gap-1.5">
                <li v-for="id in importResults.not_found" :key="id" class="text-[10px] font-mono font-bold text-red-700 bg-white p-1.5 rounded border border-red-100 shadow-sm">{{ id }}</li>
              </ul>
            </div>
          </div>

          <div v-if="importResults.already_enrolled?.length > 0" class="space-y-2">
            <p class="text-[10px] font-black text-amber-600 uppercase tracking-widest">Already Enrolled (Skipped)</p>
            <div class="bg-amber-50 border border-amber-100 rounded-xl p-3 max-h-32 overflow-y-auto">
              <ul class="space-y-1.5">
                <li v-for="item in importResults.already_enrolled" :key="item.id" class="text-[10px] text-amber-800 font-medium">
                  <span class="font-bold">{{ item.id }}</span> is already in <span class="font-black italic">'{{ item.section }}'</span>
                </li>
              </ul>
            </div>
          </div>

          <button @click="showResultModal = false" class="w-full py-4 bg-slate-100 text-slate-500 font-black rounded-xl hover:bg-slate-200 transition-colors uppercase text-[10px] tracking-[0.2em]">Close Summary</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api/axios'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { sectionPeopleListService } from '@/services/instructor/sectionPeopleListService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useModalStore } from '@/stores/modal'

const props = defineProps({
  sections: Array
})

const route = useRoute()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const modalStore = useModalStore()

const section = ref(null)
const enrolledStudents = ref([])
const isModalOpen = ref(false)
const studentNumberInput = ref('')
const loading = ref(false)
const fileInput = ref(null)
const showResultModal = ref(false)
const importResults = ref({ enrolled_count: 0, not_found: [], already_enrolled: [] })

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
    const response = await api.post(`api/instructor/sections/${sectionId}/enroll/`, 
      { student_number: studentNumberInput.value }
    )
    notificationStore.success(response.data.message)
    isModalOpen.value = false
    await fetchStudentData()
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
    confirmText: 'Unenroll Student',
    cancelText: 'Cancel',
    danger: true
  })
  if (!confirmed) return
  
  loading.value = true
  try {
    const sectionId = route.params.id
    await sectionPeopleListService.unenrollStudent(sectionId, student.id)
    notificationStore.success("Student successfully unenrolled.")
    await fetchStudentData()
  } catch (error) {
    notificationStore.error(error.response?.data?.error || "Failed to unenroll student")
  } finally {
    loading.value = false
  }
}

const triggerFileUpload = () => { fileInput.value.click() }

const handleCSVUpload = async (event) => {
  const file = event.target.files[0]
  if (!file || !file.name.endsWith('.csv')) {
    notificationStore.error("Please upload a valid .csv file")
    return
  }
  loading.value = true
  try {
    const sectionId = route.params.id
    const response = await sectionPeopleListService.bulkEnrollStudents(sectionId, file)
    importResults.value = response
    showResultModal.value = true
    await fetchStudentData()
  } catch (error) {
    notificationStore.error("Failed to process bulk enrollment")
  } finally {
    loading.value = false
    event.target.value = ''
  }
}

const handleClearAll = async () => {
  if (enrolledStudents.value.length === 0) return
  const confirmed = await modalStore.confirm({
    title: 'Wipe Section Roster',
    message: 'Are you sure you want to unenroll EVERY student in this section?',
    confirmText: 'Wipe Everything',
    cancelText: 'Cancel',
    danger: true
  })
  if (!confirmed) return
  loading.value = true
  try {
    const sectionId = route.params.id
    await sectionPeopleListService.clearEnrolledStudents(sectionId)
    notificationStore.success("Section roster cleared.")
    await fetchStudentData()
  } catch (error) {
    notificationStore.error("Failed to clear section")
  } finally {
    loading.value = false
  }
}

const fetchStudentData = async () => {
  try {
    const id = route.params.id
    section.value = await sectionDetailsService.getSectionDetails(id)
    enrolledStudents.value = await sectionPeopleListService.getEnrolledStudents(id)
  } catch (error) {
    console.error("Failed to load students", error)
  }
}

watch(() => route.params.id, fetchStudentData)
onMounted(fetchStudentData)
</script>