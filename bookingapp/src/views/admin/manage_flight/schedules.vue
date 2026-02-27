<template>
  <div class="p-6 poppins">
    <!-- Header Section -->
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
      >
        <i class="ph ph-plus"></i> Add Schedule
      </button>
    </div>

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div 
        v-for="(count, label) in statsItems" 
        :key="label" 
        class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins leading-none mb-2">{{ label }}</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ count }}</p>
          </div>
          <div :class="statIconClass(label)" class="w-12 h-12 rounded-full flex items-center justify-center">
            <i :class="[statIcon(label), 'text-xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Flight</th>
            <th class="px-6 py-4 poppins">Departure / Arrival</th>
            <th class="px-6 py-4 poppins">Duration</th>
            <th class="px-6 py-4 poppins text-center">Status</th>
            <th class="px-6 py-4 poppins text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="s in paginatedSchedules" 
            :key="s.id" 
            :id="`schedule-row-${s.id}`"
            :class="{'highlight-active': highlightedId === s.id}"
            class="hover:bg-gray-50/50 transition-all text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <i class="ph ph-airplane text-blue-600"></i>
                </div>
                <div>
                  <router-link 
                    :to="{ name: 'ManageFlights', query: { highlight: s.flight } }" 
                    class="font-bold text-[#fe3787] block poppins hover:underline hover:text-[#fb1873] transition-all flex items-center gap-1 group"
                    title="View Flight Connection"
                  >
                    {{ s.flight_number }}
                    <i class="ph ph-link-simple text-[10px] opacity-0 group-hover:opacity-100 transition-opacity"></i>
                  </router-link>
                  <div class="flex items-center gap-1 mt-1">
                    <span class="text-[9px] text-gray-400 font-bold uppercase poppins tracking-tighter">Sch ID: {{ s.id }}</span>
                    <span v-if="s.flight_detail" 
                      :class="s.flight_detail.total_stops === 0 ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'"
                      class="px-1.5 py-0.5 rounded-[1px] text-[8px] font-black uppercase poppins ml-1"
                    >
                      {{ s.flight_detail.total_stops === 0 ? 'Non-stop' : `${s.flight_detail.total_stops} Stop` }}
                    </span>
                    <div class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse ml-1" title="System Connected"></div>
                  </div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex flex-col gap-2">
                <div>
                  <p class="text-[9px] font-black uppercase text-gray-400 tracking-widest poppins mb-0.5">Departure</p>
                  <span class="font-bold text-[#002D1E] poppins block">{{ formatDate(s.departure_time) }}</span>
                  <span class="text-[11px] text-[#fe3787] font-semibold poppins">{{ formatTime(s.departure_time) }}</span>
                </div>
                <div>
                  <p class="text-[9px] font-black uppercase text-gray-400 tracking-widest poppins mb-0.5">Arrival</p>
                  <span class="font-bold text-[#002D1E] poppins block">{{ formatDate(s.arrival_time) }}</span>
                  <span class="text-[11px] text-blue-500 font-semibold poppins">{{ formatTime(s.arrival_time) }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 poppins text-gray-500 italic">
              {{ s.duration_display }}
            </td>
            <td class="px-6 py-4 text-center">
              <span 
                :class="statusClass(s.status)" 
                class="px-3 py-1 rounded-full text-[10px] font-bold uppercase poppins"
              >
                {{ s.status }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="deleteSchedule(s.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="schedules.length === 0">
            <td colspan="6" class="px-6 py-10 text-center text-gray-400 italic poppins">No flight schedules found.</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Section -->
      <div v-if="schedules.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ schedules.length }}
          </div>
          <div class="flex gap-1">
            <button 
              @click="prevPage" 
              :disabled="currentPage === 1"
              class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
            >
              Prev
            </button>
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="goToPage(page)"
              :disabled="page === '...'"
              :class="[
                'px-4 py-2 border rounded-[1px] text-xs font-bold uppercase poppins transition-all shadow-sm',
                page === '...' ? 'bg-white border-gray-200 text-gray-400' : 
                currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'bg-white border-gray-200 text-[#002D1E] hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
              class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">New Flight Schedule</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>

        <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 animate-pulse">
          <div class="flex items-center gap-3">
            <i class="ph ph-warning-circle-bold text-xl"></i>
            <span class="text-xs font-bold uppercase poppins leading-tight">{{ errorMessage }}</span>
          </div>
        </div>

        <form @submit.prevent="saveSchedule" class="space-y-6">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Select Flight Number</label>
            <select v-model="form.flight" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] bg-white" required>
              <option :value="null" disabled>Choose a flight number...</option>
              <option v-for="f in flightList" :key="f.id" :value="f.id">{{ f.flight_number }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Departure Date & Time</label>
              <input v-model="form.departure_time" type="datetime-local" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Arrival Date & Time</label>
              <input v-model="form.arrival_time" type="datetime-local" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
          </div>



          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" :disabled="loading" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ loading ? 'Validating...' : 'Confirm Schedule' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';

const modalStore = useModalStore();
const route = useRoute();

const schedules = ref([]);
const flightList = ref([]);
const isModalOpen = ref(false);
const loading = ref(false);
const errorMessage = ref(null);
const highlightedId = ref(null);

const form = ref({
  flight: null,
  departure_time: '',
  arrival_time: ''
});

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;

// Computed Stats
const statsItems = computed(() => {
  return {
    'Total Flights': schedules.value.length,
    'Open for Booking': schedules.value.filter(s => s.status === 'Open').length,
    'Currently In-Air': schedules.value.filter(s => s.status === 'On Flight').length,
    'Completed': schedules.value.filter(s => s.status === 'Arrived').length,
  };
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(schedules.value.length / itemsPerPage));
const paginatedSchedules = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return schedules.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, schedules.value.length));

const visiblePages = computed(() => {
  const pages = [];
  const t = totalPages.value;
  const c = currentPage.value;
  if (t <= 5) {
    for (let i = 1; i <= t; i++) pages.push(i);
  } else {
    if (c <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i);
      pages.push('...', t);
    } else if (c >= t - 2) {
      pages.push(1, '...');
      for (let i = t - 3; i <= t; i++) pages.push(i);
    } else {
      pages.push(1, '...', c - 1, c, c + 1, '...', t);
    }
  }
  return pages;
});

