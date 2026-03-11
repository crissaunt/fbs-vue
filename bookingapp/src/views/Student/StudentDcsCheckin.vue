<template>
  <div class="min-h-screen bg-[#f5f3ef] py-12 px-6 poppins">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
        <div>
          <h1 class="text-3xl font-black text-[#002D1E] poppins tracking-tight uppercase">DCS Control Panel</h1>
          <div class="flex items-center gap-4 mt-1">
            <p class="text-sm text-gray-500 poppins">Passenger Registry and Departure Control System</p>
            <div class="h-4 w-px bg-gray-300 hidden md:block"></div>
            <div class="flex items-center gap-2">
              <i class="ph ph-calendar-blank text-[#fe3787] font-bold"></i>
              <span class="text-xs font-black text-[#002D1E] uppercase tracking-widest">{{ currentFormattedDate }}</span>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <button @click="refreshData" class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-[1px] hover:bg-gray-50 transition-all shadow-sm group">
            <i class="ph ph-arrows-clockwise text-[#002D1E] group-hover:rotate-180 transition-transform duration-500"></i>
            <span class="text-xs font-black text-[#002D1E] uppercase tracking-widest poppins">Refresh Data</span>
          </button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div v-for="(value, label) in statsItems" :key="label" class="bg-white p-6 rounded-[1px] border border-gray-100 shadow-sm flex items-center justify-between group hover:border-[#fe3787] transition-all">
          <div>
            <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest poppins mb-1">{{ label }}</div>
            <div class="text-2xl font-black text-[#002D1E] poppins">{{ value }}</div>
          </div>
          <div :class="statIconClass(label)" class="w-12 h-12 rounded-full flex items-center justify-center">
            <i :class="[statIcon(label), 'text-xl']"></i>
          </div>
        </div>
      </div>

      <!-- Search and Filter (Aligned with criss) -->
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6">
        <div class="flex flex-col md:flex-row md:items-center gap-4">
          <div class="relative flex-1">
            <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search by trainee or simulation ID..." 
              class="pl-10 pr-4 py-2 border border-gray-200 rounded-[1px] w-full outline-none focus:border-[#fe3787] transition-all poppins text-sm"
            >
          </div>
          <div class="flex gap-2">
            <select v-model="selectedFlight" class="px-4 py-2 border border-gray-200 rounded-[1px] bg-white text-sm outline-none focus:border-[#fe3787] transition-all poppins min-w-[150px]">
              <option value="">All Flights</option>
              <option v-for="flight in uniqueFlights" :key="flight" :value="flight">{{ flight }}</option>
            </select>
            <select v-model="selectedStatus" class="px-4 py-2 border border-gray-200 rounded-[1px] bg-white text-sm outline-none focus:border-[#fe3787] transition-all poppins min-w-[150px]">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="checked-in">Checked-In</option>
              <option value="boarding">Boarding</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Table Section -->
      <div class="bg-white rounded-[1px] border border-gray-100 shadow-xl overflow-hidden min-h-[500px] flex flex-col">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50/50 border-b border-gray-100">
            <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins">Trainee</th>
            <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins">Simulation Route</th>
            <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins text-center">Identity / Baggage</th>
            <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins">Boarding Token</th>
            <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins text-center">Status</th>
            <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins text-right">Actions</th>
              </tr>
            </thead>
            <tbody v-if="!loading && paginatedCheckIns.length > 0">
              <tr 
                v-for="c in paginatedCheckIns" 
                :key="c.id" 
                :id="`checkin-row-${c.id}`"
                :class="['border-b border-gray-50 hover:bg-gray-50/80 transition-all group', highlightedId === c.id ? 'highlight-active' : '']"
              >
                <td class="px-6 py-5">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs uppercase group-hover:bg-[#fe3787] group-hover:text-white transition-all">
                      {{ c.passenger_name?.charAt(0) }}
                    </div>
                    <div>
                      <div class="text-sm font-bold text-[#002D1E] poppins">{{ c.passenger_name }}</div>
                      <div class="text-[10px] font-bold text-gray-400 uppercase poppins">{{ c.seat_number || 'No Seat Assigned' }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-5">
                  <div class="text-sm font-bold text-[#002D1E] poppins group-hover:text-[#fe3787] transition-colors">
                    {{ c.flight_number }}
                    <i class="ph ph-link-simple text-[10px] opacity-0 group-hover:opacity-100 transition-opacity ml-1"></i>
                  </div>
                  <div class="text-[10px] text-gray-400 poppins">{{ formatRoute(c.route) }}</div>
                  <div class="text-[10px] text-gray-400 poppins uppercase">{{ formatTime(c.departure_time) }}</div>
                </td>
                <td class="px-6 py-5">
                   <div class="flex flex-col items-center gap-2">
                      <div class="flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-[1px] border border-gray-100 w-full justify-center">
                         <i class="ph ph-suitcase-simple text-gray-400"></i>
                         <span class="text-[10px] font-bold text-gray-600 poppins uppercase">{{ c.baggage_count || 0 }} Bags • {{ c.baggage_weight || 0 }}KG</span>
                      </div>
                      <div class="grid grid-cols-1 gap-1 w-full">
                         <div v-if="c.passport_expiry" class="text-[9px] font-bold text-gray-400 poppins uppercase flex items-center gap-1 justify-center">
                            <i class="ph ph-identification-card"></i> PASSPORT EXP: {{ c.passport_expiry }}
                         </div>
                         <div v-if="c.pwd_id_number" class="text-[9px] font-black text-pink-500 poppins uppercase flex items-center gap-1 justify-center">
                            <i class="ph ph-hand-heart"></i> PWD-ID: {{ c.pwd_id_number }}
                         </div>
                         <div v-if="c.senior_id_number" class="text-[9px] font-black text-blue-500 poppins uppercase flex items-center gap-1 justify-center">
                            <i class="ph ph-users"></i> SNR-ID: {{ c.senior_id_number }}
                         </div>
                      </div>
                   </div>
                </td>
                <td class="px-6 py-5">
                   <div v-if="c.boarding_pass" class="flex items-center gap-2">
                      <div class="w-8 h-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
                         <i class="ph ph-ticket text-lg"></i>
                      </div>
                      <span class="font-bold text-[#002D1E] poppins tracking-tighter text-sm uppercase">{{ c.boarding_pass }}</span>
                   </div>
                   <div v-else class="text-[#fe3787] font-bold poppins text-[10px] uppercase tracking-widest">Awaiting Issue</div>
                </td>
                <td class="px-6 py-5 text-center">
                  <span :class="['px-3 py-1 text-[10px] font-bold uppercase rounded-full poppins border', statusClass(c.status)]">
                    {{ c.status }}
                  </span>
                  <div class="text-[9px] text-gray-400 mt-1.5 poppins font-bold uppercase tracking-tighter">
                    {{ c.status === 'pending' ? 'NOT CHECKED' : formatDateTime(c.check_in_time) }}
                  </div>
                </td>
                <td class="px-6 py-5 text-right">
                  <div class="flex justify-end gap-2">
                    <button v-if="c.status === 'pending'" @click="checkInPassenger(c)" class="p-2 bg-green-50 text-green-600 hover:bg-green-600 hover:text-white transition-all rounded-[1px] shadow-sm" title="Registry">
                       <i class="ph ph-fingerprint text-lg"></i>
                    </button>
                    <button v-if="c.status === 'checked-in'" @click="printBoardingPass(c)" class="p-2 bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all rounded-[1px] shadow-sm" title="Boarding Pass">
                       <i class="ph ph-ticket text-lg"></i>
                    </button>
                    <button @click="editCheckIn(c)" class="p-2 bg-gray-50 text-gray-400 hover:bg-black hover:text-white transition-all rounded-[1px]" title="Edit">
                       <i class="ph ph-pencil-simple text-lg"></i>
                    </button>
                    <button @click="deleteCheckIn(c.id)" class="p-2 bg-red-50 text-red-500 hover:bg-red-500 hover:text-white transition-all rounded-[1px]" title="Remove">
                       <i class="ph ph-trash text-lg"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="!loading && paginatedCheckIns.length === 0" class="flex-1 flex flex-col items-center justify-center p-12 text-center">
          <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
            <i class="ph ph-airplane-takeoff text-2xl text-gray-300"></i>
          </div>
          <h3 class="text-lg font-bold text-[#002D1E] mb-2 poppins">No Records</h3>
          <p class="text-sm text-gray-400 poppins">Check-in data will appear here during active flights.</p>
        </div>

        <!-- Loading Overlay -->
        <div v-if="loading" class="flex-1 flex items-center justify-center">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[#fe3787]"></div>
        </div>

        <!-- Pagination -->
        <div v-if="filteredCheckIns.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
          <div class="flex items-center justify-between">
            <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
              Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ filteredCheckIns.length }}
            </div>
            <div class="flex gap-1">
              <button @click="prevPage" :disabled="currentPage === 1" class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm">Prev</button>
              <button v-for="page in visiblePages" :key="page" @click="goToPage(page)" :disabled="page === '...'" :class="['px-4 py-2 border rounded-[1px] text-xs font-bold uppercase poppins transition-all shadow-sm', page === '...' ? 'bg-white border-gray-200 text-gray-400' : currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'bg-white border-gray-200 text-[#002D1E] hover:bg-gray-50']">{{ page }}</button>
              <button @click="nextPage" :disabled="currentPage === totalPages" class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm">Next</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Registry Modal -->
    <div v-if="showCheckInModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">Registry Process</h2>
          <button @click="closeModal" class="text-gray-400 hover:text-black"><i class="ph ph-x text-xl"></i></button>
        </div>
        
        <form @submit.prevent="processCheckIn" class="space-y-6">
          <div class="bg-gray-50 p-4 border border-gray-100 rounded-[1px] flex items-center gap-4">
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600"><i class="ph ph-user text-xl"></i></div>
            <div>
              <div class="font-bold text-[#002D1E] poppins">{{ selectedCheckIn?.passenger_name }}</div>
              <div class="text-[10px] uppercase font-bold text-gray-400 poppins">Flight {{ selectedCheckIn?.flight_number }}</div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Seat Number</label>
              <input v-model="checkInForm.seat_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Counter</label>
              <input v-model="checkInForm.check_in_counter" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Bags</label>
              <input v-model="checkInForm.baggage_count" type="number" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Weight (kg)</label>
              <input v-model="checkInForm.baggage_weight" type="number" step="0.1" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Passport Expiry</label>
              <input v-model="checkInForm.passport_expiry" type="date" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] poppins">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">PWD ID Number</label>
              <input v-model="checkInForm.pwd_id_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] poppins" placeholder="Optional">
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Senior ID Number</label>
              <input v-model="checkInForm.senior_id_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] poppins" placeholder="Optional">
            </div>
          </div>
          
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Special Instructions</label>
            <textarea v-model="checkInForm.special_instructions" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" rows="2"></textarea>
          </div>
          
          <div class="flex justify-end gap-3 pt-6 border-t">
            <button type="button" @click="closeModal" class="text-sm text-gray-500 font-medium poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">Complete Registration</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Boarding Pass Modal -->
    <div v-if="showBoardingModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-sm rounded-[1px] shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
        <div class="bg-[#002D1E] p-6 text-white flex justify-between items-start">
          <div>
            <div class="text-[10px] uppercase font-bold opacity-60 poppins">Boarding Pass</div>
            <div class="text-2xl font-black poppins tracking-tighter uppercase">{{ selectedCheckIn?.flight_number }}</div>
          </div>
          <div class="text-right">
            <div class="text-[10px] uppercase font-bold opacity-60 poppins">Seat</div>
            <div class="text-2xl font-black poppins">{{ selectedCheckIn?.seat_number }}</div>
          </div>
        </div>
        
        <div class="p-6 space-y-4">
          <div class="border-b border-dashed border-gray-200 pb-4">
            <div class="text-[10px] uppercase font-bold text-gray-400 poppins">Passenger</div>
            <div class="text-lg font-bold text-[#002D1E] poppins">{{ selectedCheckIn?.passenger_name }}</div>
          </div>
          
          <div class="grid grid-cols-2 gap-4 pb-4 border-b border-dashed border-gray-200">
            <div>
              <div class="text-[10px] uppercase font-bold text-gray-400 poppins">Departure</div>
              <div class="font-bold text-[#002D1E] poppins">{{ formatTime(selectedCheckIn?.departure_time) }}</div>
            </div>
            <div>
              <div class="text-[10px] uppercase font-bold text-gray-400 poppins">Boarding</div>
              <div class="font-bold text-[#fe3787] poppins">{{ calculateBoardingTime(selectedCheckIn?.departure_time) }}</div>
            </div>
          </div>

          <div class="text-center py-4 bg-gray-50 border border-gray-100 rounded-[1px]">
             <div class="text-[14px] font-black font-mono text-gray-800 mb-2 leading-none uppercase tracking-widest">{{ selectedCheckIn?.boarding_pass }}</div>
             <div class="text-xs text-gray-400 poppins font-bold tracking-[0.4em]">||||||||||||||||||||||||||||||||||</div>
          </div>
        </div>

        <div class="p-4 bg-gray-50 flex justify-end gap-3">
          <button @click="closeBoardingModal" class="text-xs font-bold text-gray-400 uppercase poppins">Close</button>
          <button @click="printCurrentBoardingPass" class="bg-white border border-gray-200 px-4 py-2 text-xs font-bold uppercase shadow-sm rounded-[1px] poppins"><i class="ph ph-printer mr-2"></i> Print</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api/axios'

