<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- TOP HEADER — matches DashboardHeader style -->
    <header class="bg-pink-500 text-white px-4 py-2.5 flex items-center justify-between shadow-md z-20 shrink-0">
      <div class="flex items-center gap-3">
        <!-- Icon + Title -->
        <div class="w-7 h-7 bg-white rounded-full flex items-center justify-center text-base">🖥️</div>
        <div>
          <h1 class="text-xs font-bold leading-tight">DEPARTURE CONTROL SYSTEM</h1>
          <p class="text-[9px] opacity-90 leading-tight">Agent Check-in Portal</p>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <!-- Clock -->
        <div class="text-xs font-mono opacity-90 hidden sm:block">{{ currentTime }}</div>

        <div class="h-4 w-px bg-white/30"></div>

        <!-- Online Indicator -->
        <div class="flex items-center gap-1.5 text-xs opacity-90">
          <span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
          System Online
        </div>

        <div class="h-4 w-px bg-white/30"></div>

        <!-- Exit Button -->
        <button
          @click="exitDcs"
          class="flex items-center gap-1.5 text-xs font-semibold hover:bg-pink-600/50 px-2 py-1 rounded transition-colors"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Exit Portal
        </button>
      </div>
    </header>

    <!-- PINK BANNER (like Student Dashboard banner) -->
    <div class="bg-pink-500 mx-6 mt-5 px-8 py-8 rounded-lg shadow-lg shrink-0">
      <h2 class="text-white text-xl font-light tracking-wide">
        {{ bannerTitle }}
      </h2>
      <p class="text-white/80 text-sm mt-1">{{ bannerSubtitle }}</p>
    </div>

    <!-- CONTENT AREA -->
    <main class="flex-1 overflow-y-auto px-6 py-6">
      <div class="max-w-7xl mx-auto">
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDcsStore } from '@/stores/dcs'

const router = useRouter()
const route = useRoute()
const dcsStore = useDcsStore()

const currentTime = ref('')
let timer

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})

const bannerTitle = computed(() => {
  if (route.name === 'DcsManifest' && dcsStore.selectedSchedule) {
    return `Flight ${dcsStore.selectedSchedule.flight_number} — Passenger Manifest`
  }
  if (route.name === 'DcsCheckin') {
    return 'Check-in Counter — Agent Simulation'
  }
  return 'Departing Flights'
})

const bannerSubtitle = computed(() => {
  if (route.name === 'DcsManifest' && dcsStore.selectedSchedule) {
    return `${dcsStore.selectedSchedule.origin} → ${dcsStore.selectedSchedule.destination} · Select a passenger to check them in`
  }
  if (route.name === 'DcsCheckin') {
    return 'Verify documents, check weight, and issue boarding pass'
  }
  return 'Select a flight to manage passenger check-in'
})

const exitDcs = () => {
  dcsStore.clearSelection()
  router.push('/student/dashboard')
}
</script>
