<template>
  <div class="p-8 bg-gray-50 min-h-screen poppins">
    <!-- Header -->
    <div class="mb-8 flex justify-between items-center bg-white p-6 rounded-[2px] border border-gray-200 shadow-sm relative overflow-hidden group">
      <div class="absolute inset-y-0 left-0 w-1.5 bg-[#fe3787]"></div>
      <div>
        <h1 class="text-3xl font-black text-[#002D1E] tracking-tight italic uppercase">Check-in Registry</h1>
        <p class="text-[10px] text-gray-400 font-bold uppercase tracking-[0.2em] mt-1">DCS Portal • Core Manifest Logging</p>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="fetchCheckIns" 
          class="bg-[#002D1E] text-white px-5 py-2.5 rounded-[2px] text-[10px] font-black uppercase tracking-widest hover:bg-black transition-all flex items-center gap-2 shadow-lg shadow-gray-200"
          :disabled="loading"
        >
          <i class="ph ph-arrows-clockwise" :class="{'animate-spin': loading}"></i>
          Update Manifest
        </button>
        <button 
          @click="$router.push('/dcs/dashboard')" 
          class="bg-white border border-gray-200 text-gray-600 px-5 py-2.5 rounded-[2px] text-[10px] font-black uppercase tracking-widest hover:bg-gray-50 transition-all shadow-sm"
        >
          DCS Terminal
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
              <th class="px-8 py-5">Node Name</th>
              <th class="px-8 py-5">Flight Flow</th>
              <th class="px-8 py-5 text-center">Equipment / Load</th>
              <th class="px-8 py-5">Boarding Signature</th>
              <th class="px-8 py-5 text-center">Protocol Status</th>
              <th class="px-8 py-5 text-right">Last Verified</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-gray-100 italic font-medium">
            <tr
              v-for="checkIn in paginatedCheckIns"
              :key="checkIn.id"
              class="hover:bg-gray-50/50 transition-all text-sm group/row"
            >
              <td class="px-8 py-5">
                <div class="flex items-center gap-4">
                  <div class="w-10 h-10 rounded-[2px] bg-sky-50 text-sky-600 flex items-center justify-center font-black border border-sky-100 group-hover:bg-sky-500 group-hover:text-white transition-all">
                    {{ checkIn.seat_number?.charAt(0) || '?' }}
                  </div>
                  <div>
                    <span class="font-black text-slate-800 block uppercase text-xs tracking-tight">{{ checkIn.passenger_name }}</span>
                    <span class="text-[9px] text-[#fe3787] font-black uppercase tracking-widest">Seat {{ checkIn.seat_number || 'TBD' }}</span>
                  </div>
                </div>
              </td>

              <td class="px-8 py-5">
                <span class="font-black text-slate-900 block uppercase text-xs tracking-tighter">{{ checkIn.flight_number }}</span>
                <div class="text-[9px] text-gray-400 font-bold uppercase tracking-widest">{{ checkIn.route?.replace('→', ' to ') }}</div>
              </td>

              <td class="px-8 py-5 text-center">
                <div class="flex flex-col items-center gap-1.5">
                  <div class="flex items-center gap-2 text-[9px] font-black text-slate-500 uppercase bg-slate-50 px-3 py-1.5 rounded-[2px] border border-slate-100">
                    <i class="ph ph-suitcase-simple"></i> {{ checkIn.baggage_count || 0 }} Bags • {{ checkIn.baggage_weight || 0 }}kg
                  </div>
                  <div v-if="checkIn.check_in_counter" class="text-[8px] text-gray-400 font-bold uppercase tracking-[0.2em]">Gate Node {{ checkIn.check_in_counter }}</div>
                </div>
              </td>

              <td class="px-8 py-5">
                <div v-if="checkIn.boarding_pass" class="flex items-center gap-3">
                  <i class="ph ph-fingerprint text-[#fe3787] text-xl animate-pulse"></i>
                  <span class="font-black text-slate-900 font-mono tracking-[0.15em] text-xs">{{ checkIn.boarding_pass }}</span>
                </div>
                <div v-else class="text-rose-500 font-black text-[9px] uppercase tracking-widest animate-pulse">Unauthorized Flow</div>
              </td>

              <td class="px-8 py-5 text-center">
                <span :class="statusClass(checkIn.status)" class="px-4 py-1.5 rounded-[2px] text-[9px] font-black uppercase tracking-widest border">
                  {{ checkIn.status }}
                </span>
              </td>

              <td class="px-8 py-5 text-right font-black text-[10px] text-gray-400 uppercase tracking-tight">
                {{ formatDateTime(checkIn.check_in_time) }}
              </td>
            </tr>

            <tr v-if="checkIns.length === 0 && !loading">
              <td colspan="6" class="px-8 py-20 text-center">
                <div class="flex flex-col items-center gap-4">
                  <i class="ph ph-airplane-landing text-5xl text-gray-200"></i>
                  <p class="text-gray-400 text-xs font-black uppercase tracking-widest">Manifest Empty — System operational</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="checkIns.length > itemsPerPage" class="mt-auto px-8 py-6 border-t border-gray-100 bg-gray-50/30 flex items-center justify-between">
        <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest">
          Manifest Range {{ startIndex + 1 }} to {{ endIndex }} of {{ checkIns.length }}
        </div>
        <div class="flex gap-1.5">
          <button @click="prevPage" :disabled="currentPage === 1" class="px-6 py-2.5 bg-white border border-gray-200 rounded-[2px] text-[10px] font-black uppercase tracking-widest hover:bg-black hover:text-white disabled:opacity-30 disabled:hover:bg-white transition-all shadow-sm">Back</button>
          <div class="flex gap-1">
            <button v-for="page in visiblePages" :key="page" @click="goToPage(page)" :disabled="page === '...'" :class="['w-10 h-10 flex items-center justify-center border rounded-[2px] text-[10px] font-black uppercase transition-all shadow-sm', page === '...' ? 'bg-white border-gray-200 text-gray-400' : currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787] shadow-lg shadow-pink-100' : 'bg-white border-gray-200 text-slate-900 hover:bg-gray-50']">{{ page }}</button>
          </div>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="px-6 py-2.5 bg-white border border-gray-200 rounded-[2px] text-[10px] font-black uppercase tracking-widest hover:bg-black hover:text-white disabled:opacity-30 disabled:hover:bg-white transition-all shadow-sm">Next</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import AuthStorage from '@/utils/authStorage'

