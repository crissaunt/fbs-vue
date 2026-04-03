<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBookingStore } from '@/stores/booking'
import { useModalStore } from '@/stores/modal'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const bookingStore = useBookingStore()
const modalStore = useModalStore()
const notificationStore = useNotificationStore()

const isSessionValid = computed(() => bookingStore.isSessionValid)
const isPracticeMode = computed(() => bookingStore.isPractice)
const hasValidation = computed(() => bookingStore.hasActivityCodeValidation)
const timeLeft = computed(() => bookingStore.timeLeftFormatted)
const secondsLeft = computed(() => bookingStore.secondsLeft)
const isUrgent = computed(() => secondsLeft.value < 120 && secondsLeft.value > 0)

let timerInterval = null

onMounted(() => {
  timerInterval = setInterval(() => {
    const session = bookingStore.checkSession()
    if (!session.valid && hasValidation.value) {
      handleTimeUp()
    }
  }, 1000)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

async function handleTimeUp() {
  if (timerInterval) clearInterval(timerInterval)
  
  await modalStore.error({
    title: 'Time Limit Reached',
    message: 'You have no time left.',
    confirmText: 'Close'
  })
  
  bookingStore.clearActivityCodeValidation()
  bookingStore.resetBooking()
  router.push('/student/dashboard')
}

async function handleReset() {
  const confirmed = await modalStore.confirm({
    title: 'Reset Search?',
    message: 'Are you sure you want to reset your search? Your selected flights and passenger details will be cleared.',
    confirmText: 'Reset Search',
    cancelText: 'Cancel'
  })
  
  if (confirmed) {
    bookingStore.resetBooking()
    router.push('/')
  }
}

async function handleEndSession() {
  const sessionType = isPracticeMode.value ? 'practice session' : 'activity'
  const confirmed = await modalStore.confirm({
    title: isPracticeMode.value ? 'End Practice?' : 'End Activity?',
    message: `Are you sure you want to end this ${sessionType}? All progress will be permanently cleared and you will return to the dashboard.`,
    confirmText: 'End Session',
    cancelText: 'Stay'
  })
  
  if (confirmed) {
    console.log(`🧹 Ending ${sessionType}...`)
    bookingStore.clearActivityCodeValidation()
    bookingStore.resetBooking()
    router.push('/student/dashboard')
  }
}
</script>

<template>
  <div>
    <header class="bg-gray-100 shadow-lg/20">
      <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">

        <router-link to="/" class="text-[#FF579A] font-bold text-xl tracking-wide flex items-center gap-2">
           <span>TourSim</span>
        </router-link>

        <nav class="flex items-center gap-2 md:gap-6">
            <div class="flex items-center gap-2 md:gap-3">
              <!-- Activity Timer -->
              <div 
                v-if="hasValidation" 
                :class="[
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg border font-black transition-all',
                  isUrgent ? 'bg-red-50 border-red-200 text-red-600 animate-pulse' : 'bg-white border-slate-200 text-slate-700'
                ]"
              >
                <i :class="['ph ph-timer text-lg', isUrgent ? 'text-red-500' : 'text-slate-400']"></i>
                <div class="flex flex-col leading-none">
                  <span class="text-[8px] uppercase tracking-tighter opacity-70">Remaining Time</span>
                  <span class="text-xs font-mono">{{ timeLeft }}</span>
                </div>
              </div>

              <!-- Reset Search Button (Only if validated) -->
              <button
                  v-if="hasValidation"
                  @click="handleReset"
                  class="flex items-center gap-1.5 bg-blue-800 cursor-pointer hover:bg-blue-700/80 text-white text-[10px] md:text-xs font-semibold px-2.5 py-1.5 md:px-3 md:py-1.5 rounded-md transition-colors"
                  title="Reset search and passenger data"
                >
                  ↺ <span class="hidden sm:inline">Reset</span>
              </button>

              <!-- End Activity/Practice Button -->
              <button
                  v-if="hasValidation"
                  @click="handleEndSession"
                  class="flex items-center gap-1.5 bg-red-600 hover:bg-red-600/80 cursor-pointer text-white text-[10px] md:text-xs font-bold px-3 py-1.5 md:px-4 md:py-1.5 rounded-lg transition-colors"
                >
                  ✕ <span class="hidden sm:inline">{{ isPracticeMode ? 'End Practice' : 'End Activity' }}</span>
                  <span class="sm:hidden">{{ isPracticeMode ? 'Practice' : 'Activity' }}</span>
              </button>
            </div>
        </nav>



      </div>
    </header>

    <!-- ✅ slot instead of <router-view /> -->
    <slot />
  </div>
</template>