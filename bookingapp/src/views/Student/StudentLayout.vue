<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- TOP HEADER -->
    <DashboardHeader 
      :student="userStore.studentProfile || {}" 
      @toggle-sidebar="toggleSidebar" 
      @logout="handleLogout" 
    />

    <!-- MAIN CONTENT WITH SIDEBAR -->
    <div class="flex flex-1 overflow-hidden">
      <!-- LEFT SIDEBAR -->
      <DashboardSidebar 
        :sidebar-open="sidebarOpen" 
        :section="section" 
      />

      <!-- RIGHT CONTENT AREA -->
      <main class="flex-1 flex flex-col bg-gray-50 overflow-y-auto">
        <router-view v-if="!loading" :section="section" :activities="activities" />
        
        <!-- Loading State -->
        <div v-else class="flex-1 flex items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500"></div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { studentDashboardService } from '@/services/Student/studentDashboardService.js'
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
    const sidebarOpen = ref(false)
    const section = ref(null)
    const activities = ref([])
    const loading = ref(true)

    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value
    }

    const handleLogout = () => {
      userStore.logout()
      router.push('/login')
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
      } catch (error) {
        console.error("Error loading layout data:", error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      userStore,
      sidebarOpen,
      section,
      activities,
      loading,
      toggleSidebar,
      handleLogout
    }
  }
}
</script>