const route = useRoute()

// Reactive state
const checkIns = ref([])
const loading = ref(false)
const showCheckInModal = ref(false)
const showBoardingModal = ref(false)
const selectedCheckIn = ref(null)
const highlightedId = ref(null)
const itemsPerPage = 10
const currentPage = ref(1)

// Filters
const searchQuery = ref('')
const selectedFlight = ref('')
const selectedStatus = ref('')

const uniqueFlights = computed(() => {
  const flights = new Set(checkIns.value.map(c => c.flight_number))
  return Array.from(flights).sort()
})

const checkInForm = ref({
  seat_number: '',
  check_in_counter: '',
  baggage_count: 0,
  baggage_weight: 0,
  special_instructions: '',
  status: 'checked-in',
  pwd_id_number: '',
  senior_id_number: '',
  passport_expiry: ''
})

// Computed properties
const statsItems = computed(() => {
  const total = checkIns.value.length
  const todayStr = new Date().toISOString().split('T')[0]
  const todays = checkIns.value.filter(c => c.check_in_time && c.check_in_time.startsWith(todayStr)).length
  const pending = checkIns.value.filter(c => c.status === 'pending').length
  const baggage = checkIns.value.reduce((sum, c) => sum + (c.baggage_count || 0), 0)
  
  return {
    'Total Registered': total,
    "Today's Activity": todays,
    'Awaiting Registry': pending,
    'Baggage Units': baggage
  }
})

const currentFormattedDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const statIcon = (label) => {
  if (label === 'Total Registered') return 'ph ph-users-four';
  if (label === "Today's Activity") return 'ph ph-calendar-check';
  if (label === 'Awaiting Registry') return 'ph ph-hourglass-high';
  return 'ph ph-suitcase';
};

const statIconClass = (label) => {
  if (label === 'Total Registered') return 'bg-blue-100 text-blue-600';
  if (label === "Today's Activity") return 'bg-green-100 text-green-600';
  if (label === 'Awaiting Registry') return 'bg-purple-100 text-purple-600';
  return 'bg-pink-100 text-pink-600';
};

const filteredCheckIns = computed(() => {
  let filtered = checkIns.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(c => 
      c.passenger_name?.toLowerCase().includes(q) || 
      c.flight_number?.toLowerCase().includes(q)
    )
  }
  if (selectedFlight.value) filtered = filtered.filter(c => c.flight_number === selectedFlight.value)
  if (selectedStatus.value) filtered = filtered.filter(c => c.status === selectedStatus.value)
  return [...filtered].sort((a, b) => new Date(b.check_in_time || 0) - new Date(a.check_in_time || 0))
})

const totalPages = computed(() => Math.ceil(filteredCheckIns.value.length / itemsPerPage))
const paginatedCheckIns = computed(() => {
  const s = (currentPage.value - 1) * itemsPerPage
  return filteredCheckIns.value.slice(s, s + itemsPerPage)
})
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredCheckIns.length))

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

