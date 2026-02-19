<template>
  <div class="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-50 p-4 md:p-8 relative overflow-hidden">
    <!-- Subtle Background Pattern -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute top-0 right-0 w-1/3 h-1/3 bg-gradient-to-br from-[#FF579A]/5 to-transparent rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-1/3 h-1/3 bg-gradient-to-tr from-pink-400/5 to-transparent rounded-full blur-3xl"></div>
      
      <!-- Grid Pattern -->
      <div class="absolute inset-0 opacity-[0.02] bg-[length:40px_40px] bg-[radial-gradient(#FF579A_1px,transparent_1px)]"></div>
    </div>

    <!-- Main Container -->
    <div class="relative max-w-6xl mx-auto">
      <!-- Success Header -->
      <div class="text-center mb-10 md:mb-16">
        <div class="relative inline-flex mb-8">
          <!-- Animated Success Ring -->
          <div class="absolute inset-0 animate-ping bg-gradient-to-r from-[#FF579A] to-pink-400 rounded-full opacity-20"></div>
          
          <!-- Success Icon Container -->
          <div class="relative w-28 h-28 bg-white rounded-2xl  flex items-center justify-center border border-pink-100">
            <!-- Checkmark Circle -->
            <div class="w-20 h-20 bg-gradient-to-br from-[#FF579A] via-pink-500 to-pink-400 rounded-full flex items-center justify-center ">
              <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <!-- Plane Icon -->
            <div class="absolute -top-3 -right-3 w-14 h-14 bg-white rounded-xl  border border-pink-100 flex items-center justify-center">
              <span class="text-2xl">✈️</span>
            </div>
          </div>
        </div>

        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4 tracking-tight">
          Booking <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#FF579A] to-pink-500">Confirmed</span>
        </h1>
        <p class="text-lg text-gray-600">Your flight details have been successfully processed</p>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Email Confirmation Card -->
          <div class="bg-white rounded-2xl  border border-gray-300 p-8">
            <div class="flex items-start space-x-6">
              <div class="w-16 h-16 bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl flex items-center justify-center">
                <span class="text-3xl text-[#FF579A]">📧</span>
              </div>
              <div class="flex-1">
                <div class="flex items-center justify-between ">
                  <h2 class="text-2xl font-bold text-gray-900">E-ticket Sent</h2>
                  <span class="px-4 py-1.5 bg-emerald-50 text-emerald-700 rounded-full text-[11px] font-semibold border border-emerald-100">
                    ✓ Delivered
                  </span>
                </div>
                <p class="text-gray-600 mb-6 text-[11px]">
                  Your booking confirmation and boarding pass have been sent to your registered email address.
                  You can also download them from your account.
                </p>
                <div class="bg-amber-50 border border-amber-100 rounded-xl p-4">
                  <div class="flex items-start space-x-3">
                    <span class="text-amber-500 text-xl mt-0.5">💡</span>
                    <div>
                      <p class="text-amber-800 font-medium mb-1">Check your spam folder</p>
                      <p class="text-amber-700 text-[11px]">If you don't see the email in your inbox, please check your spam or junk folder.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Booking Details -->
          <div class="bg-white rounded-2xl  border border-gray-300 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-8">Booking Information</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Reference Card -->
              <div class="group bg-gray-50 hover:bg-white border border-gray-200 hover:border-[#FF579A]/30 rounded-xl p-6 transition-all duration-300 cursor-pointer">
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 bg-pink-50 rounded-lg flex items-center justify-center">
                      <span class="text-xl text-[#FF579A]">🎫</span>
                    </div>
                    <span class="text-sm font-semibold text-gray-500 uppercase tracking-wider">Reference</span>
                  </div>
                  <button @click="copyReference" 
                          class="text-sm font-medium text-[#FF579A] hover:text-pink-600 transition-colors">
                    Copy
                  </button>
                </div>
                <p class="text-2xl font-bold text-gray-900 font-mono tracking-tight">{{ bookingReference }}</p>
              </div>

              <!-- Amount Card -->
              <div class="group bg-gray-50 hover:bg-white border border-gray-200 hover:border-emerald-200 rounded-xl p-6 transition-all duration-300">
                <div class="flex items-center space-x-3 mb-4">
                  <div class="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center">
                    <span class="text-xl text-emerald-600">💰</span>
                  </div>
                  <span class="text-sm font-semibold text-gray-500 uppercase tracking-wider">Amount Paid</span>
                </div>
                <p class="text-3xl font-bold text-emerald-700">₱{{ formattedAmount }}</p>
                <p class="text-[11px] text-gray-500 mt-2">Including taxes & fees</p>
              </div>

              <!-- Payment Card -->
              <div class="group bg-gray-50 hover:bg-white border border-gray-200 hover:border-blue-200 rounded-xl p-6 transition-all duration-300">
                <div class="flex items-center space-x-3 mb-4">
                  <div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                    <span class="text-xl text-blue-600">🆔</span>
                  </div>
                  <span class="text-sm font-semibold text-gray-500 uppercase tracking-wider">Payment ID</span>
                </div>
                <p class="text-xl font-bold text-gray-900 font-mono">{{ paymentId }}</p>
                <p class="text-sm text-gray-500 mt-2">Transaction complete</p>
              </div>

              <!-- Status Card -->
              <div class="group bg-gray-50 hover:bg-white border border-gray-200 hover:border-emerald-200 rounded-xl p-6 transition-all duration-300">
                <div class="flex items-center space-x-3 mb-4">
                  <div class="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center">
                    <span class="text-xl text-emerald-600">✅</span>
                  </div>
                  <span class="text-sm font-semibold text-gray-500 uppercase tracking-wider">Status</span>
                </div>
                <div class="inline-flex items-center space-x-2 px-4 py-2 bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-100">
                  <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                  <span class="font-semibold">Confirmed</span>
                </div>
                <p class="text-sm text-gray-500 mt-2">Seats reserved</p>
              </div>
            </div>
          </div>

          <!-- Timeline -->
          <div class="bg-white rounded-2xl  border border-gray-300 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-8">Next Steps</h2>
            
            <div class="space-y-8">
              <div v-for="(step, index) in timelineSteps" :key="index" class="flex items-start space-x-6 group">
                <!-- Step Number -->
                <div class="relative">
                  <div class="w-14 h-14 bg-gradient-to-br from-pink-50 to-white border border-pink-100 rounded-xl flex items-center justify-center">
                    <span class="text-xl font-bold text-[#FF579A]">{{ index + 1 }}</span>
                  </div>
                  <!-- Connector Line (except last) -->
                  <div v-if="index < timelineSteps.length - 1" 
                       class="absolute left-1/2 top-full w-0.5 h-8 bg-gradient-to-b from-pink-200 to-transparent -translate-x-1/2"></div>
                </div>
                
                <!-- Content -->
                <div class="flex-1 pt-1">
                  <h3 class="text-lg font-semibold text-gray-900 mb-2 group-hover:text-[#FF579A] transition-colors">
                    {{ step.title }}
                  </h3>
                  <p class="text-gray-600">{{ step.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="space-y-8">
          <!-- Quick Actions -->
          <div class="bg-white rounded-2xl  border border-gray-300 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
            
            <div class="space-y-4">
              <button @click="goToDashboard" 
                      class="w-full group flex items-center justify-between p-5 bg-gradient-to-r from-pink-50 to-white hover:from-[#FF579A] hover:to-pink-500 border border-pink-100 hover:border-transparent rounded-xl transition-all duration-300">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-white group-hover:bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-2xl text-[#FF579A] group-hover:text-white">📋</span>
                  </div>
                  <span class="text-lg font-semibold text-gray-900 group-hover:text-white">Back to Dashboard</span>
                </div>
                <span class="text-xl text-gray-400 group-hover:text-white group-hover:translate-x-2 transition-transform">→</span>
              </button>

              <button @click="goHome" 
                      class="w-full group flex items-center justify-between p-5 bg-gradient-to-r from-gray-50 to-white hover:from-gray-900 hover:to-gray-800 border border-gray-200 hover:border-transparent rounded-xl transition-all duration-300">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-white group-hover:bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-2xl text-gray-700 group-hover:text-white">✈️</span>
                  </div>
                  <span class="text-lg font-semibold text-gray-900 group-hover:text-white">New Booking</span>
                </div>
                <span class="text-xl text-gray-400 group-hover:text-white group-hover:rotate-12 transition-transform">→</span>
              </button>
            </div>
          </div>

          <!-- Support Card -->
          <div class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl  p-8 text-white">
            <div class="flex items-start space-x-4 mb-6">
              <div class="w-14 h-14 bg-white/10 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <span class="text-3xl">🆘</span>
              </div>
              <div>
                <h3 class="text-xl font-bold mb-1">Need Help?</h3>
                <p class="text-gray-300 text-sm">24/7 Customer Support</p>
              </div>
            </div>

            <div class="space-y-4">
              <a href="tel:+63288558888" 
                 class="flex items-center space-x-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-all duration-200 group">
                <div class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center group-hover:bg-white/20">
                  <span class="text-lg">📞</span>
                </div>
                <div>
                  <p class="font-medium">(02) 8855-8888</p>
                  <p class="text-sm text-gray-400">Phone Support</p>
                </div>
              </a>

              <a href="mailto:support@philippineairlines.com" 
                 class="flex items-center space-x-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-all duration-200 group">
                <div class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center group-hover:bg-white/20">
                  <span class="text-lg">✉️</span>
                </div>
                <div>
                  <p class="font-medium">Email Support</p>
                  <p class="text-sm text-gray-400">support@philippineairlines.com</p>
                </div>
              </a>

              <a href="#" 
                 class="flex items-center space-x-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-all duration-200 group">
                <div class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center group-hover:bg-white/20">
                  <span class="text-lg">💬</span>
                </div>
                <div>
                  <p class="font-medium">Live Chat</p>
                  <p class="text-sm text-gray-400">Instant messaging support</p>
                </div>
              </a>
            </div>
          </div>

          <!-- Share Card -->
          <div class="bg-white rounded-2xl  border border-gray-100 p-8">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Share Booking</h3>
            <p class="text-gray-600 text-sm mb-6">Let friends and family know about your travel plans</p>
            
            <div class="grid grid-cols-2 gap-3">
              <button class="h-12 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
                Facebook
              </button>
              <button class="h-12 bg-black hover:bg-gray-900 text-white rounded-lg font-medium transition-colors">
                Twitter
              </button>
              <button class="h-12 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors">
                WhatsApp
              </button>
              <button @click="copyBookingLink" 
                      class="h-12 bg-gradient-to-r from-[#FF579A] to-pink-500 hover:from-pink-600 hover:to-pink-400 text-white rounded-lg font-medium transition-all">
                Copy Link
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-12 pt-8 border-t border-gray-200">
        <div class="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-br from-[#FF579A] to-pink-500 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-lg">PA</span>
            </div>
            <div>
              <p class="text-lg font-semibold text-gray-900">Philippine Airlines</p>
              <p class="text-sm text-gray-600">Experience premium air travel</p>
            </div>
          </div>
          
          <div class="flex items-center space-x-6">
            <div class="flex items-center space-x-2">
              <span class="text-gray-500">🔒</span>
              <span class="text-sm text-gray-600">Secure Booking</span>
            </div>
            <div class="w-0.5 h-6 bg-gray-200"></div>
            <div class="flex items-center space-x-2">
              <span class="text-gray-500">✅</span>
              <span class="text-sm text-gray-600">Verified Payment</span>
            </div>
            <div class="w-0.5 h-6 bg-gray-200"></div>
            <div class="flex items-center space-x-2">
              <span class="text-gray-500">🛡️</span>
              <span class="text-sm text-gray-600">Data Protected</span>
            </div>
          </div>
        </div>
        
        <div class="mt-8 text-center">
          <p class="text-gray-600">
            Thank you for flying with Philippine Airlines. 
            <span class="font-medium text-[#FF579A]">Have a safe and pleasant journey!</span>
          </p>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 translate-y-2"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div v-if="showToast" 
           class="fixed bottom-6 right-6 bg-gradient-to-r from-[#FF579A] to-pink-500 text-white px-6 py-4 rounded-xl  flex items-center space-x-3 max-w-sm z-50">
        <div class="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <span class="font-medium">{{ toastMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';

const route = useRoute();
const router = useRouter();
const bookingStore = useBookingStore();

const bookingReference = ref('PAL' + Math.random().toString(36).substr(2, 9).toUpperCase());
const paymentId = ref('PAY' + Math.random().toString(36).substr(2, 12).toUpperCase());
const amountPaid = ref(12500.50);
const showToast = ref(false);
const toastMessage = ref('');

const timelineSteps = [
  {
    title: 'Check Email',
    description: 'Your e-ticket and confirmation have been sent to your registered email address.'
  },
  {
    title: 'Online Check-in',
    description: 'Check-in opens 24 hours before departure. Save time at the airport.'
  },
  {
    title: 'Prepare Documents',
    description: 'Have your passport/ID, e-ticket, and any required travel documents ready.'
  },
  {
    title: 'Airport Arrival',
    description: 'Arrive 2-3 hours before departure for domestic/international flights.'
  }
];

const formattedAmount = computed(() => {
  return amountPaid.value.toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
});

onMounted(() => {
  const query = route.query;
  
  if (query.ref) {
    bookingReference.value = query.ref;
    localStorage.setItem('last_booking_ref', query.ref);
  }
  
  if (query.payment_id) {
    paymentId.value = query.payment_id;
  }
  
  if (query.amount) {
    amountPaid.value = parseFloat(query.amount);
  }
  
  if (!bookingReference.value) {
    bookingReference.value = localStorage.getItem('last_booking_ref') || 'PAL' + Math.random().toString(36).substr(2, 9).toUpperCase();
  }
});

const copyReference = () => {
  navigator.clipboard.writeText(bookingReference.value);
  showToastMessage('Booking reference copied to clipboard');
};

const copyBookingLink = () => {
  const link = `${window.location.origin}/booking/${bookingReference.value}`;
  navigator.clipboard.writeText(link);
  showToastMessage('Booking link copied to clipboard');
};

const showToastMessage = (message) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

const goToDashboard = () => {
  showToastMessage('Returning to dashboard...');
  // Clear activity code validation so the student can access their dashboard
  bookingStore.clearActivityCodeValidation();
  bookingStore.resetBooking();
  router.push({ name: 'StudentDashboard' });
};

const downloadTicket = () => {
  showToastMessage('Preparing your e-ticket for download...');
};

const addToCalendar = () => {
  showToastMessage('Adding flight details to calendar...');
};

const goHome = () => {
  showToastMessage('Starting new booking...');
  // Keep the same session if they want new booking, but reset selection
  bookingStore.resetBooking();
  router.push({ name: 'Home' });
};
</script>

<style scoped>
/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f8fafc;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #FF579A, #FF85B3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #FF85B3, #FFAEC8);
}

/* Smooth transitions */
* {
  scroll-behavior: smooth;
}

/* Gradient text animation */
@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.text-gradient-animate {
  background: linear-gradient(45deg, #FF579A, #FF85B3, #FFAEC8, #FF579A);
  background-size: 400% 400%;
  animation: gradientShift 3s ease infinite;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>