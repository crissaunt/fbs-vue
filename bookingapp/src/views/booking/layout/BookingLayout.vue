<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBookingStore } from '@/stores/booking'

const router = useRouter()
const bookingStore = useBookingStore()

const isSessionValid = computed(() => bookingStore.isSessionValid)

function handleReset() {
  const confirmed = confirm('Are you sure you want to cancel your booking? All progress will be lost.')
  if (confirmed) {
    bookingStore.resetBooking()
    router.push('/')
  }
}
</script>

<template>
  <div>
    <header class="bg-blue-900 shadow-md">
      <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">

        <router-link to="/" class="text-white font-bold text-xl tracking-wide flex items-center gap-2">
          ✈ <span>Philippine Airlines</span>
        </router-link>

        <nav class="hidden md:flex items-center gap-6">
            <router-link to="/check-in"  class="text-blue-200 hover:text-white text-sm font-medium transition-colors" active-class="text-white border-b-2 border-yellow-400 pb-0.5">Check-in</router-link>
            <router-link to="/status"    class="text-blue-200 hover:text-white text-sm font-medium transition-colors" active-class="text-white border-b-2 border-yellow-400 pb-0.5">Flight Status</router-link>
   
            <button
                v-if="isSessionValid"
                @click="handleReset"
                class="flex items-center gap-2 border bg-red-600 hover:bg-red-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors shadow"
                >
                ✕ Cancel Booking
            </button>
            <div v-else class="w-36" />
        </nav>



      </div>
    </header>

    <!-- ✅ slot instead of <router-view /> -->
    <slot />
  </div>
</template>