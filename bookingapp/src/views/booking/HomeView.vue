<template>
  <div class=" bg-gray-50">
    <section class="hero relative flex items-center justify-center text-white py-35 ">
      <div class="container mx-auto px-4 space-y-4 relative z-10">
        <h1 class="text-5xl   font-black  tracking-tight drop-shadow-lg">
          Welcome Home, Mabuhay!
        </h1>
        <p class="text-base mb-8  opacity-90 max-w-2xl font-medium">
          Book your next adventure across the Philippines and beyond.
        </p>
        
        <div class="text-slate-900">
          <FlightSearch />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import FlightSearch from '@/components/booking/FlightSearch.vue';

const bookingStore = useBookingStore();
const sessionCleared = ref(false);

// Clear any existing booking session when visiting home
onMounted(() => {
  console.log('🏠 HomeView mounted - checking for active booking sessions...');
  
  // Check if there's an active session
  const session = bookingStore.checkSession();
  
  if (session.valid) {
    console.log('⚠️ Active booking session found. Resetting...');
    
    // Show confirmation if user has unsaved data
    if (bookingStore.passengers.length > 0 || bookingStore.selectedOutbound) {
      const userConfirmed = window.confirm(
        'We found an active booking session. Would you like to start a new search? Your current booking data will be cleared.'
      );
      
      if (userConfirmed) {
        bookingStore.resetBooking();
        sessionCleared.value = true;
        
        // Hide message after 5 seconds
        setTimeout(() => {
          sessionCleared.value = false;
        }, 5000);
      } else {
        // Redirect to review if user wants to continue
        if (bookingStore.booking_id) {
          window.location.href = '/review/booking';
          return;
        }
      }
    } else {
      // Just reset silently if no real data
      bookingStore.resetBooking();
    }
  } else {
    // Make sure store is clean
    bookingStore.resetBooking();
  }
  
  // Log status for debugging
  console.log('📊 Current booking state after cleanup:', {
    hasBookingId: !!bookingStore.booking_id,
    hasPassengers: bookingStore.passengers.length,
    hasOutbound: !!bookingStore.selectedOutbound,
    hasReturn: !!bookingStore.selectedReturn,
    sessionExpired: !session.valid
  });
});
</script>

<style scoped>
.hero {
  /* Using #FF579A at 0.8 (80%) opacity per your request */
  background: 
              url('@/assets/image/bg-cthm.svg');
  background-size: cover;
  background-position: center;
}
</style>