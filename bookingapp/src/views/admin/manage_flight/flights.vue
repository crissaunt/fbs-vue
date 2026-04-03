<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search flight number..."
    >
      <template #filters>
        <div class="flex items-center gap-2">
          <select 
            v-model="filterAirline"
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer min-w-[150px]"
          >
            <option value="all">Any Airline</option>
            <option v-for="airline in airlines" :key="airline.id" :value="airline.id">
              {{ airline.name }}
            </option>
          </select>
        </div>
      </template>

      <template #actions>
        <div class="flex items-center gap-2">
          <button 
            @click="showImportModal = true" 
            class="bg-[#002D1E] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#014d33] font-semibold poppins text-[12px] rounded-[1px] shadow-sm transition-all"
          >
            <i class="ph ph-file-csv text-[14px]"></i> Import
          </button>
          <button 
            @click="openModal()" 
            class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[12px] rounded-[1px] shadow-sm transition-all"
          >
            <i class="ph ph-plus text-[14px]"></i> Add
          </button>
        </div>
      </template>
    </AdminTableTool>

    <!-- Import Modal -->
    <ImportModal 
      :show="showImportModal" 
      title="Flights" 
      model-type="flights" 
      @close="showImportModal = false"
      @refresh="fetchData"
    />

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
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
            <th class="px-6 py-4 poppins uppercase">Flight #</th>
            <th class="px-6 py-4 poppins uppercase">Airline</th>
            <th class="px-6 py-4 poppins uppercase">Aircraft</th>
            <th class="px-6 py-4 poppins uppercase">Route</th>
            <th class="px-6 py-4 poppins uppercase text-center">Profile Status</th>
            <th class="px-6 py-4 poppins text-right uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="f in paginatedFlights" 
            :key="f.id" 
            :id="`flight-row-${f.id}`"
            :class="{'highlight-active': highlightedId === f.id}"
            class="hover:bg-gray-50/50 transition-all text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex flex-col gap-1">
                <router-link 
                  :to="{ name: 'ManageRoutes', query: { highlight: f.route } }" 
                  class="font-bold text-[#fe3787] poppins text-sm hover:underline hover:text-[#fb1873] transition-all flex items-center gap-1 group"
                  title="View Route Connection"
                >
                  {{ f.flight_number }}
                  <i class="ph ph-link-simple text-[10px] opacity-0 group-hover:opacity-100 transition-opacity"></i>
                </router-link>
                <div class="flex items-center gap-1 mt-1">
                  <span class="text-[9px] text-gray-400 font-bold uppercase tracking-tighter poppins">Internal ID: {{ f.id }}</span>
                  <div class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" title="Connected to Backend"></div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                  <i class="ph ph-buildings text-blue-600"></i>
                </div>
                <router-link 
                  :to="{ name: 'AdminAirlines', query: { highlight: f.airline } }"
                  class="font-bold text-[#002D1E] poppins hover:text-[#fe3787] transition-all"
                  title="View Airline Connection"
                >
                  {{ f.airline_display }}
                </router-link>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <i class="ph ph-airplane-tilt text-purple-600"></i>
                <router-link 
                  :to="{ name: 'AdminAircraft', query: { highlight: f.aircraft } }"
                  class="text-gray-700 poppins hover:text-[#fe3787] transition-all font-medium"
                  title="View Aircraft Connection"
                >
                  {{ f.aircraft_display }}
                </router-link>
              </div>
            </td>
            <td class="px-6 py-4">
              <router-link 
                :to="{ name: 'ManageRoutes', query: { highlight: f.route } }"
                class="bg-purple-100 text-purple-700 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins tracking-tight hover:bg-[#fe3787] hover:text-white transition-all inline-block"
                title="View Route Details"
              >
                {{ f.route_display || 'No Route' }}
              </router-link>
            </td>
            <td class="px-6 py-4 text-center">
              <span 
                :class="f.is_active !== false ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'"
                class="px-3 py-1 rounded-[1px] text-[9px] font-black uppercase poppins border"
              >
                {{ f.is_active !== false ? 'Active Profile' : 'Inactive' }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(f)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteFlight(f.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="flights.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic poppins">No flights found. Please add one.</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Section -->
      <div v-if="flights.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ flights.length }}
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
          <h2 class="text-lg font-bold text-[#002D1E] poppins">
            {{ isEditing ? 'Edit Flight' : 'New Flight' }}
          </h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveFlight" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Flight Number</label>
            <input v-model="form.flight_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. PR101" required>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Airline Owner</label>
            <SearchableSelect
              v-model="form.airline"
              :options="airlineOptions"
              placeholder="Search and select airline..."
              label="Airline"
            />
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Aircraft Model</label>
            <SearchableSelect
              v-model="form.aircraft"
              :options="aircraftOptions"
              :disabled="!form.airline"
              :placeholder="form.airline ? 'Search and select aircraft...' : 'Select an airline first'"
              label="Aircraft"
            />
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Flight Route</label>
            <SearchableSelect
              v-model="form.route"
              :options="routeOptions"
              placeholder="Search by airport or city..."
              label="Route"
            />
          </div>

          <div class="flex items-center justify-between bg-gray-50 p-3 border border-gray-100 rounded-[1px] group transition-all hover:border-[#fe3787]">
            <div class="flex flex-col">
              <span class="text-[10px] font-bold uppercase text-[#002D1E] poppins">Active Profile</span>
              <span class="text-[9px] text-gray-400 font-medium poppins">Enable this flight for live monitoring</span>
            </div>
            <div 
              @click="form.is_active = !form.is_active"
              class="w-10 h-5 rounded-full relative cursor-pointer transition-all duration-300"
              :class="form.is_active ? 'bg-emerald-500' : 'bg-gray-300'"
            >
              <div class="absolute w-4 h-4 bg-white rounded-full top-0.5 transition-all duration-300" :class="form.is_active ? 'left-5.5' : 'left-0.5'"></div>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ isEditing ? 'Update Flight' : 'Confirm Flight' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
import ImportModal from '@/components/admin/ImportModal.vue';
import SearchableSelect from '@/components/admin/SearchableSelect.vue';
import AdminTableTool from '@/components/admin/AdminTableTool.vue';

const modalStore = useModalStore();

const flights = ref([]);
const airlines = ref([]);
const allAircrafts = ref([]);
const filteredAircrafts = ref([]);
const routes = ref([]);

// Searchable select options
const airlineOptions = computed(() =>
  airlines.value.map(a => ({ value: a.id, label: a.name, sublabel: `Code: ${a.code}` }))
);
const aircraftOptions = computed(() =>
  filteredAircrafts.value.map(ac => ({ value: ac.id, label: ac.model, sublabel: `${ac.capacity} seats` }))
);
const routeOptions = computed(() =>
  routes.value.map(r => ({ value: r.id, label: `${r.origin_info} → ${r.destination_info}` }))
);
const isModalOpen = ref(false);
const showImportModal = ref(false);
const isEditing = ref(false);
const currentId = ref(null);

const form = ref({
  flight_number: '',
  airline: '',
  aircraft: '',
  route: '',
  total_stops: 0
});

const searchQuery = ref('');
const filterAirline = ref('all');

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;

// --- Computed Stats ---
const statsItems = computed(() => {
  return {
    'Total Flights': flights.value.length,
    'Active Airlines': new Set(flights.value.map(f => f.airline)).size,
    'Operational Aircraft': new Set(flights.value.map(f => f.aircraft)).size,
  };
});

// Search & Filter Logic
const filteredFlights = computed(() => {
  let result = flights.value;
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(f => f.flight_number.toLowerCase().includes(q));
  }

  if (filterAirline.value !== 'all') {
    result = result.filter(f => f.airline === filterAirline.value);
  }
  
  return result;
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(filteredFlights.value.length / itemsPerPage));
const paginatedFlights = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredFlights.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredFlights.value.length));

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
  if (label === 'Active Airlines') return 'ph ph-buildings';
  return 'ph ph-airplane-tilt';
};

