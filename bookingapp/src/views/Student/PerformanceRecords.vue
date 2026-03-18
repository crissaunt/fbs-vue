<template>
  <div class="p-8 max-w-7xl mx-auto min-h-screen bg-gray-50/50">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
      <div>
        <h1 class="text-4xl font-black text-gray-900 tracking-tight">Performance Records</h1>
        <p class="text-gray-500 mt-1 font-medium italic">Review your practice sessions and ground operation history.</p>
      </div>

      <!-- Tab Switcher -->
      <div class="flex bg-gray-200/50 p-1.5 rounded-2xl shadow-inner backdrop-blur-sm">
        <button 
          v-for="t in tabs" 
          :key="t.id"
          @click="activeTab = t.id"
          :class="[
            'px-6 py-2.5 rounded-xl text-[10px] font-black transition-all uppercase tracking-[0.2em]',
            activeTab === t.id 
              ? 'bg-white text-pink-600 shadow-sm scale-105' 
              : 'text-gray-500 hover:text-gray-800'
          ]"
        >
          {{ t.label }}
        </button>
      </div>
    </div>

    <!-- CONTENT SECTIONS -->
    <div class="relative min-h-[400px]">
      <transition name="fade-slide" mode="out-in">
        
        <!-- PRACTICE BOOKINGS -->
        <div v-if="activeTab === 'practice'" key="practice" class="space-y-4">
          <div v-if="loading" class="flex justify-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
          <div v-else-if="practiceBookings.length === 0" class="flex flex-col items-center justify-center py-24 bg-white rounded-[40px] border border-gray-100 shadow-sm">
            <div class="text-6xl mb-6 grayscale opacity-20">✈️</div>
            <h3 class="text-xl font-bold text-gray-400 uppercase tracking-widest">No Practice Records</h3>
            <p class="text-gray-400 mt-1 font-medium">Initialize a simulation to start building your history.</p>
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="booking in practiceBookings" 
              :key="booking.id"
              class="bg-white rounded-[32px] p-6 border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group"
            >
              <div class="flex justify-between items-start mb-6">
                <div :class="[
                  'px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest',
                  booking.ui_status === 'success' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                ]">
                  {{ booking.status }}
                </div>
                <span class="text-[10px] font-mono text-gray-400 uppercase tracking-tighter">{{ formatDate(booking.created_at) }}</span>
              </div>
              
              <h4 class="text-xl font-black text-gray-800 mb-1">{{ booking.route_summary }}</h4>
              <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-6">{{ booking.trip_type }} · {{ booking.passenger_count }} Passenger(s)</p>
              
              <div class="flex items-center justify-between pt-6 border-t border-gray-50">
                <div>
                  <p class="text-[9px] text-gray-400 font-black uppercase tracking-widest leading-none mb-1">Total Value</p>
                  <p class="text-lg font-black text-gray-900">₱{{ formatNumber(booking.total_amount) }}</p>
                </div>
                <div class="w-10 h-10 bg-gray-50 rounded-xl flex items-center justify-center text-xl group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  📋
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- DCS HISTORY -->
        <div v-else-if="activeTab === 'dcs'" key="dcs" class="space-y-4">
          <div v-if="loading" class="flex justify-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
          </div>
          <div v-else-if="checkinHistory.length === 0" class="flex flex-col items-center justify-center py-24 bg-white rounded-[40px] border border-gray-100 shadow-sm">
            <div class="text-6xl mb-6 grayscale opacity-20">🛂</div>
            <h3 class="text-xl font-bold text-gray-400 uppercase tracking-widest">No DCS Records</h3>
            <p class="text-gray-400 mt-1 font-medium">Head to Ground Ops to process your first check-in.</p>
          </div>
          <div v-else class="space-y-4">
            <div 
              v-for="ci in checkinHistory" 
              :key="ci.id"
              class="bg-white rounded-[24px] p-5 border border-gray-100 shadow-sm hover:shadow-md transition-all flex flex-wrap items-center justify-between gap-6"
            >
              <div class="flex items-center gap-5">
                <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center text-xl font-black">
                  {{ ci.flight_number.charAt(0) }}
                </div>
                <div>
                  <h4 class="text-base font-black text-gray-900 uppercase tracking-tight">{{ ci.passenger_name }}</h4>
                  <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">{{ ci.flight_number }} · {{ ci.route }}</p>
                </div>
              </div>

              <div class="flex items-center gap-12">
                <div>
                  <p class="text-[9px] text-gray-400 font-black uppercase tracking-widest mb-1">Sequence / Seat</p>
                  <p class="text-sm font-bold text-gray-800">{{ ci.sequence_number || ci.id }} · <span class="text-indigo-600">{{ ci.seat }}</span></p>
                </div>
                <div>
                  <p class="text-[9px] text-gray-400 font-black uppercase tracking-widest mb-1">Gate / Counter</p>
                  <p class="text-sm font-bold text-gray-800">{{ ci.gate }} · <span class="text-gray-500">{{ ci.counter }}</span></p>
                </div>
                <div class="text-right">
                  <p class="text-[9px] text-gray-400 font-black uppercase tracking-widest mb-1">Time</p>
                  <p class="text-sm font-bold text-gray-800">{{ formatDateTime(ci.check_in_time) }}</p>
                </div>
              </div>
              
              <div class="w-full sm:w-auto">
                <span class="px-4 py-1.5 bg-indigo-600 text-white rounded-full text-[10px] font-black uppercase tracking-widest">
                  {{ ci.status }}
                </span>
              </div>
            </div>
          </div>
        </div>

      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { studentDashboardService } from '@/services/Student/studentDashboardService'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

const activeTab = ref('practice')
const tabs = [
  { id: 'practice', label: 'Practice Bookings' },
  { id: 'dcs', label: 'DCS Operations' }
]

const loading = ref(true)
const practiceBookings = ref([])
const checkinHistory = ref([])

const loadData = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'practice') {
      const resp = await studentDashboardService.getPracticeBookings()
      practiceBookings.value = resp.data.practice_bookings
    } else {
      const resp = await studentDashboardService.getCheckinHistory()
      checkinHistory.value = resp.data.checkin_history
    }
  } catch (err) {
    console.error("Error loading records:", err)
    notificationStore.error("Could not load your records. Please try again later.")
  } finally {
    loading.value = false
  }
}

watch(activeTab, () => {
  loadData()
})

onMounted(() => {
  loadData()
})

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const formatNumber = (num) => {
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
