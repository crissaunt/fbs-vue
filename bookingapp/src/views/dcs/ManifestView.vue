<template>
  <div class="space-y-5">
    <!-- Back + Stats Row -->
    <div class="flex flex-wrap items-center gap-3">
      <button
        @click="router.push('/dcs/dashboard')"
        class="flex items-center gap-2 text-sm font-semibold text-gray-600 hover:text-pink-600 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        Back to Flights
      </button>

      <div class="flex-1 flex flex-wrap gap-3 justify-end">
        <!-- Scan QR Button -->
        <button
          @click="showScanner = true"
          class="bg-pink-500 hover:bg-pink-600 text-white text-sm font-bold px-4 py-2 rounded-lg transition-colors shadow-sm flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 9V6a3 3 0 013-3h3M15 3h3a3 3 0 013 3v3M3 15v3a3 3 0 003 3h3M15 21h3a3 3 0 003-3v-3"/>
            <rect x="7" y="7" width="10" height="10" rx="1" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Scan QR
        </button>

        <div class="bg-white border border-gray-200 rounded-lg px-4 py-2 text-center shadow-sm min-w-[90px]">
          <div class="text-xs text-gray-400 font-medium">Total</div>
          <div class="text-xl font-black text-gray-900">{{ dcsStore.totalPassengers }}</div>
        </div>
        <div class="bg-white border border-green-200 rounded-lg px-4 py-2 text-center shadow-sm min-w-[90px]">
          <div class="text-xs text-green-500 font-medium">Checked-In</div>
          <div class="text-xl font-black text-green-600">{{ dcsStore.checkedInPassengers }}</div>
        </div>
        <div class="bg-white border border-amber-200 rounded-lg px-4 py-2 text-center shadow-sm min-w-[90px]">
          <div class="text-xs text-amber-500 font-medium">Pending</div>
          <div class="text-xl font-black text-amber-600">{{ dcsStore.pendingPassengers }}</div>
        </div>
      </div>
    </div>

    <!-- Search -->
    <div class="bg-white border border-gray-200 rounded-lg px-4 py-2.5 shadow-sm flex items-center gap-3">
      <svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Search by PNR or Passenger Name..."
        class="flex-1 text-sm text-gray-700 placeholder-gray-400 outline-none bg-transparent"
      >
    </div>

    <!-- Error -->
    <div v-if="dcsStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
      {{ dcsStore.error }}
    </div>

    <!-- Loading -->
    <div v-if="dcsStore.isLoading && !dcsStore.manifest.length" class="space-y-2 animate-pulse">
      <div class="h-10 bg-gray-100 rounded-lg border border-gray-200"></div>
      <div v-for="i in 8" :key="i" class="h-14 bg-white rounded-lg border border-gray-100 opacity-70"></div>
    </div>

    <!-- Manifest Table -->
    <div v-else class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="border-b border-gray-200 bg-gray-50 text-xs text-gray-500 font-bold uppercase tracking-wider">
              <th class="px-5 py-3 cursor-pointer hover:text-pink-600" @click="sortBy('pnr')">
                PNR <span v-if="sortKey === 'pnr'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="px-5 py-3 cursor-pointer hover:text-pink-600" @click="sortBy('passenger_name')">
                Passenger <span v-if="sortKey === 'passenger_name'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="px-5 py-3 hidden md:table-cell">Type</th>
              <th class="px-5 py-3 hidden lg:table-cell cursor-pointer hover:text-pink-600" @click="sortBy('seat')">
                Seat <span v-if="sortKey === 'seat'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="px-5 py-3 hidden xl:table-cell">Allowance</th>
              <th class="px-5 py-3 cursor-pointer hover:text-pink-600" @click="sortBy('status')">
                Status <span v-if="sortKey === 'status'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="px-5 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <template v-if="filteredAndSortedManifest.length > 0">
              <tr
                v-for="passenger in filteredAndSortedManifest"
                :key="passenger.booking_detail_id"
                class="hover:bg-pink-50/40 transition-colors group"
                :class="{ 'bg-pink-50 ring-1 ring-pink-300': highlightedPnr && passenger.pnr === highlightedPnr }"
              >
                <td class="px-5 py-3.5 font-mono font-bold text-gray-700">{{ passenger.pnr }}</td>
                <td class="px-5 py-3.5 font-semibold text-gray-900">{{ passenger.passenger_name }}</td>
                <td class="px-5 py-3.5 hidden md:table-cell text-gray-400">{{ passenger.passenger_type }}</td>
                <td class="px-5 py-3.5 hidden lg:table-cell font-mono font-bold text-gray-700">
                  {{ passenger.seat || 'TBA' }}
                </td>
                <td class="px-5 py-3.5 hidden xl:table-cell text-gray-400 text-xs">
                  {{ passenger.baggage_allowance_name }}
                  <span class="font-semibold text-gray-600 ml-1" v-if="passenger.allowed_baggage_weight > 0">({{ passenger.allowed_baggage_weight }} KG)</span>
                </td>
                <td class="px-5 py-3.5">
                  <span :class="[
                    'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold',
                    passenger.status === 'checkin' || passenger.status === 'boarding'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-amber-100 text-amber-700'
                  ]">
                    <span class="w-1.5 h-1.5 rounded-full" :class="passenger.status === 'checkin' || passenger.status === 'boarding' ? 'bg-green-500' : 'bg-amber-400'"></span>
                    {{ passenger.status === 'checkin' ? 'Checked-In' : passenger.status === 'boarding' ? 'Boarding' : 'Pending' }}
                  </span>
                </td>
                <td class="px-5 py-3.5 text-right whitespace-nowrap">
                  <button
                    v-if="passenger.status !== 'checkin' && passenger.status !== 'boarding'"
                    @click="openCheckin(passenger)"
                    class="bg-pink-500 hover:bg-pink-600 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors shadow-sm"
                  >
                    Check In
                  </button>
                  <button
                    v-else
                    @click="reprintBoardingPass(passenger)"
                    class="border border-gray-200 text-gray-500 hover:border-pink-300 hover:text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
                  >
                    Print Pass
                  </button>
                </td>
              </tr>
            </template>
            <tr v-else>
              <td colspan="7" class="px-5 py-10 text-center text-gray-400 text-sm">
                No passengers match your search.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div class="px-5 py-3 bg-gray-50 border-t border-gray-200 flex justify-between items-center text-xs text-gray-400">
        <span>Showing {{ filteredAndSortedManifest.length }} of {{ dcsStore.totalPassengers }} passengers</span>
        <button @click="refreshManifest" class="flex items-center gap-1 hover:text-pink-600 transition-colors font-medium">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" :class="{ 'animate-spin': dcsStore.isLoading }">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- QR Scanner Modal -->
    <QrScannerModal
      v-if="showScanner"
      :schedule-id="schedule_id"
      @close="showScanner = false"
      @passenger-selected="handleScanResult"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDcsStore } from '@/stores/dcs'
