<template>
  <div class="p-4 lg:p-8 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center gap-3 mb-1">
        <div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8M10 12v4M14 12v4" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-slate-800 tracking-tight">Archived Sections</h2>
      </div>
      <p class="text-sm text-slate-500 ml-11">Read-only view of archived sections. No new activities or enrollments can be added.</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-pink-500"></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="archivedSections.length === 0" class="bg-white rounded-2xl border-2 border-dashed border-slate-200 p-16 text-center">
      <div class="w-20 h-20 bg-amber-50 rounded-full flex items-center justify-center mx-auto mb-5">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-amber-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8M10 12v4M14 12v4" />
        </svg>
      </div>
      <h3 class="text-lg font-bold text-slate-700 mb-2">No Archived Sections</h3>
      <p class="text-slate-500 text-sm max-w-xs mx-auto">Sections you archive will appear here. You can archive a section from the dashboard.</p>
    </div>

    <!-- Archived sections grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <div
        v-for="section in archivedSections"
        :key="section.id"
        @click="openSection(section)"
        class="group bg-white rounded-2xl shadow-sm border border-amber-100 hover:border-amber-300 overflow-hidden transition-all duration-300 cursor-pointer flex flex-col relative"
      >
        <!-- Archived banner -->
        <div class="bg-amber-50 border-b border-amber-100 px-4 py-1.5 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8l1 12a2 2 0 002 2h8a2 2 0 002-2L19 8" />
          </svg>
          <span class="text-[9px] font-black uppercase tracking-widest text-amber-600">Archived · {{ formatDate(section.archived_at) }}</span>
        </div>

        <div class="p-4 flex-1 flex flex-col">
          <div class="flex items-center gap-2.5 mb-3">
            <div class="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center font-bold text-base text-amber-600 border border-amber-100 flex-shrink-0">
              {{ section.section_name?.charAt(0) }}
            </div>
            <div class="min-w-0">
              <span class="text-[8px] font-black uppercase tracking-[0.2em] text-slate-400 block truncate mb-0.5">{{ section.section_code }}</span>
              <h3 class="text-xs font-black text-slate-800 group-hover:text-amber-600 transition-colors truncate leading-tight">{{ section.section_name }}</h3>
            </div>
          </div>

          <p class="text-[12px] text-slate-500 leading-relaxed line-clamp-2 mb-4">
            {{ section.description || 'No description provided.' }}
          </p>

          <div class="mt-auto grid grid-cols-3 gap-2 text-center">
            <div class="bg-slate-50 rounded-lg p-2 border border-slate-100">
              <p class="text-base font-black text-slate-700">{{ section.student_count }}</p>
              <p class="text-[8px] font-black uppercase tracking-widest text-slate-400">Students</p>
            </div>
            <div class="bg-slate-50 rounded-lg p-2 border border-slate-100">
              <p class="text-base font-black text-slate-700">{{ section.activity_count }}</p>
              <p class="text-[8px] font-black uppercase tracking-widest text-slate-400">Activities</p>
            </div>
            <div class="bg-slate-50 rounded-lg p-2 border border-slate-100">
              <p class="text-[10px] font-black text-slate-700">{{ section.semester }}</p>
              <p class="text-[8px] font-black uppercase tracking-widest text-slate-400">Semester</p>
            </div>
          </div>
        </div>

        <div class="px-4 pb-3.5 flex justify-between items-center border-t border-slate-100 pt-2.5">
          <button
            @click.stop="confirmUnarchive(section)"
            class="text-[9px] font-bold text-amber-600 hover:text-amber-700 bg-amber-50 hover:bg-amber-100 px-2.5 py-1 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Restore
          </button>
          <span class="text-[9px] text-slate-400 font-medium">{{ section.academic_year }}</span>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedSection" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4" @click.self="selectedSection = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Modal Header -->
        <div class="bg-gradient-to-r from-amber-600 to-amber-500 text-white px-6 py-4 flex justify-between items-center">
          <div>
            <p class="text-[9px] font-black uppercase tracking-[0.2em] text-amber-200 mb-0.5">{{ selectedSection.section_code }} · Archived</p>
            <h3 class="text-lg font-black">{{ selectedSection.section_name }}</h3>
          </div>
          <button @click="selectedSection = null" class="text-white/70 hover:text-white transition-colors text-2xl leading-none">&times;</button>
        </div>

        <!-- Read-only badge -->
        <div class="bg-amber-50 border-b border-amber-100 px-6 py-2 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <span class="text-[10px] font-bold text-amber-700">Read-only — No new activities or enrollments can be added to archived sections.</span>
        </div>

        <div class="overflow-y-auto flex-1">
          <!-- Section Info -->
          <div class="p-6 grid grid-cols-2 sm:grid-cols-4 gap-4 border-b border-slate-100">
            <div>
              <p class="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-1">Semester</p>
              <p class="text-sm font-bold text-slate-700">{{ selectedSection.semester }}</p>
            </div>
            <div>
              <p class="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-1">Academic Year</p>
              <p class="text-sm font-bold text-slate-700">{{ selectedSection.academic_year }}</p>
            </div>
            <div>
              <p class="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-1">Students</p>
              <p class="text-sm font-bold text-slate-700">{{ selectedSection.student_count }}</p>
            </div>
            <div>
              <p class="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-1">Archived On</p>
              <p class="text-sm font-bold text-slate-700">{{ formatDate(selectedSection.archived_at) }}</p>
            </div>
          </div>

          <!-- Activities -->
          <div class="p-6 border-b border-slate-100">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-3">Activities ({{ selectedSection.activities?.length || 0 }})</h4>
            <div v-if="!selectedSection.activities?.length" class="text-sm text-slate-400 italic">No activities created.</div>
            <div v-else class="space-y-2">
              <div v-for="activity in selectedSection.activities" :key="activity.id"
                class="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-3 border border-slate-100">
                <div>
                  <p class="text-sm font-bold text-slate-700">{{ activity.title }}</p>
                  <p class="text-[10px] text-slate-400 font-medium">{{ activity.activity_type }} · {{ activity.total_points }} pts</p>
                </div>
                <span :class="[
                  'text-[9px] font-black uppercase tracking-widest px-2 py-1 rounded-md',
                  activity.status === 'published' ? 'bg-green-50 text-green-600 border border-green-100' :
                  activity.status === 'closed' ? 'bg-red-50 text-red-500 border border-red-100' :
                  'bg-slate-100 text-slate-500'
                ]">{{ activity.status }}</span>
              </div>
            </div>
          </div>

          <!-- Enrolled Students -->
          <div class="p-6">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-3">Enrolled Students ({{ selectedSection.students?.length || 0 }})</h4>
            <div v-if="!selectedSection.students?.length" class="text-sm text-slate-400 italic">No students were enrolled.</div>
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div v-for="student in selectedSection.students" :key="student.id"
                class="flex items-center gap-3 bg-slate-50 rounded-lg px-4 py-3 border border-slate-100">
                <div class="w-7 h-7 rounded-full bg-pink-100 flex items-center justify-center font-bold text-[11px] text-pink-600 flex-shrink-0">
                  {{ student.first_name?.charAt(0) }}
                </div>
                <div class="min-w-0">
                  <p class="text-[12px] font-bold text-slate-700 truncate">{{ student.first_name }} {{ student.last_name }}</p>
                  <p class="text-[9px] text-slate-400 font-medium">{{ student.student_number }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3">
          <button @click="confirmUnarchive(selectedSection); selectedSection = null"
            class="px-5 py-2.5 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-xs font-black uppercase tracking-widest shadow-sm transition-all active:scale-95 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Restore Section
          </button>
          <button @click="selectedSection = null" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-black uppercase tracking-widest transition-all">
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Unarchive Confirm Modal -->
    <div v-if="unarchiveTarget" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-8 text-center">
        <div class="w-14 h-14 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        </div>
        <h3 class="text-lg font-black text-slate-800 mb-2">Restore Section?</h3>
        <p class="text-sm text-slate-500 mb-6">
          <strong>{{ unarchiveTarget.section_name }}</strong> will be restored to active. Students must be manually re-enrolled.
        </p>
        <div class="flex gap-3">
          <button @click="unarchiveTarget = null" class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-black uppercase tracking-widest transition-all">Cancel</button>
          <button @click="doUnarchive" :disabled="unarchiving" class="flex-1 py-3 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-xs font-black uppercase tracking-widest shadow-sm transition-all active:scale-95 disabled:opacity-60">
            {{ unarchiving ? 'Restoring...' : 'Yes, Restore' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

const loading = ref(true)
const archivedSections = ref([])
const selectedSection = ref(null)
const unarchiveTarget = ref(null)
const unarchiving = ref(false)

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const openSection = (section) => {
  selectedSection.value = section
}

const confirmUnarchive = (section) => {
  unarchiveTarget.value = section
}

const doUnarchive = async () => {
  if (!unarchiveTarget.value) return
  unarchiving.value = true
  try {
    await instructorDashboardService.unarchiveSection(unarchiveTarget.value.id)
    notificationStore.success(`Section "${unarchiveTarget.value.section_name}" has been restored!`)
    archivedSections.value = archivedSections.value.filter(s => s.id !== unarchiveTarget.value.id)
    unarchiveTarget.value = null
  } catch (e) {
    notificationStore.error(e?.response?.data?.error || 'Failed to restore section.')
  } finally {
    unarchiving.value = false
  }
}

onMounted(async () => {
  try {
    const data = await instructorDashboardService.getArchivedSections()
    archivedSections.value = data.archived_sections || []
  } catch (e) {
    notificationStore.error('Failed to load archived sections.')
  } finally {
    loading.value = false
  }
})
</script>
