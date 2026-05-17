<template>
  <div class="flex-1 flex flex-col bg-gray-100 min-h-0 overflow-y-auto">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-5">
      <div class="flex items-center gap-3 mb-1">
        <div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8M10 12v4M14 12v4" />
          </svg>
        </div>
        <h2 class="text-lg font-black text-gray-800">Archived Sections</h2>
      </div>
      <p class="text-xs text-gray-500 ml-11">Sections from previous terms you were enrolled in. Read-only access only.</p>
    </div>

    <!-- Section Archived Notice Banner -->
    <Transition name="banner-fade">
      <div
        v-if="showArchivedBanner"
        class="mx-6 mt-5 bg-amber-50 border border-amber-200 rounded-2xl p-4 flex gap-4 items-start shadow-sm"
      >
        <div class="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center flex-shrink-0">
          <i class="ph ph-warning text-amber-600 text-xl"></i>
        </div>
        <div class="flex-1">
          <p class="text-sm font-black text-amber-800 mb-0.5">Your Section Was Archived</p>
          <p class="text-xs text-amber-700 leading-relaxed">
            <span v-if="userStore.archivedSectionName">
              <strong>{{ userStore.archivedSectionName }}</strong> has been archived by your instructor.
            </span>
            <span v-else>Your previous section has been archived.</span>
            You have been automatically unenrolled and your history is preserved below.
            Please contact your instructor to be enrolled in a new active section.
          </p>
        </div>
        <button
          @click="dismissBanner"
          class="text-amber-400 hover:text-amber-600 transition-colors flex-shrink-0 w-6 h-6 flex items-center justify-center"
        >
          <i class="ph ph-x text-lg"></i>
        </button>
      </div>
    </Transition>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-pink-500"></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="archivedSections.length === 0" class="flex-1 flex flex-col items-center justify-center py-20 px-6 text-center">
      <div class="w-20 h-20 bg-amber-50 rounded-full flex items-center justify-center mb-5">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-amber-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8M10 12v4M14 12v4" />
        </svg>
      </div>
      <h3 class="text-lg font-bold text-gray-700 mb-2">No Archived Sections</h3>
      <p class="text-gray-500 text-sm max-w-xs">When your instructor archives a section you were enrolled in, it will appear here.</p>
    </div>

    <!-- Archived sections list -->
    <div v-else class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <div
        v-for="section in archivedSections"
        :key="section.id"
        @click="openSection(section)"
        class="group bg-white rounded-2xl border border-amber-100 hover:border-amber-300 shadow-sm hover:shadow-md overflow-hidden cursor-pointer transition-all duration-300"
      >
        <!-- Archived ribbon -->
        <div class="bg-amber-50 border-b border-amber-100 px-4 py-1.5 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8" />
          </svg>
          <span class="text-[9px] font-black uppercase tracking-widest text-amber-500">Archived · {{ formatDate(section.archived_at) }}</span>
        </div>

        <div class="p-4">
          <div class="flex items-center gap-2.5 mb-3">
            <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-400 to-amber-500 flex items-center justify-center font-black text-lg text-white shadow-sm flex-shrink-0">
              {{ section.section_name?.charAt(0) }}
            </div>
            <div class="min-w-0">
              <span class="text-[8px] font-black uppercase tracking-[0.2em] text-gray-400 block truncate">{{ section.section_code }}</span>
              <h3 class="text-xs font-black text-gray-800 group-hover:text-amber-600 transition-colors truncate leading-tight">{{ section.section_name }}</h3>
              <p class="text-[9px] text-gray-400 font-medium truncate">by {{ section.instructor_name }}</p>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2 mb-3">
            <div class="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
              <p class="text-sm font-black text-gray-700">{{ section.activities?.length || 0 }}</p>
              <p class="text-[8px] font-black uppercase tracking-widest text-gray-400">Activities</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
              <p class="text-sm font-black text-gray-700">{{ section.classmates?.length || 0 }}</p>
              <p class="text-[8px] font-black uppercase tracking-widest text-gray-400">Classmates</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
              <p class="text-[10px] font-black text-gray-700">{{ section.semester }}</p>
              <p class="text-[8px] font-black uppercase tracking-widest text-gray-400">Semester</p>
            </div>
          </div>

          <div class="flex items-center justify-between mt-1">
            <span class="text-[9px] text-gray-400 font-medium">{{ section.academic_year }}</span>
            <span class="text-[9px] font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-lg border border-amber-100 flex items-center gap-1 group-hover:bg-amber-100 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Details
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedSection" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4" @click.self="selectedSection = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Modal header -->
        <div class="bg-gradient-to-r from-amber-600 to-amber-500 text-white px-6 py-4 flex justify-between items-center">
          <div>
            <p class="text-[9px] font-black uppercase tracking-[0.2em] text-amber-200 mb-0.5">{{ selectedSection.section_code }} · Archived Class</p>
            <h3 class="text-lg font-black">{{ selectedSection.section_name }}</h3>
            <p class="text-[10px] text-amber-200">Instructor: {{ selectedSection.instructor_name }}</p>
          </div>
          <button @click="selectedSection = null" class="text-white/70 hover:text-white text-2xl leading-none">&times;</button>
        </div>

        <!-- Read-only notice -->
        <div class="bg-amber-50 border-b border-amber-100 px-6 py-2 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-amber-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <span class="text-[10px] font-bold text-amber-700">You have been unenrolled from this section. View is read-only.</span>
        </div>

        <div class="overflow-y-auto flex-1">
          <!-- Meta -->
          <div class="p-5 grid grid-cols-2 sm:grid-cols-3 gap-3 border-b border-gray-100">
            <div><p class="text-[9px] font-black uppercase tracking-widest text-gray-400 mb-0.5">Semester</p><p class="text-sm font-bold text-gray-700">{{ selectedSection.semester }}</p></div>
            <div><p class="text-[9px] font-black uppercase tracking-widest text-gray-400 mb-0.5">Academic Year</p><p class="text-sm font-bold text-gray-700">{{ selectedSection.academic_year }}</p></div>
            <div><p class="text-[9px] font-black uppercase tracking-widest text-gray-400 mb-0.5">Archived On</p><p class="text-sm font-bold text-gray-700">{{ formatDate(selectedSection.archived_at) }}</p></div>
          </div>

          <!-- Activities -->
          <div class="p-5 border-b border-gray-100">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-3">Activities ({{ selectedSection.activities?.length || 0 }})</h4>
            <div v-if="!selectedSection.activities?.length" class="text-sm text-gray-400 italic">No activities were created.</div>
            <div v-else class="space-y-2">
              <div v-for="activity in selectedSection.activities" :key="activity.id"
                class="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3 border border-gray-100">
                <div>
                  <p class="text-sm font-bold text-gray-700">{{ activity.title }}</p>
                  <p class="text-[10px] text-gray-400">{{ activity.activity_type }} · {{ activity.total_points }} pts</p>
                </div>
                <span :class="[
                  'text-[9px] font-black uppercase tracking-widest px-2 py-1 rounded-md border',
                  activity.status === 'published' ? 'bg-green-50 text-green-600 border-green-100' :
                  activity.status === 'closed' ? 'bg-red-50 text-red-500 border-red-100' :
                  'bg-gray-100 text-gray-500 border-gray-200'
                ]">{{ activity.status }}</span>
              </div>
            </div>
          </div>

          <!-- Classmates -->
          <div class="p-5">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-3">Classmates ({{ selectedSection.classmates?.length || 0 }})</h4>
            <div v-if="!selectedSection.classmates?.length" class="text-sm text-gray-400 italic">No other students were enrolled.</div>
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div v-for="mate in selectedSection.classmates" :key="mate.id"
                class="flex items-center gap-3 bg-gray-50 rounded-xl px-3 py-2.5 border border-gray-100">
                <div class="w-7 h-7 rounded-full bg-pink-100 flex items-center justify-center font-bold text-[11px] text-pink-600 flex-shrink-0">
                  {{ mate.first_name?.charAt(0) }}
                </div>
                <div class="min-w-0">
                  <p class="text-[12px] font-bold text-gray-700 truncate">{{ mate.first_name }} {{ mate.last_name }}</p>
                  <p class="text-[9px] text-gray-400">{{ mate.student_number }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="px-5 py-4 border-t border-gray-100 flex justify-end">
          <button @click="selectedSection = null" class="px-6 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl text-xs font-black uppercase tracking-widest transition-all">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { studentArchiveService } from '@/services/Student/studentArchiveService'
import { useNotificationStore } from '@/stores/notification'
import { useUserStore } from '@/stores/user'

const notificationStore = useNotificationStore()
const userStore = useUserStore()
const loading = ref(true)
const archivedSections = ref([])
const selectedSection = ref(null)

// Show banner if student was just redirected here because their section was archived
const showArchivedBanner = computed(() => userStore.sectionArchived)

const dismissBanner = () => {
  userStore.setSectionArchived(false, '')
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const openSection = (section) => {
  selectedSection.value = section
}

onMounted(async () => {
  try {
    const data = await studentArchiveService.getArchivedSections()
    archivedSections.value = data.archived_sections || []
  } catch (e) {
    notificationStore.error('Failed to load archived sections.')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.banner-fade-enter-active, .banner-fade-leave-active {
  transition: all 0.3s ease;
}
.banner-fade-enter-from, .banner-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