import QrScannerModal from '@/components/dcs/QrScannerModal.vue'

const props = defineProps({
  schedule_id: { type: [String, Number], required: true }
})

const router = useRouter()
const route = useRoute()
const dcsStore = useDcsStore()

const searchQuery = ref('')
const sortKey = ref('passenger_name')
const sortOrder = ref('asc')
const showScanner = ref(false)
const highlightedPnr = ref(null)

onMounted(() => {
  dcsStore.fetchManifest(props.schedule_id)
  
  // If we just came back from a successful check-in
  if (route.query.checkedin) {
    const pId = route.query.checkedin
    // Optional: auto-open boarding pass or show success
    // reprintBoardingPass({ booking_detail_id: pId })
  }
})

const refreshManifest = () => dcsStore.fetchManifest(props.schedule_id)

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const filteredAndSortedManifest = computed(() => {
  let result = dcsStore.manifest
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      (p.passenger_name?.toLowerCase().includes(q)) ||
      (p.pnr?.toLowerCase().includes(q))
    )
  }
  return [...result].sort((a, b) => {
    let va = (a[sortKey.value] || '').toString().toLowerCase()
    let vb = (b[sortKey.value] || '').toString().toLowerCase()
    if (va < vb) return sortOrder.value === 'asc' ? -1 : 1
    if (va > vb) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})

const openCheckin = (p) => { 
  router.push(`/dcs/checkin/${p.booking_detail_id}`)
}

/**
 * When a passenger is selected from the QR scanner, navigate to check-in
 */
const handleScanResult = (passenger) => {
  showScanner.value = false
  openCheckin(passenger)
}

const reprintBoardingPass = (p) => {
  window.open(`http://localhost:8000/flightapp/download-boarding-pass/${p.booking_detail_id}/`, '_blank')
}
</script>
