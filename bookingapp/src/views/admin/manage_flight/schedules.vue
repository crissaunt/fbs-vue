<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#e02d74] transition-all shadow-sm">
        <i class="ph ph-plus-bold"></i> Add Schedule
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div v-for="(count, label) in stats" :key="label" class="bg-white p-4 border border-gray-100 shadow-sm rounded-sm">
        <p class="text-[10px] uppercase font-bold text-gray-400 tracking-widest">{{ label }}</p>
        <p class="text-2xl font-bold text-[#002D1E]">{{ count }}</p>
      </div>
    </div>

    <div class="bg-white border border-gray-200 shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-500 text-[11px] uppercase font-bold border-b">
          <tr>
            <th class="px-6 py-4">Flight</th>
            <th class="px-6 py-4">Departure / Arrival</th>
            <th class="px-6 py-4">Duration</th>
            <th class="px-6 py-4">Status</th>
            <th class="px-6 py-4">Price</th>
            <th class="px-6 py-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 text-sm">
          <tr v-for="s in schedules" :key="s.id" class="hover:bg-gray-50/50 transition-colors">
            <td class="px-6 py-4">
              <span class="font-bold text-[#fe3787] block">{{ s.flight_number }}</span>
              <span class="text-[10px] text-gray-400 uppercase">#{{ s.id }}</span>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <span class="font-medium">{{ formatTime(s.departure_time) }}</span>
                <i class="ph ph-caret-right text-gray-300"></i>
                <span class="font-medium">{{ formatTime(s.arrival_time) }}</span>
              </div>
              <div class="text-[10px] text-gray-400 mt-0.5">{{ formatDate(s.departure_time) }}</div>
            </td>
            <td class="px-6 py-4 text-gray-500 font-medium">{{ s.duration_display }}</td>
            <td class="px-6 py-4">
              <span :class="statusClass(s.status)" class="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter">
                {{ s.status }}
              </span>
            </td>
            <td class="px-6 py-4 font-bold">₱{{ parseFloat(s.price).toLocaleString() }}</td>
            <td class="px-6 py-4 text-right">
              <button @click="deleteSchedule(s.id)" class="text-gray-400 hover:text-red-500 p-2"><i class="ph ph-trash text-lg"></i></button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-6">
          <h2 class="font-bold text-lg">New Flight Schedule</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black"><i class="ph ph-x text-xl"></i></button>
        </div>

        <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-xs leading-relaxed">
          <div class="flex gap-2">
            <i class="ph ph-warning-circle-bold text-lg"></i>
            <span>{{ errorMessage }}</span>
          </div>
        </div>

        <form @submit.prevent="saveSchedule" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Select Flight</label>
            <select v-model="form.flight" class="w-full border p-2 text-sm bg-white focus:border-[#fe3787] outline-none" required>
              <option :value="null" disabled>Choose a flight number...</option>
              <option v-for="f in flightList" :key="f.id" :value="f.id">{{ f.flight_number }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Departure</label>
              <input v-model="form.departure_time" type="datetime-local" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787]" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Arrival</label>
              <input v-model="form.arrival_time" type="datetime-local" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787]" required>
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Base Price (PHP)</label>
            <input v-model="form.price" type="number" step="0.01" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787]" placeholder="0.00">
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium">Cancel</button>
            <button type="submit" :disabled="loading" class="bg-[#002D1E] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-black transition-all">
              {{ loading ? 'Checking Conflicts...' : 'Confirm Schedule' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/admin/api';

const schedules = ref([]);
const flightList = ref([]);
const isModalOpen = ref(false);
const loading = ref(false);
const errorMessage = ref(null);

const form = ref({
  flight: '',
  departure_time: '',
  arrival_time: '',
  price: 0
});

// Computed Stats
const stats = computed(() => {
  return {
    'Total Flights': schedules.value.length,
    'Open for Booking': schedules.value.filter(s => s.status === 'Open').length,
    'Currently In-Air': schedules.value.filter(s => s.status === 'On Flight').length,
    'Completed': schedules.value.filter(s => s.status === 'Arrived').length,
  };
});

const fetchData = async () => {
  try {
    const [resS, resF] = await Promise.all([
      api.get('/schedules/'),
      api.get('/flights/')
    ]);
    schedules.value = resS.data.results || resS.data;
    flightList.value = resF.data.results || resF.data;
  } catch (err) {
    console.error("Fetch failed", err);
  }
};

const saveSchedule = async () => {
  loading.value = true;
  errorMessage.value = null;
  
  // Validate that flight is selected
  if (!form.value.flight) {
    errorMessage.value = "Please select a flight.";
    loading.value = false;
    return;
  }
  
  // Convert flight to integer and ensure proper data types
  const payload = {
    flight: parseInt(form.value.flight),  // Convert string to integer
    departure_time: form.value.departure_time,
    arrival_time: form.value.arrival_time,
    price: parseFloat(form.value.price) || 0  // Ensure price is a number
  };
  
  console.log('Sending payload:', payload);  // Debug log
  
  try {
    await api.post('/schedules/', payload);
    await fetchData();
    isModalOpen.value = false;
  } catch (err) {
    console.error('Full error:', err);
    console.error('Error response:', err.response);
    
    if (err.response && err.response.data) {
      const data = err.response.data;
      console.error('Error data:', data);
      
      // Better error handling
      if (data.flight) {
        errorMessage.value = `Flight: ${data.flight.join(', ')}`;
      } else if (data.non_field_errors) {
        errorMessage.value = data.non_field_errors.join(', ');
      } else if (data.detail) {
        errorMessage.value = data.detail;
      } else {
        errorMessage.value = Object.entries(data)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
          .join('; ');
      }
    } else {
      errorMessage.value = "Unable to save schedule. Please check your connection.";
    }
  } finally {
    loading.value = false;
  }
};

const openModal = () => {
  form.value = { 
    flight: null,  // Use null instead of empty string
    departure_time: '', 
    arrival_time: '', 
    price: 0 
  };
  errorMessage.value = null;
  isModalOpen.value = true;
};

const deleteSchedule = async (id) => {
  if (confirm('Permanently remove this schedule?')) {
    await api.delete(`/schedules/${id}/`);
    fetchData();
  }
};

// Helpers
const formatTime = (d) => new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
const formatDate = (d) => new Date(d).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
const statusClass = (s) => {
  if (s === 'Open') return 'bg-green-100 text-green-700';
  if (s === 'Closed') return 'bg-orange-100 text-orange-700';
  if (s === 'On Flight') return 'bg-blue-600 text-white';
  return 'bg-gray-100 text-gray-500';
};

onMounted(fetchData);
</script>