<template>
  <div id="app" class="min-h-screen flex flex-col bg-gray-50">
    <!-- <BookingTimer v-if="bookingStore.sessionExpiry" /> -->
    
    <!-- Header -->
    <header class="navbar bg-white relative z-10 py-4 border-b-10 border-[#FF579A] shadow-md">
      <div class="container mx-auto px-5 md:px-10">
        <div class="flex justify-between items-center">
          <!-- Logo -->
          <div class="logo flex items-center gap-3">
            <span class="brand-name font-bold text-[#FF579A] tracking-wide text-2xl">
              LOGO
            </span>
          </div>
          
          <!-- Navigation -->
          <nav class="flex gap-6">
            <router-link 
              to="/" 
              class="text-gray-700 font-medium hover:text-red-600 transition-colors"
              :class="{ 'text-red-600 border-b-2 border-red-600': $route.path === '/' }"
            >
              Book
            </router-link>
            <router-link 
              to="/check-in" 
              class="text-gray-700 font-medium hover:text-red-600 transition-colors"
              :class="{ 'text-red-600 border-b-2 border-red-600': $route.path === '/check-in' }"
            >
              Check-In
            </router-link>
            <router-link 
              to="/status" 
              class="text-gray-700 font-medium hover:text-red-600 transition-colors"
              :class="{ 'text-red-600 border-b-2 border-red-600': $route.path === '/status' }"
            >
              Flight Status
            </router-link>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content ">
      <router-view />
    </main>

    <!-- Footer -->
    <!-- <footer class="footer bg-gray-800 text-white py-6 mt-10">
      <div class="container mx-auto px-5 md:px-10 text-center">
        <p>&copy; 2024 Philippine Airlines. All rights reserved.</p>
      </div>
    </footer> -->
  </div>
</template>

<script setup>
import { useBookingStore } from '@/stores/booking';
import { useRouter, useRoute } from 'vue-router';
import BookingTimer from '@/components/booking/BookingTimer.vue';
import { onMounted, onUnmounted } from 'vue';

const bookingStore = useBookingStore();
const router = useRouter();
const route = useRoute();

let timerInterval = null;
const checkExpiry = () => {
  if (bookingStore.sessionExpiry && Date.now() > bookingStore.sessionExpiry){
    alert("Your booking session has expired. You will be redirected to the home page.");
    bookingStore.resetBooking();
    router.push('/');
  }
}
// onMounted(() => {
//   timerInterval = setInterval(checkExpiry, 1000);
// });

onUnmounted (() => {
  if (timerInterval) clearInterval(timerInterval);
});
</script>

<style>
/* Global button styles that might be used by child components */
.btn-cancel {
  margin-left: 20px;
  background: transparent;
  border: 1px solid #d11241;
  color: #d11241;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #d11241;
  color: white;
}
</style>