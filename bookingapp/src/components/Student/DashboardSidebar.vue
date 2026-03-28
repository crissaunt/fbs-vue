<template>
  <div class="sidebar-wrapper">
    <!-- Overlay for mobile -->
    <div 
      v-if="sidebarOpen" 
      class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-[90] lg:hidden"
      @click="$emit('close-sidebar')"
    ></div>

    <div 
      :class="[
        'bg-[#F9F9F9] text-gray-800 transition-all duration-300 ease-in-out flex flex-col font-normal overflow-hidden z-[100] lg:z-0',
        'fixed inset-y-0 left-0 lg:relative lg:inset-auto lg:h-full',
        sidebarOpen ? 'translate-x-0 w-64' : '-translate-x-full lg:translate-x-0 w-64 lg:w-[88px]'
      ]"
    >
      <div class="flex-shrink-0 w-full flex flex-col h-full overflow-y-auto space-y-3 mt-6">
        <!-- Home Button -->
        <router-link 
          to="/student/dashboard"
          :class="['flex items-center rounded-2xl sm:rounded-full hover:bg-[#FF579A]/10 hover:text-[#FF579A] transition-all group', sidebarOpen ? 'mx-4 px-4 py-3' : 'mx-auto justify-center w-14 h-14']"
          active-class="bg-[#FF579A] !text-white hover:bg-[#FF579A]/90 shadow-sm"
        >
          <div class="flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
            <i class="ph ph-house text-2xl"></i>
          </div>
          <span v-show="sidebarOpen" class="text-base font-medium tracking-wide ml-4 whitespace-nowrap">Dashboard</span>
        </router-link>

        <!-- Calendar Button -->
        <router-link 
          to="/student/calendar"
          :class="['flex items-center rounded-2xl sm:rounded-full hover:bg-[#FF579A]/10 hover:text-[#FF579A] transition-all group', sidebarOpen ? 'mx-4 px-4 py-3' : 'mx-auto justify-center w-14 h-14']"
          active-class="bg-[#FF579A] !text-white hover:bg-[#FF579A]/90 shadow-sm"
        >
          <div class="flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
            <i class="ph ph-calendar text-2xl"></i>
          </div>
          <span v-show="sidebarOpen" class="text-base font-medium tracking-wide ml-4 whitespace-nowrap">Calendar</span>
        </router-link>

        <!-- Tasks Button -->
        <router-link 
          to="/student/tasks"
          :class="['flex items-center rounded-2xl sm:rounded-full hover:bg-[#FF579A]/10 hover:text-[#FF579A] transition-all group', sidebarOpen ? 'mx-4 px-4 py-3' : 'mx-auto justify-center w-14 h-14']"
          active-class="bg-[#FF579A] !text-white hover:bg-[#FF579A]/90 shadow-sm"
        >
          <div class="flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
            <i class="ph ph-list-checks text-2xl"></i>
          </div>
          <span v-show="sidebarOpen" class="text-base font-medium tracking-wide ml-4 whitespace-nowrap">My Tasks</span>
        </router-link>

        <!-- My Section (Only if enrolled) -->
        <router-link 
          v-if="section"
          to="/student/dashboard"
          class="flex items-center mt-auto transition-all group justify-center no-underline border-t border-gray-200/50"
          :class="sidebarOpen ? 'w-full px-6 py-5 hover:bg-black/5' : 'mx-auto w-[88px] py-6 hover:bg-black/5'"
        >
          <div :class="['rounded-2xl bg-white text-[#FF579A] flex items-center justify-center font-bold text-xl flex-shrink-0 shadow-sm transition-all border border-pink-100', sidebarOpen ? 'w-12 h-12 group-hover:rotate-6' : 'w-12 h-12']">
            {{ section.section_code?.charAt(0).toUpperCase() || section.section_name?.charAt(0).toUpperCase() }}
          </div>
          <div v-show="sidebarOpen" class="ml-4 flex-1 overflow-hidden">
            <span class="block truncate text-sm font-black tracking-tight uppercase text-gray-800">
              {{ section.section_code || section.section_name }}
            </span>
            <span class="text-[10px] text-gray-500 font-bold flex items-center gap-1.5 mt-0.5">
              <span class="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.6)]"></span>
              {{ section.activities_count || 0 }} Activities
            </span>
          </div>
        </router-link>
      </div>
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
