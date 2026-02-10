<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] font-medium flex items-center gap-2 hover:bg-[#e02d74] transition-colors shadow-sm"
      >
        <i class="ph ph-plus-circle"></i>
        Add New Route
      </button>
    </div>

    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 text-sm">
          <tr>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider">Route ID</th>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider">Origin</th>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider">Destination</th>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider">Base Price</th>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="route in routes" :key="route.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 font-medium text-gray-400">#{{ route.id }}</td>
            <td class="px-6 py-4 font-bold text-[#fe3787]">{{ route.origin_info || route.origin_airport }}</td>
            <td class="px-6 py-4 font-bold text-[#fe3787]">{{ route.destination_info || route.destination_airport }}</td>
            <td class="px-6 py-4 font-semibold text-[#002D1E]">₱{{ parseFloat(route.base_price || 0).toLocaleString() }}</td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openModal(route)" class="text-blue-600 hover:text-blue-800 transition-colors">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="deleteRoute(route.id)" class="text-red-600 hover:text-red-800 transition-colors">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </td>
          </tr>
          <tr v-if="routes.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic">No routes found. Please add one.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl">
        <h2 class="text-lg font-bold mb-4 text-[#002D1E]">
          {{ isEditing ? 'Edit Route' : 'Add New Route' }}
        </h2>
        
        <form @submit.prevent="saveRoute" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Origin Airport</label>
            <select v-model="form.origin_airport" class="w-full border p-2 rounded-[1px] focus:outline-none focus:border-[#fe3787] bg-white" required>
              <option value="" disabled>Select Airport</option>
              <option v-for="airport in airports" :key="airport.id" :value="airport.id">
                {{ airport.name }} ({{ airport.code }})
              </option>
            </select>
            <p v-if="airports.length === 0" class="text-xs text-red-500 mt-1">No airports loaded. Check API.</p>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Destination Airport</label>
            <select v-model="form.destination_airport" class="w-full border p-2 rounded-[1px] focus:outline-none focus:border-[#fe3787] bg-white" required>
              <option value="" disabled>Select Airport</option>
              <option v-for="airport in airports" :key="airport.id" :value="airport.id">
                {{ airport.name }} ({{ airport.code }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Base Price (₱)</label>
            <input v-model="form.base_price" type="number" step="0.01" class="w-full border p-2 rounded-[1px] focus:outline-none focus:border-[#fe3787]" placeholder="0.00" required>
          </div>
          
          <div class="flex justify-end gap-2 mt-6">
            <button type="button" @click="isModalOpen = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-[1px]">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px] hover:bg-[#e02d74] transition-colors shadow-sm">
              {{ isEditing ? 'Update Route' : 'Create Route' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/admin/api';

// --- State ---
const routes = ref([]);
const airports = ref([]); 
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);

const form = ref({
  origin_airport: '',
  destination_airport: '',
  base_price: 0
});

// --- Methods ---

const fetchData = async () => {
  try {
    // 1. Ensure trailing slashes are present for Django routers
    // 2. We handle both paginated (res.data.results) and non-paginated (res.data) responses
    const [routeRes, airportRes] = await Promise.all([
      api.get('/routes/'),
      api.get('/airports/')
    ]);

    routes.value = routeRes.data.results || routeRes.data;
    airports.value = airportRes.data.results || airportRes.data;

    console.log("Airports Loaded for Dropdown:", airports.value);
  } catch (error) {
    console.error("Fetch Error:", error.response?.data || error.message);
    // If you get a 404 here, ensure fbs_backend/urls.py includes path('api/', include('flightapp.urls'))
  }
};

const saveRoute = async () => {
  if (form.value.origin_airport === form.value.destination_airport) {
    alert("Error: Origin and Destination cannot be the same airport.");
    return;
  }

  try {
    const payload = {
      origin_airport: form.value.origin_airport,
      destination_airport: form.value.destination_airport,
      base_price: parseFloat(form.value.base_price)
    };

    if (isEditing.value) {
      await api.put(`/routes/${currentId.value}/`, payload);
    } else {
      await api.post('/routes/', payload);
    }
    
    await fetchData(); 
    isModalOpen.value = false;
  } catch (error) {
    console.error("Save failed:", error.response?.data);
    const errorMsg = error.response?.data?.non_field_errors?.[0] || "Check if this route already exists.";
    alert("Error: " + errorMsg);
  }
};

const deleteRoute = async (id) => {
  if (confirm('Delete this route? This will affect schedules linked to it.')) {
    try {
      await api.delete(`/routes/${id}/`);
      routes.value = routes.value.filter(r => r.id !== id);
    } catch (error) {
      console.error("Delete failed:", error);
      alert("Could not delete. Route may be in use by active flights.");
    }
  }
};

const openModal = (route = null) => {
  if (route) {
    isEditing.value = true;
    currentId.value = route.id;
    // We bind the form to the ID so the <select> can match the value
    form.value = { 
      origin_airport: route.origin_airport, 
      destination_airport: route.destination_airport, 
      base_price: route.base_price 
    };
  } else {
    isEditing.value = false;
    currentId.value = null;
    form.value = { origin_airport: '', destination_airport: '', base_price: 0 };
  }
  isModalOpen.value = true;
};

onMounted(fetchData);
</script>

<style scoped>
.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>