<template>
  <div class="p-8 bg-gray-200 min-h-screen poppins">
    <!-- Header -->
    <div class="mb-8 flex justify-between items-center bg-white p-6 rounded-[2px] border border-gray-200 shadow-sm relative overflow-hidden group">
      <div class="absolute inset-y-0 left-0 w-1.5 bg-[#fe3787]"></div>
      <div>
        <h1 class="text-3xl font-black text-[#002D1E] tracking-tight italic uppercase">Booking Registry</h1>
        <p class="text-[10px] text-gray-400 font-bold uppercase tracking-[0.2em] mt-1">Simulation Control Ledger • Real-time Records</p>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="fetchBookings" 
          class="bg-[#002D1E] text-white px-5 py-2.5 rounded-[2px] text-[10px] font-black uppercase tracking-widest hover:bg-black transition-all flex items-center gap-2 shadow-lg shadow-gray-200"
          :disabled="loading"
        >
          <i class="ph ph-arrows-clockwise" :class="{'animate-spin': loading}"></i>
          Sync Registry
        </button>
        <button 
          @click="$router.push('/student/dashboard')" 
          class="bg-white border border-gray-200 text-gray-600 px-5 py-2.5 rounded-[2px] text-[10px] font-black uppercase tracking-widest hover:bg-gray-50 transition-all shadow-sm"
        >
          Exit Ledger
        </button>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div 
        v-for="(count, label) in statsItems" 
        :key="label" 
        class="bg-white p-6 border border-gray-200 rounded-[2px] shadow-sm hover:shadow-md transition-all group"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-widest leading-none mb-3">{{ label }}</p>
            <p class="text-3xl font-black text-[#002D1E] tracking-tighter">{{ count }}</p>
          </div>
          <div :class="statIconClass(label)" class="w-14 h-14 rounded-[2px] flex items-center justify-center shadow-inner group-hover:scale-110 transition-transform">
            <i :class="[statIcon(label), 'text-2xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[2px] shadow-sm overflow-hidden flex flex-col min-h-[500px]">
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-gray-50 text-gray-500 text-[10px] uppercase font-black tracking-[0.15em] border-b border-gray-200">
            <tr>
              <th class="px-8 py-5">Global ID</th>
              <th class="px-8 py-5">PNR Reference</th>
              <th class="px-8 py-5">Manifest User</th>
              <th class="px-8 py-5">Sector Flow</th>
              <th class="px-8 py-5 text-right">Value</th>
              <th class="px-8 py-5 text-center">Status</th>
              <th class="px-8 py-5 text-right">Timestamp</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-gray-100 italic font-medium">
            <tr
              v-for="booking in paginatedBookings"
              :key="booking.id"
              class="hover:bg-gray-50/50 transition-all text-sm group/row"
            >
              <td class="px-8 py-5">
                <span class="font-black text-[#fe3787] font-mono tracking-tighter">#{{ booking.id }}</span>
              </td>

              <td class="px-8 py-5">
                <span class="font-black text-slate-800 font-mono tracking-[0.2em] uppercase">{{ booking.pnr || '——' }}</span>
              </td>

              <td class="px-8 py-5">
                <div class="flex items-center gap-4">
                  <div class="w-10 h-10 rounded-[2px] bg-slate-100 flex items-center justify-center border border-slate-200 group-hover/row:bg-pink-100 transition-colors">
                    <i class="ph ph-user text-slate-400 group-hover/row:text-pink-600 transition-colors"></i>
                  </div>
                  <div class="font-black text-slate-900 uppercase text-xs tracking-tight">
                    {{ booking.user_name || 'System Generated' }}
                  </div>
                </div>
              </td>

              <td class="px-8 py-5">
                 <span class="bg-slate-100 text-slate-500 px-3 py-1 rounded-[2px] text-[9px] font-black uppercase tracking-widest border border-slate-200">
                   {{ booking.trip_type?.replace('_', ' ') || 'Single' }}
                 </span>
              </td>

              <td class="px-8 py-5 text-right">
                 <span class="font-black text-slate-900 font-mono">₱{{ parseFloat(booking.total_amount).toLocaleString() }}</span>
              </td>

              <td class="px-8 py-5 text-center">
                <span
                  class="px-4 py-1.5 text-[9px] font-black uppercase rounded-[2px] border"
                  :class="statusBadge(booking.status)"
                >
                  {{ booking.status }}
                </span>
              </td>

              <td class="px-8 py-5 text-right text-gray-400 font-black text-[10px] uppercase">
                {{ formatDate(booking.created_at) }}
              </td>
            </tr>

            <tr v-if="bookings.length === 0 && !loading">
              <td colspan="7" class="px-8 py-20 text-center">
                <div class="flex flex-col items-center gap-4">
                  <i class="ph ph-scroll text-5xl text-gray-200"></i>
                  <p class="text-gray-400 text-xs font-black uppercase tracking-widest">Registry Empty — No simulation data found</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Section -->
      <div v-if="bookings.length > itemsPerPage" class="mt-auto px-8 py-6 border-t border-gray-100 bg-gray-50/30 flex items-center justify-between">
        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest flex items-center gap-3">
          <span class="w-2 h-2 rounded-full bg-pink-500 animate-pulse"></span>
          Showing entries {{ startIndex + 1 }} to {{ endIndex }} of {{ bookings.length }}
        </div>
        <div class="flex gap-1.5">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            class="px-6 py-2.5 bg-white border border-gray-200 rounded-[2px] text-[10px] font-black uppercase tracking-widest hover:bg-black hover:text-white disabled:opacity-30 disabled:hover:bg-white disabled:hover:text-gray-400 transition-all shadow-sm"
          >
            Previous
          </button>
          <div class="flex gap-1">
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="goToPage(page)"
              :disabled="page === '...'"
              :class="[
                'w-10 h-10 flex items-center justify-center border rounded-[2px] text-[10px] font-black uppercase transition-all shadow-sm',
                page === '...' ? 'bg-white border-gray-200 text-gray-400' : 
                currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787] shadow-lg shadow-pink-100' : 'bg-white border-gray-200 text-slate-900 hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
          </div>
          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages"
            class="px-6 py-2.5 bg-white border border-gray-200 rounded-[2px] text-[10px] font-black uppercase tracking-widest hover:bg-black hover:text-white disabled:opacity-30 disabled:hover:bg-white disabled:hover:text-gray-400 transition-all shadow-sm"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import axios from "axios"
