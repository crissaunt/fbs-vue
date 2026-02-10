<template>
  <div class="h-screen bg-gray-100 flex ">
    <nav
      :class="[
        'sidebar text-white bg-[#fe3787] flex flex-col items-start transition-all duration-300 fixed h-screen z-50 ',
        collapsed ? 'w-16' : 'w-64'
      ]"
    >
    <button
      @click="toggleSidebar"
      class="absolute -right-3 top-1/2 -translate-y-1/2
            bg-white text-black rounded-full p-1 shadow-md z-50
            flex items-center justify-center border border-gray-200"
    >
      <i :class="collapsed ? 'ph ph-caret-right' : 'ph ph-caret-left'" class="text-xs"></i>
    </button>

      <div id="sidebar-content" class="w-full h-full overflow-y-auto flex flex-col py-4">
      <div class="mt-4 mb-8 flex items-center w-full px-4">
        <img src="@/assets/admin/cthm-logos.png" class="w-12 h-12 flex-shrink-0" />
        <span v-if="!collapsed" class="ml-3 font-bold leading-tight text-white text-[15px] poppins">
          Caraga State University <br/>
          <span class="font-semibold opacity-90">Cabadbaran Campus</span>
        </span>
      </div>

      <div class="w-full space-y-1 flex-1">
        <hr class="border-white/15 my-4 mx-4" />

        <router-link 
          to="/admin/dashboard" 
          class="flex items-center px-4 py-3 text-white hover:bg-white/10 transition-colors group"
          active-class="bg-white/10 border-l-4 border-white"
        >
          <i class="ph ph-squares-four text-xl"></i>
          <span v-if="!collapsed" class="ml-3 text-[14px] font-medium">Dashboard</span>
        </router-link>

        <SidebarGroup title="Manage Flight" icon="ph-airplane">
          <SidebarSubLink label="Routes" to="/admin/manage-flight/routes" />
          <SidebarSubLink label="Flights" to="/admin/manage-flight/flights" /> 
          <SidebarSubLink label="Schedules" to="/admin/manage-flight/schedules" />
          <SidebarSubLink label="Seats Maps" to="/admin/manage-flight/seats" />
        </SidebarGroup>

        <SidebarGroup title="Assets" icon="ph-package">
          <SidebarSubLink label="Airports" to="/admin/assets/airports" />
          <SidebarSubLink label="Add-Ons" to="/admin/assets/add-ons" />
          <SidebarSubLink label="Seat Classes" to="/admin/assets/seat-classes" />
          <SidebarSubLink label="Airlines" to="/admin/assets/airlines" />
          <SidebarSubLink label="Aircraft" to="/admin/assets/aircraft" />
        </SidebarGroup>

        <SidebarGroup title="Booking" icon="ph-receipt">
          <SidebarSubLink label="Booking Details" to="/admin/booking/details" />
          <SidebarSubLink label="Bookings" to="/admin/booking/list" />
          <SidebarSubLink label="Payments" to="/admin/booking/payments" />
        </SidebarGroup>

        <SidebarGroup title="Passenger" icon="ph-users">
          <SidebarSubLink label="Passengers" to="/admin/passenger/list" />
          <SidebarSubLink label="Check-Ins" to="/admin/passenger/check-ins" />
        </SidebarGroup>

        <SidebarGroup title="Student Info" icon="ph-student">
          <SidebarSubLink label="Student" to="/admin/student-info/list" />
          <SidebarSubLink label="Track Log" to="/admin/student-info/track-log" />
        </SidebarGroup>

        <SidebarGroup title="Instructor Info" icon="ph-chalkboard-teacher">
          <SidebarSubLink label="Instructor" to="/admin/instructor-info/list" />
        </SidebarGroup>

        <SidebarGroup title="Manage Tax" icon="ph-bank">
          <SidebarSubLink label="Airport Fee" to="/admin/manage-tax/airport-fee" />
          <SidebarSubLink label="Tax Type" to="/admin/manage-tax/tax-type" />
          <SidebarSubLink label="Airline Tax" to="/admin/manage-tax/airline-tax" />
          <SidebarSubLink label="Travel Tax" to="/admin/manage-tax/travel-tax" />
          <SidebarSubLink label="Booking Tax" to="/admin/manage-tax/booking-tax" />
        </SidebarGroup>
      </div>
      </div>
    </nav>

    <main 
      :class="['flex-1 flex flex-col min-h-screen transition-all duration-300', collapsed ? 'ml-16' : 'ml-64']"
    >
      <header class="h-16 flex items-center justify-between px-12 sticky top-0 z-40 
               bg-white/30 backdrop-blur-md border-b border-transparent">
        <div>
         <h1 class="text-xl font-bold text-[#002D1E] poppins">
          {{ pageTitle }}
          </h1>
          <p class="text-xs text-gray-500">Hi {{ adminName }}, have a nice day!</p>
        </div>

        <div class="flex items-center space-x-4">
          <div class="relative">
            <div 
              @click.stop="isProfileOpen = !isProfileOpen"
              class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] flex items-center cursor-pointer font-medium text-sm gap-2 hover:bg-[#fa1571] transition-all shadow-sm"
            >
              <i class="ph ph-user-circle text-xl"></i>
              <span>{{ adminName }}</span>
              <i :class="isProfileOpen ? 'ph-caret-up' : 'ph-caret-down'" class="ph text-xs transition-transform duration-200"></i>
            </div>

            <transition 
              enter-active-class="transition duration-100 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-in"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0"
            >
              <div 
                v-if="isProfileOpen" 
                class="absolute right-0 mt-2 w-48 bg-white shadow-xl  rounded-[1px] border border-gray-100 py-1 z-50 overflow-hidden"
              >
                <button   
                  @click="handleLogout"
                  class="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-colors gap-3"
                >
                  <i class="ph ph-sign-out text-lg"></i>
                  <span class="font-medium">Logout</span>
                </button>
              </div>
            </transition>
          </div>
        </div>
      </header>

      <div class="p-6 bg-gray-100 flex-1">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, provide, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

// Import child components
import SidebarGroup from '@/components/admin/SidebarGroup.vue';
import SidebarSubLink from '@/components/admin/SidebarSubLink.vue';

const collapsed = ref(false);
const isProfileOpen = ref(false);
const adminName = ref('Admin');

const router = useRouter();
const route = useRoute();

/* -------------------------
   Sidebar
-------------------------- */
const toggleSidebar = () => {
  collapsed.value = !collapsed.value;
};

/* -------------------------
   Logout
-------------------------- */
const handleLogout = () => {
  localStorage.removeItem('adminLoggedIn');
  localStorage.removeItem('adminName');
  router.push('/admin/login');
};

/* -------------------------
   Profile dropdown
-------------------------- */
const closeDropdown = (e) => {
  if (!e.target.closest('.relative')) {
    isProfileOpen.value = false;
  }
};

/* -------------------------
   🔥 Dynamic Page Title
-------------------------- */
const pageTitle = computed(() => {
  return route.meta.title || 'Dashboard';
});

// Optional: update browser tab title
watch(
  () => route.meta.title,
  (title) => {
    document.title = title ? `${title} | Admin Panel` : 'Admin Panel';
  },
  { immediate: true }
);

/* -------------------------
   Lifecycle
-------------------------- */
onMounted(() => {
  const storedName = localStorage.getItem('adminName');
  if (storedName) {
    adminName.value = storedName;
  }

  window.addEventListener('click', closeDropdown);
});

onUnmounted(() => {
  window.removeEventListener('click', closeDropdown);
});

/* -------------------------
   Provide sidebar state
-------------------------- */
provide('isSidebarCollapsed', collapsed);
</script>


<style scoped>
.poppins {
  font-family: 'Poppins', sans-serif;
}

#sidebar-content::-webkit-scrollbar {
  width: 4px;
}
#sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
</style>