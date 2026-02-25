<template>
  <div class="p-6 poppins">
    <div class="mb-6 flex justify-between items-center">
    </div>

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div 
        v-for="(count, label) in statsItems" 
        :key="label" 
        class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins leading-none mb-2">{{ label }}</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ count }}</p>
          </div>
          <div :class="statIconClass(label)" class="w-12 h-12 rounded-full flex items-center justify-center">
            <i :class="[statIcon(label), 'text-xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Booking ID</th>
            <th class="px-6 py-4 poppins">User</th>
            <th class="px-6 py-4 poppins">Trip Type</th>
            <th class="px-6 py-4 poppins text-right">Total Amount</th>
            <th class="px-6 py-4 poppins text-center">Status</th>
            <th class="px-6 py-4 poppins text-right">Created</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="booking in bookings"
            :key="booking.id"
            class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium"
          >
            <td class="px-6 py-4 font-bold text-[#fe3787] poppins">
              #{{ booking.id }}
            </td>

            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                  <i class="ph ph-user text-blue-600"></i>
                </div>
                <div class="font-bold text-[#002D1E] poppins">
                  {{ booking.user_name || '—' }}
                </div>
              </div>
            </td>

            <td class="px-6 py-4">
               <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins tracking-tight">
                 {{ booking.trip_type.replace('_', ' ') }}
               </span>
            </td>

            <td class="px-6 py-4 text-right">
               <span class="font-bold text-[#002D1E] poppins">₱{{ parseFloat(booking.total_amount).toLocaleString() }}</span>
            </td>

            <td class="px-6 py-4 text-center">
              <span
                class="px-3 py-1 text-[10px] font-bold uppercase rounded-full poppins"
                :class="statusBadge(booking.status)"
              >
                {{ booking.status }}
              </span>
            </td>

            <td class="px-6 py-4 text-right text-gray-400 poppins">
              {{ formatDate(booking.created_at) }}
            </td>
          </tr>

          <tr v-if="bookings.length === 0">
            <td colspan="6" class="px-6 py-10 text-center text-gray-400 italic poppins">
              No bookings found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import api from "@/services/admin/api"

const bookings = ref([])

const statsItems = computed(() => {
  return {
    'Total Bookings': bookings.value.length,
    'Confirmed': bookings.value.filter(b => b.status?.toLowerCase() === 'confirmed').length,
    'Pending': bookings.value.filter(b => b.status?.toLowerCase() === 'pending').length,
    'Cancelled': bookings.value.filter(b => b.status?.toLowerCase() === 'cancelled').length,
  };
});

const statIcon = (label) => {
  if (label === 'Total Bookings') return 'ph ph-notebook';
  if (label === 'Confirmed') return 'ph ph-check-circle';
  if (label === 'Pending') return 'ph ph-clock';
  return 'ph ph-x-circle';
};

const statIconClass = (label) => {
  if (label === 'Total Bookings') return 'bg-blue-100 text-blue-600';
  if (label === 'Confirmed') return 'bg-green-100 text-green-600';
  if (label === 'Pending') return 'bg-purple-100 text-purple-600';
  return 'bg-pink-100 text-pink-600';
};

const fetchBookings = async () => {
  try {
    const res = await api.get("/bookings/")
    bookings.value = res.data.results || res.data
  } catch (err) {
    console.error("Fetch failed", err);
  }
}

const formatDate = (date) =>
  new Date(date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })

const statusBadge = (status) => {
  switch (status.toLowerCase()) {
    case "pending":
      return "bg-purple-100 text-purple-700"
    case "confirmed":
      return "bg-green-100 text-green-700"
    case "cancelled":
      return "bg-pink-100 text-pink-700"
    default:
      return "bg-gray-100 text-gray-600"
  }
}

onMounted(fetchBookings)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
