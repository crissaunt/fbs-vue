<template>
  <div class="flex flex-col h-screen bg-[#FDF2F8]/30 font-sans text-slate-900 overflow-hidden">
    <!-- MODERN AVIATION HEADER -->
    <header class="bg-[#0F172A] text-white px-6 py-3.5 flex items-center justify-between shadow-lg z-30 shrink-0 border-b border-pink-500/20">
      <div class="flex items-center gap-4">
        <!-- Logo/Icon -->
        <div class="w-9 h-9 bg-gradient-to-br from-pink-500 to-rose-700 rounded-[5px] flex items-center justify-center shadow-pink-500/20 shadow-lg text-lg">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
        </div>
        <div class="flex flex-col">
          <h1 class="text-xs font-black tracking-[0.2em] leading-tight text-pink-400 uppercase">Aviation Terminal</h1>
          <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-tight mt-0.5">DCS Agent Simulation Portal</p>
        </div>
      </div>

      <div class="flex items-center gap-6">
        <!-- Clock -->
        <div class="flex flex-col items-end">
          <span class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Local Server Time</span>
          <div class="text-sm font-black font-mono tracking-tighter text-pink-100">{{ currentTime }}</div>
        </div>

        <div class="h-8 w-px bg-white/10 hidden sm:block"></div>

        <!-- System State -->
        <div class="hidden md:flex items-center gap-3">
          <div class="flex flex-col items-end">
            <span class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Network Status</span>
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse"></span>
              <span class="text-[10px] font-bold text-slate-300 uppercase tracking-wider">Secure Connection</span>
            </div>
          </div>
        </div>

        <div class="h-8 w-px bg-white/10"></div>

        <!-- Exit Button -->
        <button
          @click="exitDcs"
          class="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-[2px] transition-all duration-300 border border-slate-700 hover:border-pink-500/50 group"
        >
          <span class="text-[10px] font-black text-slate-300 group-hover:text-white uppercase tracking-widest">Logout</span>
          <svg class="w-4 h-4 text-slate-400 group-hover:text-pink-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </header>


    <!-- CONTENT AREA -->
    <main class="flex-1 overflow-y-auto px-8 py-8 relative">
      <!-- Grid/Pattern Background Overlay -->
      <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: linear-gradient(#db2777 1px, transparent 1px), linear-gradient(90deg, #db2777 1px, transparent 1px); background-size: 40px 40px;"></div>
      
      <div class="max-w-7xl mx-auto relative z-10 transition-all duration-500">
        <router-view v-slot="{ Component }">
          <transition 
            name="fade-slide" 
            mode="out-in"
          >
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- MINI FOOTER STATUS -->
    <footer class="bg-white border-t border-slate-200 px-6 py-2 flex items-center justify-between shrink-0 z-20">
       <div class="flex items-center gap-4">
         <div class="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
           <span class="w-1.5 h-1.5 rounded-full bg-pink-500"></span>
           Active Session
         </div>
       </div>
       <div class="text-[10px] font-medium text-slate-400">
         v3.0.0-DCS · Departure Control Management System
       </div>
    </footer>
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

const getViewIcon = computed(() => {
  if (route.name === 'DcsManifest') return '📋'
  if (route.name === 'DcsCheckin') return '🪪'
  return '🛫'
})

const bannerTitle = computed(() => {
  if (route.name === 'DcsManifest' && dcsStore.selectedSchedule) {
    return `${dcsStore.selectedSchedule.flight_number} Manifest`
  }
  if (route.name === 'DcsCheckin') {
    return 'Check-in Counter'
  }
  return 'Departure Scheduling'
})

const bannerSubtitle = computed(() => {
  if (route.name === 'DcsManifest' && dcsStore.selectedSchedule) {
    return `${dcsStore.selectedSchedule.origin} → ${dcsStore.selectedSchedule.destination}`
  }
  if (route.name === 'DcsCheckin') {
    return 'Document Verification & Baggage Processing'
  }
  return 'Flight Dispatch & Real-time Monitoring'
})

const exitDcs = () => {
  dcsStore.clearSelection()
  router.push('/student/dashboard')
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