import AuthStorage from "@/utils/authStorage"

const bookings = ref([])
const loading = ref(false)

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 8;

const statsItems = computed(() => {
  return {
    'Total Operations': bookings.value.length,
    'Confirmed Flow': bookings.value.filter(b => b.status?.toLowerCase() === 'confirmed').length,
    'Simulation Pending': bookings.value.filter(b => b.status?.toLowerCase() === 'pending').length,
    'Aborted Sessions': bookings.value.filter(b => b.status?.toLowerCase() === 'cancelled').length,
  };
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(bookings.value.length / itemsPerPage));
const paginatedBookings = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return bookings.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, bookings.value.length));

const visiblePages = computed(() => {
  const pages = [];
  const t = totalPages.value;
  const c = currentPage.value;
  if (t <= 5) {
    for (let i = 1; i <= t; i++) pages.push(i);
  } else {
    if (c <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i);
      pages.push('...', t);
    } else if (c >= t - 2) {
      pages.push(1, '...');
      for (let i = t - 3; i <= t; i++) pages.push(i);
    } else {
      pages.push(1, '...', c - 1, c, c + 1, '...', t);
    }
  }
  return pages;
});

const statIcon = (label) => {
  if (label === 'Total Operations') return 'ph ph-notebook';
  if (label === 'Confirmed Flow') return 'ph ph-check-circle';
  if (label === 'Simulation Pending') return 'ph ph-clock';
  return 'ph ph-warning-circle';
};

const statIconClass = (label) => {
  if (label === 'Total Operations') return 'bg-blue-50 text-blue-600';
  if (label === 'Confirmed Flow') return 'bg-emerald-50 text-emerald-600';
  if (label === 'Simulation Pending') return 'bg-amber-50 text-amber-600';
  return 'bg-rose-50 text-rose-600';
};

const fetchBookings = async () => {
  loading.value = true
  try {
    const res = await axios.get("http://localhost:8000/api/bookings/", {
      headers: AuthStorage.getApiHeaders()
    })
    bookings.value = (res.data.results || res.data).sort((a, b) => b.id - a.id)
  } catch (err) {
    console.error("Fetch failed", err);
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const statusBadge = (status) => {
  if (!status) return 'bg-gray-100 text-gray-500 border-gray-200'
  switch (status.toLowerCase()) {
    case "pending":
      return "bg-amber-50 text-amber-700 border-amber-200"
    case "confirmed":
      return "bg-emerald-50 text-emerald-700 border-emerald-200"
    case "cancelled":
      return "bg-rose-50 text-rose-700 border-rose-200"
    default:
      return "bg-gray-100 text-gray-600 border-gray-200"
  }
}

const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const goToPage = (p) => { if (p !== '...') currentPage.value = p; };

onMounted(fetchBookings)
</script>

<style scoped>
.poppins { font-family: 'Poppins', sans-serif; }
</style>
