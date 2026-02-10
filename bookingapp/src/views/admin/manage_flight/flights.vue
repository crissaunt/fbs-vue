<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#e02d74] transition-colors shadow-sm">
        <i class="ph ph-plus"></i> Create Flight
      </button>
    </div>

    <div class="bg-white border border-gray-200 shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-sm border-b uppercase font-semibold">
          <tr>
            <th class="px-6 py-4">Flight #</th>
            <th class="px-6 py-4">Airline</th>
            <th class="px-6 py-4">Aircraft</th>
            <th class="px-6 py-4">Route</th>
            <th class="px-6 py-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="f in flights" :key="f.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 font-bold text-[#fe3787]">{{ f.flight_number }}</td>
            <td class="px-6 py-4">{{ f.airline_display || 'N/A' }}</td>
            <td class="px-6 py-4">{{ f.aircraft_display || 'N/A' }}</td>
            <td class="px-6 py-4 text-xs font-medium">{{ f.route_display || 'No Route' }}</td>
            <td class="px-6 py-4 text-right space-x-2">
              <button @click="openModal(f)" class="text-blue-600 hover:bg-blue-50 p-2 rounded"><i class="ph ph-pencil text-lg"></i></button>
              <button @click="deleteFlight(f.id)" class="text-red-600 hover:bg-red-50 p-2 rounded"><i class="ph ph-trash text-lg"></i></button>
            </td>
          </tr>
          <tr v-if="flights.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic">No flights found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 shadow-2xl">
        <h2 class="font-bold text-lg mb-4 text-[#002D1E]">{{ isEditing ? 'Edit Flight' : 'New Flight' }}</h2>
        
        <form @submit.prevent="saveFlight" class="space-y-4">
          <div>
            <label class="block text-xs font-bold mb-1 uppercase text-gray-500">Flight Number</label>
            <input v-model="form.flight_number" type="text" class="w-full border p-2 outline-none focus:border-[#fe3787]" placeholder="e.g. PR101" required>
          </div>

          <div>
            <label class="block text-xs font-bold mb-1 uppercase text-gray-500">Airline</label>
            <select v-model="form.airline" class="w-full border p-2 bg-white outline-none focus:border-[#fe3787]" required>
              <option value="" disabled>Select Airline</option>
              <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold mb-1 uppercase text-gray-500">Aircraft</label>
            <select v-model="form.aircraft" class="w-full border p-2 bg-white outline-none focus:border-[#fe3787]" required :disabled="!form.airline">
              <option value="" disabled>{{ form.airline ? 'Select Aircraft' : 'Select Airline First' }}</option>
              <option v-for="ac in filteredAircrafts" :key="ac.id" :value="ac.id">
                {{ ac.model }} ({{ ac.capacity }} seats)
              </option>
            </select>
            <p v-if="form.airline && filteredAircrafts.length === 0" class="text-[10px] text-red-500 mt-1">
              No aircraft assigned to this airline.
            </p>
          </div>

          <div>
            <label class="block text-xs font-bold mb-1 uppercase text-gray-500">Route</label>
            <select v-model="form.route" class="w-full border p-2 bg-white outline-none focus:border-[#fe3787]" required>
              <option value="" disabled>Select Route</option>
              <option v-for="r in routes" :key="r.id" :value="r.id">
                {{ r.origin_info }} → {{ r.destination_info }}
              </option>
            </select>
          </div>

          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="isModalOpen = false" class="px-4 py-2 text-gray-500 hover:bg-gray-100 transition-colors">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 font-bold hover:bg-[#e02d74] transition-all">
              {{ isEditing ? 'Update' : 'Create' }} Flight
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '@/services/admin/api';

const flights = ref([]);
const airlines = ref([]);
const allAircrafts = ref([]);
const filteredAircrafts = ref([]);
const routes = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);

const form = ref({
  flight_number: '',
  airline: '',
  aircraft: '',
  route: ''
});

const fetchData = async () => {
  try {
    const [resF, resA, resAc, resR] = await Promise.all([
      api.get('/flights/'),
      api.get('/airlines/'),
      api.get('/aircraft/'),
      api.get('/routes/')
    ]);

    // Handle pagination (results) or flat lists
    flights.value = resF.data.results || resF.data;
    airlines.value = resA.data.results || resA.data;
    allAircrafts.value = resAc.data.results || resAc.data;
    routes.value = resR.data.results || resR.data;
    
    console.log("Aircrafts Data:", allAircrafts.value);
  } catch (err) {
    console.error("Data fetch failed:", err.response?.data || err.message);
  }
};

// Logic: Filter aircrafts whenever the airline selection changes
watch(() => form.value.airline, (newAirlineId) => {
  if (newAirlineId) {
    // IMPORTANT: Check if your Aircraft model has the 'airline' field as an ID
    filteredAircrafts.value = allAircrafts.value.filter(
      ac => ac.airline === newAirlineId
    );
    // Reset aircraft selection if the current one isn't in the new list
    if (!filteredAircrafts.value.find(ac => ac.id === form.value.aircraft)) {
      form.value.aircraft = '';
    }
  } else {
    filteredAircrafts.value = [];
  }
});

const saveFlight = async () => {
  try {
    form.value.flight_number = form.value.flight_number.toUpperCase().trim();

    if (isEditing.value) {
      await api.put(`/flights/${currentId.value}/`, form.value);
    } else {
      await api.post('/flights/', form.value);
    }
    
    await fetchData();
    isModalOpen.value = false;
  } catch (err) {
    console.error("Save error:", err.response?.data);
    alert("Error: " + JSON.stringify(err.response?.data || "Save failed"));
  }
};

const deleteFlight = async (id) => {
  if (confirm('Delete this flight?')) {
    try {
      await api.delete(`/flights/${id}/`);
      fetchData();
    } catch (err) {
      alert("Delete failed.");
    }
  }
};

const openModal = (flight = null) => {
  isEditing.value = !!flight;
  currentId.value = flight?.id || null;
  
  if (flight) {
    form.value = { 
      flight_number: flight.flight_number,
      airline: flight.airline, // Ensure serializer sends the ID
      aircraft: flight.aircraft, // Ensure serializer sends the ID
      route: flight.route // Ensure serializer sends the ID
    };
  } else {
    form.value = { flight_number: '', airline: '', aircraft: '', route: '' };
  }
  isModalOpen.value = true;
};

onMounted(fetchData);
</script>