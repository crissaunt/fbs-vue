<template>
  <div class="flex flex-col h-screen bg-gray-200">
    <!-- SECTION ARCHIVED BANNER -->
    <Transition name="banner-slide">
      <div
        v-if="sectionArchivedBanner"
        class="fixed inset-0 z-[200] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      >
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
          <div class="bg-amber-500 px-6 py-4 flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
              <i class="ph ph-archive text-2xl text-white"></i>
            </div>
            <div>
              <h3 class="text-sm font-black text-white uppercase tracking-widest">Section Archived</h3>
              <p class="text-amber-100 text-[10px] font-bold uppercase tracking-widest">Your enrollment has ended</p>
            </div>
          </div>
          <div class="p-6">
            <p class="text-slate-700 text-sm font-medium leading-relaxed mb-2">
              Your section <strong class="text-amber-600">{{ archivedSectionName }}</strong> has been archived by your instructor.
            </p>
            <p class="text-slate-500 text-xs leading-relaxed mb-4">
              You have been automatically unenrolled. You can still view your archived section history in the <strong>Archive</strong> tab after logging in again. You will be redirected to enroll in a new section.
            </p>
            <div class="bg-amber-50 border border-amber-100 rounded-xl p-3 flex items-center gap-3">
              <div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <i class="ph ph-clock-countdown text-amber-600 text-lg"></i>
              </div>
              <p class="text-amber-700 text-xs font-bold">Logging out in <span class="text-amber-600 text-sm font-black">{{ logoutCountdown }}</span> second{{ logoutCountdown !== 1 ? 's' : '' }}...</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- TOP HEADER -->
    <DashboardHeader
      :student="userStore.studentProfile || {}"
      @toggle-sidebar="toggleSidebar"
      @logout="handleLogout"
    />

    <!-- MAIN CONTENT WITH SIDEBAR -->
    <div class="flex flex-1 overflow-hidden relative">
      <!-- LEFT SIDEBAR - Becomes a drawer on mobile -->
      <DashboardSidebar
        :sidebar-open="sidebarOpen"
        :section="section"
        :archived-section-count="archivedSectionCount"
        @close-sidebar="sidebarOpen = false"
      />

      <!-- RIGHT CONTENT AREA -->
      <main class="flex-1 flex flex-col bg-gray-200 overflow-y-auto">
        <router-view v-if="!loading" :section="section" :activities="activities" :classmates="classmates" :instructor="instructor" />

        <!-- Loading State -->
        <div v-else class="flex-1 flex items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500"></div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { studentDashboardService } from '@/services/Student/studentDashboardService.js'
import { studentArchiveService } from '@/services/Student/studentArchiveService.js'
import DashboardHeader from '@/components/Student/DashboardHeader.vue'
import DashboardSidebar from '@/components/Student/DashboardSidebar.vue'

export default {
  name: 'StudentLayout',
  components: {
    DashboardHeader,
    DashboardSidebar
  },
  setup() {
    const userStore = useUserStore()
    const router = useRouter()
    const sidebarOpen = ref(window.innerWidth >= 1024)
    const section = ref(null)
    const activities = ref([])
    const classmates = ref([])
    const instructor = ref(null)
    const loading = ref(true)

    // Archive notification state
    const sectionArchivedBanner = ref(false)
    const archivedSectionName = ref('')
    const archivedSectionCode = ref('')
    const logoutCountdown = ref(5)
    const archivedSectionCount = ref(0)
    let countdownInterval = null

    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value
    }

    const handleLogout = () => {
      userStore.logout()
      router.push('/login')
    }

    const triggerArchivedLogout = (sectionName, sectionCode) => {
      archivedSectionName.value = sectionName
      archivedSectionCode.value = sectionCode
      sectionArchivedBanner.value = true
      logoutCountdown.value = 5

      countdownInterval = setInterval(() => {
        logoutCountdown.value--
        if (logoutCountdown.value <= 0) {
          clearInterval(countdownInterval)
          userStore.logout()
          router.push('/login')
        }
      }, 1000)
    }

    const fetchArchivedCount = async () => {
      try {
        const data = await studentArchiveService.getArchivedSections()
        archivedSectionCount.value = (data.archived_sections || []).length
      } catch {
        archivedSectionCount.value = 0
      }
    }

    const loadData = async () => {
      try {
        loading.value = true
        const response = await studentDashboardService.getStudentDashboard()

        if (response.data?.not_enrolled) {
          userStore.setEnrolled(false)
          return
        }

        userStore.setEnrolled(true)
        if (response.data?.user) {
          userStore.setStudentProfile(response.data.user)
        }

        section.value = response.data.section || null
        activities.value = response.data.activities || []
        classmates.value = response.data.classmates || []
        instructor.value = response.data.instructor || null

        // Fetch archived section count for sidebar badge
        fetchArchivedCount()
      } catch (error) {
        console.error("Error loading layout data:", error)
        const httpStatus = error.response?.status
        const errData = error.response?.data

        // 401 = session token was deactivated (section archived → token killed by backend)
        // The axios interceptor skips global 401-redirect for student/dashboard URLs,
        // so we must handle it explicitly here.
        if (httpStatus === 401) {
          userStore.logout()
          router.push('/login')
          return
        }

        // 403 section_archived = backend fallback when session is still alive but section was archived.
        // (Normal flow: login redirects to /student/archive. This handles edge cases.)
        if (errData?.section_archived) {
          if (errData.user) userStore.setStudentProfile(errData.user)
          userStore.setEnrolled(false)
          userStore.setSectionArchived(true, errData.archived_section_name || '')
          // Redirect to archive so they can see their history — no logout loop
          router.push('/student/archive')
          return
        }

        if (errData?.not_enrolled) {
          userStore.setEnrolled(false)
          if (errData.user) {
            userStore.setStudentProfile(errData.user)
          }
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadData()
    })

    onUnmounted(() => {
      if (countdownInterval) clearInterval(countdownInterval)
    })

    return {
      userStore,
      sidebarOpen,
      section,
      activities,
      classmates,
      instructor,
      loading,
      sectionArchivedBanner,
      archivedSectionName,
      archivedSectionCode,
      logoutCountdown,
      archivedSectionCount,
      toggleSidebar,
      handleLogout
    }
  }
}
</script>

<style scoped>
.banner-slide-enter-active, .banner-slide-leave-active {
  transition: opacity 0.3s ease;
}
.banner-slide-enter-from, .banner-slide-leave-to {
  opacity: 0;
}
</style>

