<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] font-medium flex items-center gap-2">
        <i class="ph ph-package"></i> New Add-On
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="item in addOns" :key="item.id" class="bg-white border border-gray-200 p-5 rounded-[1px] shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-[#002D1E] text-lg">{{ item.name }}</h3>
            <div class="space-x-2">
              <button @click="openModal(item)" class="text-blue-500 hover:text-blue-700"><i class="ph ph-pencil-simple"></i></button>
              <button @click="deleteAddOn(item.id)" class="text-red-500 hover:text-red-700"><i class="ph ph-trash"></i></button>
            </div>
          </div>
          <p class="text-gray-500 text-sm line-clamp-3">{{ item.description || 'No description provided.' }}</p>
        </div>
      </div>
      <div v-if="addOns.length === 0" class="col-span-full py-12 text-center text-gray-400">
        No add-ons created yet.
      </div>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl">
        <h2 class="text-lg font-bold mb-4 text-[#002D1E]">{{ isEditing ? 'Edit Service' : 'Create New Service' }}</h2>
        <form @submit.prevent="saveAddOn" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Service Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 rounded-[1px]" placeholder="e.g. 20kg Extra Baggage" required>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Description</label>
            <textarea v-model="form.description" class="w-full border p-2 rounded-[1px] h-24" placeholder="Briefly describe what is included..."></textarea>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button type="button" @click="isModalOpen = false" class="px-4 py-2 text-gray-600">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px]">Save Service</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/admin/api';

const addOns = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ name: '', description: '' });

const fetchAddOns = async () => {
  const res = await api.get('/add-ons/');
  addOns.value = res.data;
};

const saveAddOn = async () => {
  try {
    if (isEditing.value) await api.put(`/add-ons/${currentId.value}/`, form.value);
    else await api.post('/add-ons/', form.value);
    fetchAddOns();
    isModalOpen.value = false;
  } catch (err) { alert("Error saving Add-On."); }
};

const deleteAddOn = async (id) => {
  if (confirm('Delete this service type?')) {
    await api.delete(`/add-ons/${id}/`);
    fetchAddOns();
  }
};

const openModal = (item = null) => {
  isEditing.value = !!item;
  currentId.value = item?.id || null;
  form.value = item ? { ...item } : { name: '', description: '' };
  isModalOpen.value = true;
};

onMounted(fetchAddOns);
</script>