<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] font-medium flex items-center gap-2 hover:bg-[#e02d74] transition-colors">
        <i class="ph ph-plus-circle"></i> Add Airport
      </button>
    </div>

    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 text-sm">
          <tr>
            <th class="px-6 py-4 font-semibold uppercase">Code</th>
            <th class="px-6 py-4 font-semibold uppercase">Airport</th>
            <th class="px-6 py-4 font-semibold uppercase">City/Country</th>
            <th class="px-6 py-4 font-semibold uppercase">Type</th>
            <th class="px-6 py-4 font-semibold uppercase text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="airport in airports" :key="airport.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 font-bold text-[#fe3787]">{{ airport.code }}</td>
            <td class="px-6 py-4">
              <div class="font-medium text-[#002D1E]">{{ airport.name }}</div>
              <div class="text-xs text-gray-400">{{ airport.location }}</div>
            </td>
            <td class="px-6 py-4">{{ airport.city }}, {{ airport.country_name || 'N/A' }}</td>
            <td class="px-6 py-4">
              <span :class="airport.airport_type === 'international' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'" 
                    class="px-2 py-1 rounded-full text-[10px] font-bold uppercase">
                {{ airport.airport_type }}
              </span>
            </td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openModal(airport)" class="text-blue-600 hover:text-blue-800">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="deleteAirport(airport.id)" class="text-red-600 hover:text-red-800">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </td>
          </tr>
          <tr v-if="airports.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic">No airports found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <h2 class="text-lg font-bold mb-4 text-[#002D1E]">{{ isEditing ? 'Edit Airport' : 'Add Airport' }}</h2>
        
        <form @submit.prevent="saveAirport" class="grid grid-cols-2 gap-4">
          <div class="col-span-2">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Airport Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 rounded-[1px] focus:outline-none focus:border-[#fe3787]" required>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">IATA Code</label>
            <input v-model="form.code" type="text" class="w-full border p-2 rounded-[1px] focus:outline-none focus:border-[#fe3787]" placeholder="MNL" maxlength="3" required>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Type</label>
            <select v-model="form.airport_type" class="w-full border p-2 rounded-[1px] bg-white focus:outline-none focus:border-[#fe3787]">
              <option value="domestic">Domestic</option>
              <option value="international">International</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">City</label>
            <input v-model="form.city" type="text" class="w-full border p-2 rounded-[1px] focus:outline-none focus:border-[#fe3787]">
          </div>

          <div class="col-span-2">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Detailed Location</label>
            <input v-model="form.location" type="text" class="w-full border p-2 rounded-[1px] focus:outline-none focus:border-[#fe3787]" placeholder="NAIA Terminal 3, Pasay City">
          </div>
          
          <div class="flex justify-end col-span-2 gap-2 mt-4">
            <button type="button" @click="isModalOpen = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 transition-colors">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px] hover:bg-[#e02d74] transition-all">
              {{ isEditing ? 'Update Airport' : 'Save Airport' }}
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

// State
const airports = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);

const form = ref({
  name: '',
  code: '',
  city: '',
  location: '',
  airport_type: 'domestic'
});

// Fetch Data
const fetchAirports = async () => {
  try {
    const res = await api.get('/airports/');
    airports.value = res.data;
  } catch (err) {
    console.error("Fetch Error:", err.response?.data || err.message);
  }
};

// Save (Create or Update)
const saveAirport = async () => {
  try {
    if (isEditing.value) {
      // PUT request to /api/airports/{id}/
      await api.put(`/airports/${currentId.value}/`, form.value);
    } else {
      // POST request to /api/airports/
      await api.post('/airports/', form.value);
    }
    await fetchAirports(); // Refresh list
    isModalOpen.value = false;
  } catch (err) {
    console.error("Save error:", err.response?.data);
    alert("Save failed. Please check the data format.");
  }
};

// Delete
const deleteAirport = async (id) => {
  if (confirm('Are you sure you want to delete this airport? This may affect existing routes.')) {
    try {
      // DELETE request to /api/airports/{id}/
      await api.delete(`/airports/${id}/`);
      // Update local state for immediate UI feedback
      airports.value = airports.value.filter(a => a.id !== id);
    } catch (err) {
      console.error("Delete error:", err.response?.data);
      alert("Delete failed. This airport might be in use.");
    }
  }
};

// UI Logic
const openModal = (airport = null) => {
  if (airport) {
    isEditing.value = true;
    currentId.value = airport.id;
    // Clone airport object to form
    form.value = { 
      name: airport.name, 
      code: airport.code, 
      city: airport.city, 
      location: airport.location, 
      airport_type: airport.airport_type 
    };
  } else {
    isEditing.value = false;
    currentId.value = null;
    form.value = { name: '', code: '', city: '', location: '', airport_type: 'domestic' };
  }
  isModalOpen.value = true;
};

onMounted(fetchAirports);
</script>