// Methods
const fetchCheckIns = async () => {
  loading.value = true
  try {
    // Note: Using student API endpoint
    const response = await api.get('api/check-ins/')
    checkIns.value = (response.data.results || response.data).map(c => ({
      ...c,
      passenger_name: `${c.passenger?.first_name || ''} ${c.passenger?.last_name || ''}`.trim(),
      flight_number: c.booking_detail?.schedule?.flight?.flight_number || '',
      route: c.booking_detail?.schedule?.flight?.route || '',
      departure_time: c.booking_detail?.schedule?.departure_time || '',
      seat_number: c.booking_detail?.seat?.seat_number || '',
      status: c.status || 'pending'
    }))

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;
        const index = checkIns.value.findIndex(c => c.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }
    }
  } catch (err) { 
    console.error(err) 
  } finally { 
    loading.value = false 
  }
}

const refreshData = () => fetchCheckIns()

const checkInPassenger = (c) => {
  selectedCheckIn.value = c
  checkInForm.value = {
    seat_number: c.seat_number || '',
    check_in_counter: c.check_in_counter || '',
    baggage_count: c.baggage_count || 0,
    baggage_weight: c.baggage_weight || 0,
    special_instructions: c.special_instructions || '',
    status: 'checked-in',
    pwd_id_number: c.pwd_id_number || '',
    senior_id_number: c.senior_id_number || '',
    passport_expiry: c.passport_expiry || ''
  }
  showCheckInModal.value = true
}

