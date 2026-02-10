<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] font-medium flex items-center gap-2">
        <i class="ph ph-plus-circle"></i> Add Class
      </button>
    </div>

    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 text-sm">
          <tr>
            <th class="px-6 py-4 font-semibold uppercase">Name</th>
            <th class="px-6 py-4 font-semibold uppercase">Airline</th>
            <th class="px-6 py-4 font-semibold uppercase">Multiplier</th>
            <th class="px-6 py-4 font-semibold uppercase text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="sc in seatClasses" :key="sc.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 font-bold text-[#002D1E]">{{ sc.name }}</td>
            <td class="px-6 py-4">{{ sc.airline_name || 'Global' }}</td>
            <td class="px-6 py-4 text-blue-600 font-mono">x{{ sc.price_multiplier }}</td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openModal(sc)" class="text-blue-600"><i class="ph ph-pencil-simple text-lg"></i></button>
              <button @click="deleteSeatClass(sc.id)" class="text-red-600"><i class="ph ph-trash text-lg"></i></button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl">
        <h2 class="text-lg font-bold mb-4 text-[#002D1E]">{{ isEditing ? 'Edit Seat Class' : 'New Seat Class' }}</h2>
        <form @submit.prevent="saveSeatClass" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Airline</label>
            <select v-model="form.airline" class="w-full border p-2 rounded-[1px] bg-white" required>
              <option value="" disabled>Select Airline</option>
              <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Class Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 rounded-[1px]" placeholder="e.g. Business Class" required>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Price Multiplier</label>
            <input v-model="form.price_multiplier" type="number" step="0.01" class="w-full border p-2 rounded-[1px]" required>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button type="button" @click="isModalOpen = false" class="px-4 py-2 text-gray-600">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px]">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/admin/api';

const seatClasses = ref([]);
const airlines = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ airline: '', name: '', price_multiplier: 1.00 });

const fetchData = async () => {
  const [scRes, aRes] = await Promise.all([
    api.get('/seat-classes/'),
    api.get('/airlines/')
  ]);
  seatClasses.value = scRes.data;
  airlines.value = aRes.data;
};

const saveSeatClass = async () => {
  try {
    if (isEditing.value) await api.put(`/seat-classes/${currentId.value}/`, form.value);
    else await api.post('/seat-classes/', form.value);
    fetchData();
    isModalOpen.value = false;
  } catch (err) { alert("Error: " + JSON.stringify(err.response.data)); }
};

const deleteSeatClass = async (id) => {
  if (confirm('Delete?')) {
    await api.delete(`/seat-classes/${id}/`);
    fetchData();
  }
};

const openModal = (sc = null) => {
  isEditing.value = !!sc;
  currentId.value = sc?.id || null;
  form.value = sc ? { airline: sc.airline, name: sc.name, price_multiplier: sc.price_multiplier } : { airline: '', name: '', price_multiplier: 1.00 };
  isModalOpen.value = true;
};

onMounted(fetchData);
</script>