const statIcon = (label) => {
  if (label === 'Total Flights') return 'ph ph-airplane';
  if (label === 'Open for Booking') return 'ph ph-ticket';
  if (label === 'Currently In-Air') return 'ph ph-airplane-in-flight';
  return 'ph ph-checks';
};

const statIconClass = (label) => {
  if (label === 'Total Flights') return 'bg-blue-100 text-blue-600';
  if (label === 'Open for Booking') return 'bg-green-100 text-green-600';
  if (label === 'Currently In-Air') return 'bg-purple-100 text-purple-600';
  return 'bg-pink-100 text-pink-600';
};

const fetchData = async () => {
  try {
    const [resS, resF] = await Promise.all([
      api.get('/schedules/'),
      api.get('/flights/')
    ]);
    schedules.value = resS.data.results || resS.data;
    flightList.value = resF.data.results || resF.data;

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = schedules.value.findIndex(s => s.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`schedule-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) {
    console.error("Fetch Error:", err);
  }
};

const saveSchedule = async () => {
  loading.value = true;
  errorMessage.value = null;
  
  if (!form.value.flight) {
    errorMessage.value = "Please select a flight.";
    loading.value = false;
    return;
  }
  
  const payload = {
    flight: parseInt(form.value.flight),
    departure_time: form.value.departure_time,
    arrival_time: form.value.arrival_time
  };
  
  try {
    await api.post('/schedules/', payload);
    await fetchData();
    isModalOpen.value = false;
  } catch (err) {
    if (err.response && err.response.data) {
      const data = err.response.data;
      if (data.flight) errorMessage.value = `Flight: ${data.flight.join(', ')}`;
      else if (data.non_field_errors) errorMessage.value = data.non_field_errors.join(', ');
      else if (data.detail) errorMessage.value = data.detail;
      else errorMessage.value = "An error occurred. Check inputs.";
    } else {
      errorMessage.value = "Connection error.";
    }
  } finally {
    loading.value = false;
  }
};

const openModal = () => {
  form.value = { flight: null, departure_time: '', arrival_time: '' };
  errorMessage.value = null;
  isModalOpen.value = true;
};

const deleteSchedule = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Purge Schedule?',
    message: 'Are you sure you want to permanently remove this schedule?',
    variant: 'danger',
    confirmText: 'Purge',
    loadingText: 'Purging...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/schedules/${id}/`);
      await fetchData();
      modalStore.close(true);
    } catch (err) {
      console.error("Delete Error:", err);
      modalStore.setLoader(false);
    }
  }
};

const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const goToPage = (p) => { if (p !== '...') currentPage.value = p; };

// UI Helpers
const formatTime = (d) => new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
const formatDate = (d) => new Date(d).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
const statusClass = (s) => {
  if (s === 'Open') return 'bg-green-100 text-green-700';
  if (s === 'Closed') return 'bg-pink-100 text-pink-700';
  if (s === 'On Flight') return 'bg-blue-100 text-blue-700';
  if (s === 'Arrived') return 'bg-purple-100 text-purple-700';
  return 'bg-gray-100 text-gray-500';
};

onMounted(fetchData);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

@keyframes pulse-highlight {
  0% { background-color: rgba(254, 55, 135, 0.05); }
  50% { background-color: rgba(254, 55, 135, 0.2); }
  100% { background-color: rgba(254, 55, 135, 0.05); }
}

.highlight-active {
  animation: pulse-highlight 1.5s ease-in-out infinite;
  border-left: 4px solid #fe3787 !important;
  box-shadow: inset 0 0 20px rgba(254, 55, 135, 0.1);
}

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
