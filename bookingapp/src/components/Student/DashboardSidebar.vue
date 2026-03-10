<template>
  <div 
    :class="[
      'bg-pink-500 text-white transition-all duration-300 ease-in-out flex flex-col shadow-lg overflow-hidden', 
      sidebarOpen ? 'w-56' : 'w-0'
    ]"
  >
    <div v-show="sidebarOpen" class="flex flex-col h-full overflow-y-auto">
      <!-- Home Button -->
      <router-link 
        to="/student/home"
        class="flex items-center px-5 py-4 hover:bg-white/10 transition-all border-b border-white/5 group"
        active-class="bg-white/20 font-bold"
      >
        <div class="w-8 h-8 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
        </div>
        <span class="text-sm tracking-wide ml-4 whitespace-nowrap">Home</span>
      </router-link>

      <!-- Calendar Button -->
      <router-link 
        to="/student/calendar"
        class="flex items-center px-5 py-4 hover:bg-white/10 transition-all border-b border-white/5 group"
        active-class="bg-white/20 font-bold"
      >
        <div class="w-8 h-8 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </div>
        <span class="text-sm tracking-wide ml-4 whitespace-nowrap">Calendar</span>
      </router-link>

      <!-- Tasks Button -->
      <router-link 
        to="/student/tasks"
        class="flex items-center px-5 py-4 hover:bg-white/10 transition-all border-b border-white/5 group"
        active-class="bg-white/20 font-bold"
      >
        <div class="w-8 h-8 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
        </div>
        <span class="text-sm tracking-wide ml-4 whitespace-nowrap">Tasks</span>
      </router-link>

      <!-- My Section (Only if enrolled) -->
      <router-link 
        v-if="section"
        to="/student/dashboard"
        class="flex items-center px-5 py-5 bg-black/10 border-b border-white/5 mt-auto hover:bg-black/20 transition-all group"
        active-class="bg-pink-700 font-bold shadow-inner"
      >
        <div class="w-10 h-10 rounded-2xl bg-white text-pink-600 flex items-center justify-center font-bold text-lg flex-shrink-0 shadow-lg group-hover:rotate-6 transition-transform">
          {{ section.section_code?.charAt(0).toUpperCase() || section.section_name?.charAt(0).toUpperCase() }}
        </div>
        <div class="ml-4 flex-1 overflow-hidden">
          <span class="block truncate text-sm font-bold tracking-tight uppercase">
            {{ section.section_code || section.section_name }}
          </span>
          <span class="text-[10px] opacity-75 font-medium flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
            {{ section.activities_count || 0 }} activities
          </span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardSidebar',
  props: {
    sidebarOpen: {
      type: Boolean,
      required: true
    },
    section: {
      type: Object,
      default: null
    }
  }
}
</script>
