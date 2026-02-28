<template>
  <div class="space-y-6">
    <!-- Header with Stats -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black text-gray-900 tracking-tight">Flight Dashboard</h1>
        <p class="text-sm text-gray-500 font-medium">Manage upcoming departures and manifests.</p>
      </div>
      
      <div class="flex items-center gap-3">
        <div class="bg-white border border-gray-200 px-4 py-2 rounded-lg shadow-sm flex items-center gap-3">
          <div class="flex flex-col">
            <span class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Total Flights</span>
            <span class="text-lg font-black text-pink-600 leading-tight">{{ dcsStore.flights.length }}</span>
          </div>
          <div class="w-px h-8 bg-gray-100"></div>
          <div class="flex flex-col">
            <span class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Today</span>
            <span class="text-lg font-black text-gray-900 leading-tight">{{ todayFlightsCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="bg-white border border-gray-200 rounded-lg shadow-sm p-4 flex flex-col lg:flex-row items-center gap-4">
      <!-- Search -->
      <div class="relative flex-1 w-full">
        <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </span>
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Search flight #, origin, destination..." 
          class="w-full pl-11 pr-4 py-3 bg-gray-50 border-none rounded-lg text-sm focus:ring-2 focus:ring-pink-500/20 transition-all font-medium"
        />
      </div>

      <!-- Airline Filter -->
      <div class="flex items-center gap-2 w-full lg:w-auto">
        <select 
          v-model="selectedAirline"
          class="flex-1 lg:w-48 px-4 py-3 bg-gray-50 border-none rounded-lg text-sm focus:ring-2 focus:ring-pink-500/20 transition-all font-medium appearance-none cursor-pointer"
        >
          <option value="">All Airlines</option>
          <option v-for="airline in uniqueAirlines" :key="airline" :value="airline">{{ airline }}</option>
        </select>
        
        <button 
          @click="showTodayOnly = !showTodayOnly"
          :class="[
            'px-5 py-3 rounded-lg text-sm font-bold transition-all border shrink-0',
            showTodayOnly 
              ? 'bg-pink-600 border-pink-600 text-white shadow-md shadow-pink-200' 
              : 'bg-white border-gray-200 text-gray-600 hover:border-pink-300'
          ]"
        >
          Only Today
        </button>
      </div>

      <!-- Reset -->
      <button 
        v-if="hasFilters"
        @click="resetFilters"
        class="text-gray-400 hover:text-pink-600 p-2 transition-colors lg:ml-2"
        title="Reset Filters"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
      </button>
    </div>

    <!-- Error -->
    <div v-if="dcsStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3 text-red-700 text-sm animate-shake">
      <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      {{ dcsStore.error }}
    </div>

    <!-- Loading Skeleton -->
    <div v-if="dcsStore.isLoading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-pulse">
      <div v-for="i in 6" :key="i" class="bg-white rounded-lg border border-gray-100 h-52 shadow-sm"></div>
    </div>

    <!-- Flights Grid -->
    <div v-else-if="filteredFlights.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div
        v-for="flight in filteredFlights"
        :key="flight.id"
        class="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-xl hover:border-pink-300 transition-all group overflow-hidden flex flex-col relative"
      >
        <!-- Card Header -->
        <div class="px-5 py-4 bg-gradient-to-r from-pink-600 to-pink-500 flex justify-between items-center relative z-10">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-md flex items-center justify-center backdrop-blur-md">
               <span class="text-white font-black text-xs">{{ flight.airline_code }}</span>
            </div>
            <div class="flex flex-col">
              <span class="text-white font-black font-mono text-xl tracking-wider leading-none">{{ flight.flight_number }}</span>
              <span class="text-[10px] text-white/70 font-bold uppercase tracking-widest mt-0.5">{{ flight.airline_name }}</span>
            </div>
          </div>
          <div :class="[
            'flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm border',
            getStatusClass(flight.status)
          ]">
            <span :class="['w-1.5 h-1.5 rounded-full', flight.status === 'Open' ? 'bg-green-400 animate-pulse' : 'bg-current']"></span>
            {{ flight.status || 'Scheduled' }}
          </div>
        </div>

        <!-- Body -->
        <div class="px-6 py-6 flex-1 flex flex-col justify-between">
          <div class="flex items-center justify-between gap-4">
            <!-- Origin -->
            <div class="flex flex-col">
              <div class="text-4xl font-black text-gray-900 tracking-tighter">{{ flight.origin }}</div>
              <div class="text-sm font-bold text-gray-600 mt-1 uppercase">{{ formatTime(flight.departure_time) }}</div>
            </div>

            <!-- Path -->
            <div class="flex-1 flex flex-col items-center px-2">
              <div class="relative w-full flex items-center justify-center">
                <div class="absolute h-px w-full bg-dashed border-t border-gray-200 top-1/2 -translate-y-1/2"></div>
                <div class="relative z-10 bg-white px-2 text-pink-500 transform transition-transform group-hover:translate-x-3 duration-500">
                  <svg class="w-5 h-5 fill-current" viewBox="0 0 24 24">
                     <path d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5Z" />
                  </svg>
                </div>
              </div>
              <div class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-3 bg-gray-50 px-2 py-0.5 rounded-full">GATE {{ flight.gate }}</div>
            </div>

            <!-- Destination -->
            <div class="flex flex-col text-right">
              <div class="text-4xl font-black text-gray-900 tracking-tighter">{{ flight.destination }}</div>
              <div class="text-sm font-bold text-gray-600 mt-1 uppercase">{{ formatTime(flight.arrival_time) }}</div>
            </div>
          </div>

          <div class="mt-6 flex items-center justify-between text-[11px] font-bold text-gray-400">
            <div class="flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              {{ formatDate(flight.departure_time) }}
            </div>
            
            <div class="flex flex-col items-end gap-1.5">
              <div class="flex items-center gap-2">
                <span class="text-[9px] uppercase tracking-widest font-black text-gray-300">LOAD FACTOR</span>
                <span :class="[
                  'px-1.5 py-0.5 rounded text-[10px] font-black',
                  getFlightLoad(flight) > 85 ? 'bg-red-50 text-red-600' : 'bg-gray-50 text-gray-600'
                ]">{{ getFlightLoad(flight) }}%</span>
              </div>
              <div class="w-24 h-1 bg-gray-100 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-pink-500 rounded-full transition-all duration-1000" 
                  :style="{ width: `${getFlightLoad(flight)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Footer -->
        <div class="px-5 py-4 bg-gray-50 border-t border-gray-100 flex justify-end">
          <button
            @click="manageManifest(flight.id)"
            class="bg-white hover:bg-pink-600 border border-gray-200 hover:border-pink-600 text-gray-700 hover:text-white px-5 py-2.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all shadow-sm flex items-center gap-2 group/btn"
          >
            Manage Flight
            <svg class="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty/No Results -->
    <div v-else class="bg-white border-2 border-dashed border-gray-200 rounded-lg p-20 text-center shadow-inner">
      <div class="text-7xl mb-6 opacity-20 filter grayscale">🚀</div>
      <h3 class="text-2xl font-black text-gray-800 tracking-tight">
        {{ hasFilters ? 'No matches found' : 'No upcoming flights' }}
      </h3>
      <p class="text-base text-gray-400 mt-2 font-medium max-w-sm mx-auto">
        {{ hasFilters 
          ? 'Try adjusting your filters or search query to find the flight you are looking for.' 
          : 'The schedule is looking clear for now. New flights will appear here once registered.' 
        }}
      </p>
      
      <button 
        v-if="hasFilters"
        @click="resetFilters"
        class="mt-8 text-pink-600 font-bold hover:underline"
      >
        Clear all filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDcsStore } from '@/stores/dcs'