const checkIns = ref([])
const loading = ref(false)
const currentPage = ref(1)
const itemsPerPage = 8

const statsItems = computed(() => {
  const total = checkIns.value.length
  const checkedIn = checkIns.value.filter(c => c.status === 'checked-in').length
  const pending = checkIns.value.filter(c => c.status === 'pending').length
  const weight = checkIns.value.reduce((sum, c) => sum + parseFloat(c.baggage_weight || 0), 0)
  
  return {
    'Total Manifest': total,
    'Clearance OK': checkedIn,
    'Node Pending': pending,
    'Gross Load (KG)': weight.toFixed(1)
  }
})

const statIcon = (label) => {
  if (label === 'Total Manifest') return 'ph ph-users-three';
  if (label === 'Clearance OK') return 'ph ph-shield-check';
  if (label === 'Node Pending') return 'ph ph-hourglass-medium';
  return 'ph ph-scales';
};

const statIconClass = (label) => {
  if (label === 'Total Manifest') return 'bg-blue-50 text-blue-600';
  if (label === 'Clearance OK') return 'bg-emerald-50 text-emerald-600';
  if (label === 'Node Pending') return 'bg-amber-50 text-amber-600';
  return 'bg-pink-50 text-[#fe3787]';
};

const fetchCheckIns = async () => {
  loading.value = true
  try {
    const res = await axios.get("http://localhost:8000/api/checkins/", {
      headers: AuthStorage.getApiHeaders()
    })
    checkIns.value = (res.data.results || res.data).map(c => ({
      ...c,
      passenger_name: `${c.passenger?.first_name || ''} ${c.passenger?.last_name || ''}`.trim().toUpperCase(),
      flight_number: c.booking_detail?.schedule?.flight?.flight_number || 'N/A',
      route: c.booking_detail?.schedule?.flight?.route?.name || 'N/A',
      seat_number: c.booking_detail?.seat?.seat_number || 'TBD',
      status: c.status || 'pending'
    })).sort((a, b) => b.id - a.id)
  } catch (err) { console.error(err) } finally { loading.value = false }
}

const formatDateTime = (d) => {
  if (!d) return 'UNVERIFIED'
  return new Date(d).toLocaleString('en-PH', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).toUpperCase()
}

const statusClass = (s) => {
  switch(s?.toLowerCase()) {
    case 'pending': return 'bg-amber-50 text-amber-700 border-amber-200'
    case 'checked-in': return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    case 'boarding': return 'bg-blue-50 text-blue-700 border-blue-200'
    case 'completed': return 'bg-slate-100 text-slate-700 border-slate-200'
    default: return 'bg-slate-100 text-slate-500 border-slate-200'
  }
}

// Pagination Logic
const totalPages = computed(() => Math.ceil(checkIns.value.length / itemsPerPage));
const paginatedCheckIns = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return checkIns.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, checkIns.value.length));

const visiblePages = computed(() => {
  const pages = []; const t = totalPages.value; const c = currentPage.value;
  if (t <= 5) for (let i = 1; i <= t; i++) pages.push(i)
  else {
    if (c <= 3) { for (let i = 1; i <= 4; i++) pages.push(i); pages.push('...', t) }
    else if (c >= t - 2) { pages.push(1, '...'); for (let i = t - 3; i <= t; i++) pages.push(i) }
    else pages.push(1, '...', c - 1, c, c + 1, '...', t)
  }
  return pages
})

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (p) => { if (p !== '...') currentPage.value = p }

onMounted(fetchCheckIns)
</script>

<style scoped>
.poppins { font-family: 'Poppins', sans-serif; }
</style>
