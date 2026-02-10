<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] font-medium flex items-center gap-2">
        <i class="ph ph-plus-circle"></i> Add Airline
      </button>
    </div>

    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 text-sm">
          <tr>
            <th class="px-6 py-4 font-semibold uppercase">Code</th>
            <th class="px-6 py-4 font-semibold uppercase">Airline Name</th>
            <th class="px-6 py-4 font-semibold uppercase text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="airline in airlines" :key="airline.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 font-bold text-[#fe3787]">{{ airline.code }}</td>
            <td class="px-6 py-4 font-medium text-[#002D1E]">{{ airline.name }}</td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openModal(airline)" class="text-blue-600 hover:text-blue-800"><i class="ph ph-pencil-simple text-lg"></i></button>
              <button @click="deleteAirline(airline.id)" class="text-red-600 hover:text-red-800"><i class="ph ph-trash text-lg"></i></button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl">
        <h2 class="text-lg font-bold mb-4 text-[#002D1E]">{{ isEditing ? 'Edit Airline' : 'Add Airline' }}</h2>
        <form @submit.prevent="saveAirline" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Airline Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 rounded-[1px]" placeholder="e.g. Philippine Airlines" required>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">IATA Code</label>
            <input v-model="form.code" type="text" class="w-full border p-2 rounded-[1px]" placeholder="e.g. PR" required>
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

const airlines = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ name: '', code: '' });

const fetchAirlines = async () => {
  const res = await api.get('/airlines/');
  airlines.value = res.data;
};

const saveAirline = async () => {
  try {
    if (isEditing.value) await api.put(`/airlines/${currentId.value}/`, form.value);
    else await api.post('/airlines/', form.value);
    fetchAirlines();
    isModalOpen.value = false;
  } catch (err) { alert("Error: " + JSON.stringify(err.response.data)); }
};

const deleteAirline = async (id) => {
  if (confirm('Delete airline?')) {
    await api.delete(`/airlines/${id}/`);
    fetchAirlines();
  }
};

const openModal = (airline = null) => {
  isEditing.value = !!airline;
  currentId.value = airline?.id || null;
  form.value = airline ? { ...airline } : { name: '', code: '' };
  isModalOpen.value = true;
};

onMounted(fetchAirlines);
</script>