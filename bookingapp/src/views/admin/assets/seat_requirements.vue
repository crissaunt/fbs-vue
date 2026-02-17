<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-[#002D1E]">Seat Requirements</h1>
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] font-medium flex items-center gap-2">
        <i class="ph ph-plus-circle"></i> Add Requirement
      </button>
    </div>

    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 text-sm">
          <tr>
            <th class="px-6 py-4 font-semibold uppercase">Icon</th>
            <th class="px-6 py-4 font-semibold uppercase">Name</th>
            <th class="px-6 py-4 font-semibold uppercase">Code</th>
            <th class="px-6 py-4 font-semibold uppercase text-right">Price</th>
            <th class="px-6 py-4 font-semibold uppercase text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="req in requirements" :key="req.id" class="hover:bg-gray-50">
            <td class="px-6 py-4">
              <div class="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                <i :class="[req.icon || 'ph ph-star', 'text-gray-600 text-lg']"></i>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="font-bold text-[#002D1E]">{{ req.name }}</div>
              <div class="text-xs text-gray-500 truncate max-w-[200px]">{{ req.description }}</div>
            </td>
            <td class="px-6 py-4 font-mono text-xs text-gray-500">{{ req.code }}</td>
            <td class="px-6 py-4 text-right font-bold text-[#fe3787]">₱{{ formatPrice(req.price) }}</td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openModal(req)" class="text-blue-600 hover:text-blue-800"><i class="ph ph-pencil-simple text-lg"></i></button>
              <button @click="deleteRequirement(req.id)" class="text-red-600 hover:text-red-800"><i class="ph ph-trash text-lg"></i></button>
            </td>
          </tr>
          <tr v-if="requirements.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-500">
              No seat requirements found. Add one to get started!
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E]">{{ isEditing ? 'Edit Requirement' : 'Add Requirement' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-gray-600">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="saveRequirement" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Name</label>
              <input v-model="form.name" type="text" class="w-full border p-2 rounded-[1px] outline-none focus:border-[#fe3787]" placeholder="e.g. Extra Legroom" required>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Code</label>
              <input v-model="form.code" type="text" class="w-full border p-2 rounded-[1px] outline-none focus:border-[#fe3787]" placeholder="e.g. has_extra_legroom" required>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Price (₱)</label>
              <input v-model.number="form.price" type="number" step="0.01" class="w-full border p-2 rounded-[1px] outline-none focus:border-[#fe3787]" required>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Icon (Phospor Class)</label>
              <div class="flex gap-2">
                <input v-model="form.icon" type="text" class="flex-1 border p-2 rounded-[1px] outline-none focus:border-[#fe3787]" placeholder="ph ph-stars">
                <div class="w-10 h-10 bg-gray-50 border flex items-center justify-center">
                  <i :class="[form.icon || 'ph ph-star', 'text-[#fe3787]']"></i>
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Description</label>
            <textarea v-model="form.description" class="w-full border p-2 rounded-[1px] h-24 outline-none focus:border-[#fe3787]" placeholder="Describe this requirement..."></textarea>
          </div>

          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="isModalOpen = false" class="px-6 py-2 text-gray-600 font-medium hover:bg-gray-50">Cancel</button>
            <button type="submit" class="px-6 py-2 bg-[#fe3787] text-white font-bold rounded-[1px] hover:bg-[#e62e7a]">
              {{ isEditing ? 'Update Requirement' : 'Save Requirement' }}
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

const requirements = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({
  name: '',
  code: '',
  price: 0,
  icon: 'ph ph-star',
  description: ''
});

const fetchRequirements = async () => {
  try {
    const res = await api.get('/seat-requirements/');
    requirements.value = res.data.results || res.data || [];
  } catch (err) {
    console.error('Failed to fetch requirements:', err);
  }
};

const saveRequirement = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/seat-requirements/${currentId.value}/`, form.value);
    } else {
      await api.post('/seat-requirements/', form.value);
    }
    fetchRequirements();
    isModalOpen.value = false;
  } catch (err) {
    alert("Error saving: " + JSON.stringify(err.response?.data || err.message));
  }
};

const deleteRequirement = async (id) => {
  if (confirm('Are you sure you want to delete this seat requirement? This might affect existing seat configurations.')) {
    try {
      await api.delete(`/seat-requirements/${id}/`);
      fetchRequirements();
    } catch (err) {
      alert("Error deleting: " + JSON.stringify(err.response?.data || err.message));
    }
  }
};

const openModal = (req = null) => {
  isEditing.value = !!req;
  currentId.value = req?.id || null;
  form.value = req ? { ...req } : {
    name: '',
    code: '',
    price: 0,
    icon: 'ph ph-star',
    description: ''
  };
  isModalOpen.value = true;
};

const formatPrice = (price) => {
  return parseFloat(price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

onMounted(fetchRequirements);
</script>
