<template>
  <div class="p-6 poppins">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all">
        <i class="ph ph-plus"></i> Add Country
      </button>
    </div>

    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Country</th>
            <th class="px-6 py-4 poppins">Code</th>
            <th class="px-6 py-4 poppins">Currency</th>
            <th class="px-6 py-4 poppins text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="c in countries" :key="c.id" class="hover:bg-gray-50/50 transition-all text-[12px] font-medium">
            <td class="px-6 py-4 font-bold text-[#002D1E]">{{ c.name }}</td>
            <td class="px-6 py-4"><span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-[1px] text-[10px] font-black uppercase">{{ c.code || '—' }}</span></td>
            <td class="px-6 py-4 text-gray-500">{{ c.currency || '—' }}</td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(c)" class="text-green-600 hover:text-green-400 p-2 transition-colors"><i class="ph ph-pencil-simple text-lg"></i></button>
                <button @click="deleteItem(c.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors"><i class="ph ph-trash text-lg"></i></button>
              </div>
            </td>
          </tr>
          <tr v-if="countries.length === 0"><td colspan="4" class="px-6 py-10 text-center text-gray-400 italic poppins">No countries found.</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Country' : 'New Country' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors"><i class="ph ph-x text-xl"></i></button>
        </div>
        <form @submit.prevent="saveItem" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Country Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Country Code</label>
              <input v-model="form.code" type="text" maxlength="5" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. PH">
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Currency</label>
              <input v-model="form.currency" type="text" maxlength="10" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. PHP">
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-4 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
const modalStore = useModalStore();
const countries = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ name: '', code: '', currency: '' });

const fetchData = async () => {
  const res = await api.get('/countries/');
  countries.value = res.data.results || res.data;
};
const saveItem = async () => {
  if (isEditing.value) await api.put(`/countries/${currentId.value}/`, form.value);
  else await api.post('/countries/', form.value);
  await fetchData(); isModalOpen.value = false;
};
const deleteItem = async (id) => {
  const ok = await modalStore.confirm({ title: 'Delete Country?', message: 'This cannot be undone.', variant: 'danger', confirmText: 'Delete', loadingText: 'Deleting...' });
  if (ok) { modalStore.setLoader(true); await api.delete(`/countries/${id}/`); await fetchData(); modalStore.close(true); }
};
const openModal = (item = null) => {
  isEditing.value = !!item; currentId.value = item?.id || null;
  form.value = item ? { name: item.name, code: item.code, currency: item.currency } : { name: '', code: '', currency: '' };
  isModalOpen.value = true;
};
onMounted(fetchData);
</script>
<style scoped>.poppins { font-family: 'Poppins', sans-serif; }</style>