const router = useRouter()
const dcsStore = useDcsStore()

// Filter State
const searchQuery = ref('')
const selectedAirline = ref('')
const showTodayOnly = ref(false)

onMounted(() => {
  dcsStore.fetchFlights()
})

// Recommendations & Derived Data
const uniqueAirlines = computed(() => {
  const airlines = dcsStore.flights.map(f => f.airline_name).filter(Boolean)
  return [...new Set(airlines)].sort()
})

const todayFlightsCount = computed(() => {
  return dcsStore.flights.filter(f => isToday(f.departure_time)).length
})

const hasFilters = computed(() => {
  return searchQuery.value || selectedAirline.value || showTodayOnly.value
})

const filteredFlights = computed(() => {
  return dcsStore.flights.filter(flight => {
    // 1. Search Query (Number, Origin, Dest)
    const q = searchQuery.value.toLowerCase().trim()
    const matchesSearch = !q || 
      flight.flight_number.toLowerCase().includes(q) ||
      flight.origin.toLowerCase().includes(q) ||
      flight.destination.toLowerCase().includes(q) ||
      flight.airline_name.toLowerCase().includes(q)

    // 2. Airline Filter
    const matchesAirline = !selectedAirline.value || 
      flight.airline_name === selectedAirline.value

    // 3. Today Only
    const matchesToday = !showTodayOnly.value || isToday(flight.departure_time)

    return matchesSearch && matchesAirline && matchesToday
  })
})

const resetFilters = () => {
  searchQuery.value = ''
  selectedAirline.value = ''
  showTodayOnly.value = false
}

// Helpers
const getStatusClass = (status) => {
  switch (status) {
    case 'Open': return 'bg-green-50 text-green-700 border-green-100'
    case 'On Flight': return 'bg-blue-50 text-blue-700 border-blue-100'
    case 'Closed': return 'bg-red-50 text-red-700 border-red-100'
    case 'Arrived': return 'bg-gray-50 text-gray-700 border-gray-100'
    default: return 'bg-pink-50 text-pink-700 border-pink-100'
  }
}

const getFlightLoad = (flight) => {
  if (!flight.total_seats) return 0
  return Math.round((flight.booked_count / flight.total_seats) * 100)
}

const formatTime = (d) => {
  if (!d) return '--:--'
  return new Date(d).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' })
}
const formatDate = (d) => {
  if (!d) return '---'
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
const isToday = (d) => {
  if (!d) return false
  const date = new Date(d)
  const today = new Date()
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
}
const manageManifest = (id) => router.push(`/dcs/manifest/${id}`)
</script>

<style scoped>
.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

.bg-dashed {
  background-image: linear-gradient(to right, #e5e7eb 50%, rgba(255,255,255,0) 0%);
  background-position: bottom;
  background-size: 8px 1px;
  background-repeat: repeat-x;
}
</style>