const statIconClass = (label) => {
  if (label === 'Total Flights') return 'bg-blue-100 text-blue-600';
  if (label === 'Active Airlines') return 'bg-green-100 text-green-600';
  return 'bg-purple-100 text-purple-600';
};

const highlightedId = ref(null);
const route = useRoute();

const fetchData = async () => {
  try {
    const [resF, resA, resAc, resR] = await Promise.all([
      api.get('/flights/'),
      api.get('/airlines/'),
      api.get('/aircraft/'),
      api.get('/routes/')
    ]);

    flights.value = resF.data.results || resF.data;
    airlines.value = resA.data.results || resA.data;
    allAircrafts.value = resAc.data.results || resAc.data;
    routes.value = resR.data.results || resR.data;

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    // Handle highlighted record from query params
    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = flights.value.findIndex(f => f.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`flight-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Clear highlight after 3 seconds
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) {
    console.error("Data fetch failed:", err.response?.data || err.message);
  }
};

watch(() => form.value.airline, (newAirlineId) => {
  if (newAirlineId) {
    filteredAircrafts.value = allAircrafts.value.filter(
      ac => ac.airline === newAirlineId
    );
    if (!filteredAircrafts.value.find(ac => ac.id === form.value.aircraft)) {
      form.value.aircraft = '';
    }
  } else {
    filteredAircrafts.value = [];
  }
});

const saveFlight = async () => {
  try {
    const payload = { ...form.value };
    payload.flight_number = payload.flight_number.toUpperCase().trim();

    if (isEditing.value) {
      await api.put(`/flights/${currentId.value}/`, payload);
    } else {
      await api.post('/flights/', payload);
    }
    
    await fetchData();
    isModalOpen.value = false;
  } catch (err) {
    console.error("Save error:", err.response?.data);
    alert("Error saving flight.");
  }
};

const deleteFlight = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Flight?',
    message: 'Are you sure you want to delete this flight record?',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/flights/${id}/`);
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

const openModal = (flight = null) => {
  isEditing.value = !!flight;
  currentId.value = flight?.id || null;
  
  if (flight) {
    form.value = { 
      flight_number: flight.flight_number,
      airline: flight.airline, 
      aircraft: flight.aircraft, 
      route: flight.route,
      total_stops: flight.total_stops
    };
  } else {
    form.value = { flight_number: '', airline: '', aircraft: '', route: '', total_stops: 0, is_active: true };
  }
  isModalOpen.value = true;
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
