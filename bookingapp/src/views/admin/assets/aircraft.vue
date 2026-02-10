<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] font-medium flex items-center gap-2">
        <i class="ph ph-plus-circle"></i> Add Aircraft
      </button>
    </div>

    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 text-sm">
          <tr>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider">Model</th>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider">Airline</th>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider text-center">Capacity</th>
            <th class="px-6 py-4 font-semibold uppercase tracking-wider text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="plane in aircraftList" :key="plane.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 font-bold text-[#002D1E]">{{ plane.model }}</td>
            <td class="px-6 py-4">
               <span class="bg-gray-100 px-2 py-1 rounded text-xs font-medium">{{ plane.airline_name || 'Unassigned' }}</span>
            </td>
            <td class="px-6 py-4 text-center">{{ plane.capacity }} seats</td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openModal(plane)" class="text-blue-600"><i class="ph ph-pencil-simple text-lg"></i></button>
              <button @click="deleteAircraft(plane.id)" class="text-red-600"><i class="ph ph-trash text-lg"></i></button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl">
        <h2 class="text-lg font-bold mb-4 text-[#002D1E]">{{ isEditing ? 'Edit Aircraft' : 'Register New Aircraft' }}</h2>
        <form @submit.prevent="saveAircraft" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Airline Owner</label>
            <select v-model="form.airline" class="w-full border p-2 rounded-[1px] bg-white" required>
              <option value="" disabled>Select Airline</option>
              <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }} ({{ a.code }})</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Aircraft Model</label>
            <input v-model="form.model" type="text" class="w-full border p-2 rounded-[1px]" placeholder="e.g. Airbus A321neo" required>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Total Seat Capacity</label>
            <input v-model="form.capacity" type="number" class="w-full border p-2 rounded-[1px]" required>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button type="button" @click="isModalOpen = false" class="px-4 py-2 text-gray-600">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px]">Save Aircraft</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/admin/api';

const aircraftList = ref([]);
const airlines = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ model: '', capacity: 0, airline: '' });

const fetchData = async () => {
  try {
    const [planeRes, airlineRes] = await Promise.all([
      api.get('/aircraft/'),
      api.get('/airlines/')
    ]);
    aircraftList.value = planeRes.data;
    airlines.value = airlineRes.data;
  } catch (err) { console.error(err); }
};

const saveAircraft = async () => {
  try {
    if (isEditing.value) await api.put(`/aircraft/${currentId.value}/`, form.value);
    else await api.post('/aircraft/', form.value);
    fetchData();
    isModalOpen.value = false;
  } catch (err) { alert("Error saving aircraft."); }
};

const deleteAircraft = async (id) => {
  if (confirm('Remove this aircraft from fleet?')) {
    await api.delete(`/aircraft/${id}/`);
    fetchData();
  }
};

const openModal = (plane = null) => {
  isEditing.value = !!plane;
  currentId.value = plane?.id || null;
  form.value = plane ? { model: plane.model, capacity: plane.capacity, airline: plane.airline } : { model: '', capacity: 0, airline: '' };
  isModalOpen.value = true;
};

onMounted(fetchData);
</script>