const processCheckIn = async () => {
  try {
    const bp = `BP-${Math.random().toString(36).substring(2, 10).toUpperCase()}`
    const data = { 
      ...checkInForm.value, 
      boarding_pass: bp, 
      check_in_time: new Date().toISOString(), 
      status: 'checked-in' 
    }
    await api.put(`api/check-ins/${selectedCheckIn.value.id}/`, data)
    await fetchCheckIns()
    closeModal()
    selectedCheckIn.value = checkIns.value.find(c => c.id === selectedCheckIn.value.id)
    showBoardingModal.value = true
  } catch (err) { 
    alert('Process failed.') 
  }
}

const printBoardingPass = (c) => { 
  selectedCheckIn.value = c; 
  showBoardingModal.value = true 
}

const printCurrentBoardingPass = () => window.print()

const editCheckIn = (c) => { 
  selectedCheckIn.value = c; 
  checkInForm.value = { ...c }; 
  showCheckInModal.value = true 
}

const deleteCheckIn = async (id) => {
  if (confirm('Delete this record?')) {
    try {
      await api.delete(`api/check-ins/${id}/`)
      checkIns.value = checkIns.value.filter(c => c.id !== id)
    } catch (err) {
      alert('Delete failed.')
    }
  }
}

const closeModal = () => { 
  showCheckInModal.value = false; 
  selectedCheckIn.value = null 
}

const closeBoardingModal = () => { 
  showBoardingModal.value = false; 
  selectedCheckIn.value = null 
}

const statusClass = (s) => {
  switch(s?.toLowerCase()) {
    case 'pending': return 'bg-purple-100 text-purple-700 border-purple-200'
    case 'checked-in': return 'bg-green-100 text-green-700 border-green-200'
    case 'boarding': return 'bg-blue-100 text-blue-700 border-blue-200'
    case 'completed': return 'bg-gray-100 text-gray-700 border-gray-200'
    default: return 'bg-gray-100 text-gray-500 border-gray-200'
  }
}

const formatRoute = (r) => r?.replace('→', ' to ') || 'N/A'
const formatTime = (d) => d ? new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A'
const formatDateTime = (d) => d ? new Date(d).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'N/A'
const calculateBoardingTime = (d) => d ? new Date(new Date(d).getTime() - 30 * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'TBD'

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (p) => { if (p !== '...') currentPage.value = p }

watch([searchQuery, selectedFlight, selectedStatus], () => currentPage.value = 1)
onMounted(fetchCheckIns)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

@keyframes pulse-highlight {
  0% { background-color: rgba(254, 55, 135, 0.05); }
  50% { background-color: rgba(254, 55, 135, 0.2); }
  100% { background-color: rgba(254, 55, 135, 0.05); }
}

.highlight-active {
  animation: pulse-highlight 1.5s ease-in-out infinite;
  border-left: 4px solid #fe3787 !important;
  box-shadow: inset 0 0 20px rgba(254, 55, 135, 0.1);
}

.poppins { font-family: 'Poppins', sans-serif !important; }

@media print { 
  .no-print { display: none; } 
  body * { visibility: hidden; }
  .fixed.inset-0 { position: absolute; left: 0; top: 0; }
  .max-w-sm { width: 100%; max-width: none; }
  .max-w-sm * { visibility: visible; }
}

/* Phosphor Icons implementation if needed, assuming they are available globally via link */
</style>
