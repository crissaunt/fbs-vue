<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 p-4 md:p-8 relative overflow-hidden">
    <!-- Background Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 right-0 w-1/3 h-1/3 bg-gradient-to-br from-[#FF579A]/5 to-transparent rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-1/3 h-1/3 bg-gradient-to-tr from-gray-400/5 to-transparent rounded-full blur-3xl"></div>
    </div>

    <!-- Main Container -->
    <div class="relative max-w-6xl mx-auto">
      <!-- Header -->
      

      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-sm  border border-gray-300 p-12 text-center">
        <div class="relative inline-flex mb-6">
          <div class="w-20 h-20 border-4 border-pink-100 rounded-full"></div>
          <div class="absolute inset-0 w-20 h-20 border-4 border-[#FF579A] border-t-transparent rounded-full animate-spin"></div>
        </div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ loadingMessage }}</h3>
        <p class="text-gray-600">Please wait while we process your request</p>
      </div>

      <!-- Session Expired -->
      <div v-else-if="!isSessionValid" class="bg-white rounded-sm  border border-gray-300 p-12 text-center">
        <div class="w-20 h-20 bg-gradient-to-br from-amber-50 to-amber-100 rounded-sm flex items-center justify-center mx-auto mb-6">
          <span class="text-3xl text-amber-500">⏰</span>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-3">Session Expired</h3>
        <p class="text-gray-600 mb-8 max-w-md mx-auto">
          Your booking session has expired. Please restart your booking process to continue.
        </p>
        <button @click="restartBooking" 
                class="bg-gradient-to-r from-gray-900 to-gray-800 hover:from-black hover:to-gray-900 text-white px-8 py-3 rounded-sm font-semibold transition-all duration-300  hover:shadow-xl">
          Start New Booking
        </button>
      </div>

      <!-- Main Content -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column - Booking Summary -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Amount Card -->
          <div class="bg-white rounded-sm  border border-gray-300 p-8">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-2xl font-bold text-gray-900">Payment Summary</h2>
              <span class="px-4 py-1.5 bg-green-50 text-green-700 rounded-full text-sm font-semibold border border-green-100">
                Active Session
              </span>
            </div>

            <div class="bg-gradient-to-r from-gray-50 to-white border border-gray-200 rounded-sm p-8 mb-8">
              <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Total Amount</p>
              <p class="text-5xl font-bold text-gray-900">₱ {{ totalAmount.toLocaleString() }}</p>
              <p class="text-gray-500 text-sm mt-2">Inclusive of all taxes and fees</p>
            </div>

            <!-- Booking Details -->
            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gray-50 rounded-sm p-5">
                  <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Booking Reference</p>
                  <p class="text-xl font-bold text-gray-900 font-mono">{{ bookingReference || 'N/A' }}</p>
                </div>
                <div class="bg-gray-50 rounded-sm p-5">
                  <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Status</p>
                  <div class="inline-flex items-center space-x-2 px-4 py-2 bg-amber-50 text-amber-700 rounded-sm">
                    <div class="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
                    <span class="font-semibold">{{ bookingStatus }}</span>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gray-50 rounded-sm p-5">
                  <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Passenger</p>
                  <p class="text-lg font-semibold text-gray-900">{{ contactName }}</p>
                </div>
                <div class="bg-gray-50 rounded-sm p-5">
                  <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Trip Type</p>
                  <div class="inline-flex items-center space-x-2">
                    <span class="px-4 py-1.5 bg-blue-50 text-blue-700 rounded-sm font-semibold">
                      {{ tripTypeLabel }}
                    </span>
                    <span v-if="bookingStore.isRoundTrip" class="text-blue-500">🔄</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Flight Details -->
          <div v-if="hasFlightInfo" class="bg-white rounded-sm  border border-gray-300 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Flight Details</h2>
            
            <div class="space-y-6">
              <!-- Outbound Flight -->
              <div v-if="bookingStore.selectedOutbound" class="bg-gradient-to-r from-blue-50 to-white border border-blue-100 rounded-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 bg-blue-100 rounded-sm flex items-center justify-center">
                      <span class="text-xl text-blue-600">✈️</span>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider">Departure</p>
                      <p class="text-lg font-bold text-gray-900">{{ bookingStore.selectedOutbound.origin }} → {{ bookingStore.selectedOutbound.destination }}</p>
                    </div>
                  </div>
                  <span class="px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
                    {{ bookingStore.selectedOutbound.flight_number }}
                  </span>
                </div>
              </div>

              <!-- Return Flight -->
              <div v-if="bookingStore.selectedReturn" class="bg-gradient-to-r from-emerald-50 to-white border border-emerald-100 rounded-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 bg-emerald-100 rounded-sm flex items-center justify-center">
                      <span class="text-xl text-emerald-600">🔄</span>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider">Return</p>
                      <p class="text-lg font-bold text-gray-900">{{ bookingStore.selectedReturn.origin }} → {{ bookingStore.selectedReturn.destination }}</p>
                    </div>
                  </div>
                  <span class="px-4 py-1.5 bg-emerald-100 text-emerald-700 rounded-full text-sm font-semibold">
                    {{ bookingStore.selectedReturn.flight_number }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column - Payment -->
        <div class="space-y-8">
          <!-- Payment Methods -->
          <div class="bg-white rounded-sm  border border-gray-300 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Payment Methods</h2>
            <p class="text-gray-600 mb-8 text-[11px]">
              You'll be redirected to our secure payment partner to complete your transaction. All major payment methods are accepted.
            </p>

            <div class="space-y-4">
              <!-- PayMongo Multi-method -->
              <button @click="handlePayMongoCheckout" 
                      class="w-full group flex items-center justify-between p-5 bg-gradient-to-r from-pink-50 to-white hover:from-[#FF579A] hover:to-pink-500 border border-pink-100 hover:border-transparent rounded-sm transition-all duration-300">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-white group-hover:bg-white/20 rounded-sm flex items-center justify-center">
                    <span class="text-2xl text-[#FF579A] group-hover:text-white">💳</span>
                  </div>
                  <div class="text-left">
                    <p class="font-semibold text-gray-900 group-hover:text-white">All Payment Methods</p>
                    <p class="text-sm text-gray-600 group-hover:text-white/80">GCash, Maya, Credit/Debit Cards</p>
                  </div>
                </div>
                <span class="text-xl text-gray-400 group-hover:text-white group-hover:translate-x-2 transition-transform">→</span>
              </button>

              <!-- GCash Direct -->
              <button v-if="paymentService.isPayMongoConfigured()" 
                      @click="handleDirectGCash"
                      class="w-full group flex items-center justify-between p-5 bg-gradient-to-r from-emerald-50 to-white hover:from-emerald-600 hover:to-emerald-500 border border-emerald-100 hover:border-transparent rounded-sm transition-all duration-300">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-white group-hover:bg-white/20 rounded-sm flex items-center justify-center">
                    <span class="text-2xl text-emerald-600 group-hover:text-white">📱</span>
                  </div>
                  <div class="text-left">
                    <p class="font-semibold text-gray-900 group-hover:text-white">GCash Direct</p>
                    <p class="text-sm text-gray-600 group-hover:text-white/80">Pay directly via GCash wallet</p>
                  </div>
                </div>
                <span class="text-xl text-gray-400 group-hover:text-white group-hover:translate-x-2 transition-transform">→</span>
              </button>
            </div>

            <!-- Payment Providers -->
            <!-- <div class="mt-8 pt-8 border-t border-gray-200">
              <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Secure Payment Partners</p>
              <div class="grid grid-cols-4 gap-4">
                <div class="h-12 bg-gray-100 rounded-sm flex items-center justify-center">
                  <span class="text-gray-600 font-bold">GCash</span>
                </div>
                <div class="h-12 bg-gray-100 rounded-sm flex items-center justify-center">
                  <span class="text-gray-600 font-bold">Maya</span>
                </div>
                <div class="h-12 bg-gray-100 rounded-sm flex items-center justify-center">
                  <span class="text-gray-600 font-bold">Visa</span>
                </div>
                <div class="h-12 bg-gray-100 rounded-sm flex items-center justify-center">
                  <span class="text-gray-600 font-bold">Master</span>
                </div>
              </div>
            </div> -->
          </div>

          <!-- Action Buttons -->
          <div class="space-y-4">
             <button @click="handlePayMongoCheckout" 
                    :disabled="loading || !bookingId"
                    class="w-full py-3.5 bg-gradient-to-r from-[#FF579A] to-pink-500 hover:from-pink-600 hover:to-pink-400 text-white rounded-sm font-semibold transition-all duration-300  hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed">
              Proceed to Secure Payment
            </button>
            <button @click="goBack" 
                    class="w-full py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-sm font-semibold transition-colors duration-200 border border-gray-200">
              Back to Review
            </button>
            
           
          </div>

          <!-- Help Section -->
          <div class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-sm p-6 text-white">
            <h4 class="font-semibold mb-4">Need Help?</h4>
            <div class="space-y-3">
              <a href="tel:+63288558888" 
                 class="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors">
                <span class="text-lg">📞</span>
                <span>(02) 8855-8888</span>
              </a>
              <a href="mailto:support@philippineairlines.com" 
                 class="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors">
                <span class="text-lg">✉️</span>
                <span>Payment Support</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Debug Info (Development Only) -->
      <!-- <div v-if="showDebugInfo" class="mt-8 p-6 bg-gray-900 rounded-sm">
        <p class="text-sm font-mono text-gray-300 mb-2">Debug Information:</p>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p class="text-xs text-gray-500">Booking ID</p>
            <p class="text-sm text-white">{{ bookingId || 'None' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Session Valid</p>
            <p :class="isSessionValid ? 'text-green-400' : 'text-red-400'" class="text-sm">{{ isSessionValid }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Total Amount</p>
            <p class="text-sm text-white">₱{{ totalAmount.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Trip Type</p>
            <p class="text-sm text-white">{{ tripTypeLabel }}</p>
          </div>
        </div>
      </div> -->
    </div>

    <!-- Toast Notification -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 translate-y-2"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div v-if="showToast" 
           class="fixed bottom-6 right-6 bg-gradient-to-r from-[#FF579A] to-pink-500 text-white px-6 py-4 rounded-sm shadow-xl flex items-center space-x-3 max-w-sm z-50">
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
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import api from '@/services/booking/api';
import { paymentService } from '@/services/booking/paymentService';

const bookingStore = useBookingStore();
const router = useRouter();

const loading = ref(false);
const loadingMessage = ref("");
const showDebugInfo = ref(process.env.NODE_ENV === 'development');
const showToast = ref(false);
const toastMessage = ref("");

// Computed properties
const bookingId = computed(() => bookingStore.booking_id);
const bookingReference = computed(() => bookingStore.booking_reference);
const bookingStatus = computed(() => bookingStore.booking_status || 'pending');
const tripTypeLabel = computed(() => bookingStore.isRoundTrip ? 'Round Trip' : 'One Way');

const contactName = computed(() => {
  const info = bookingStore.contactInfo;
  return `${info.title || ''} ${info.firstName || ''} ${info.lastName || ''}`.trim() || 'Not specified';
});

const totalAmount = computed(() => {
  return bookingStore.booking_total > 0 
    ? bookingStore.booking_total 
    : bookingStore.grandTotal || 0;
});

const hasFlightInfo = computed(() => {
  return bookingStore.selectedOutbound || bookingStore.selectedReturn;
});

const isSessionValid = computed(() => {
  if (!bookingStore.sessionExpiry) return false;
  return Date.now() < bookingStore.sessionExpiry;
});

/**
 * Show toast message
 */
const showToastMessage = (message, duration = 3000) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, duration);
};

/**
 * Restores booking data from localStorage if store is empty
 */
const restoreBookingData = () => {
  if (bookingStore.booking_id) return;
  
  try {
    const savedBooking = localStorage.getItem('current_booking');
    if (savedBooking) {
      const bookingData = JSON.parse(savedBooking);
      
      const bookingAge = Date.now() - new Date(bookingData.created_at).getTime();
      const thirtyMinutes = 30 * 60 * 1000;
      
      if (bookingAge < thirtyMinutes) {
        bookingStore.saveBookingConfirmation({
          booking_id: bookingData.id,
          booking_reference: bookingData.reference,
          status: bookingData.status,
          total_amount: bookingData.total
        });
        
        bookingStore.sessionExpiry = Date.now() + (15 * 60 * 1000);
      } else {
        localStorage.removeItem('current_booking');
      }
    }
  } catch (error) {
    console.error('Error restoring booking data:', error);
  }
};

/**
 * Go back to review page
 */
const goBack = () => {
  router.back();
};

/**
 * Restarts the booking process
 */
const restartBooking = () => {
  bookingStore.resetBooking();
  localStorage.removeItem('current_booking');
  router.push({ name: 'SearchFlights' });
};

/**
 * Handle PayMongo Checkout
 */
const handlePayMongoCheckout = async () => {
  if (!isSessionValid.value) {
    showToastMessage("Booking session expired. Please restart your booking.");
    restartBooking();
    return;
  }

  if (!bookingStore.booking_id) {
    try {
      showToastMessage("No booking ID found. Please complete your booking details first.");
      goBack();
      return;
    } catch (error) {
      showToastMessage(`Failed to create booking: ${error.message}`);
      return;
    }
  }

  loading.value = true;
  loadingMessage.value = "Creating secure payment session...";

  try {
    const paymentData = {
      amount: totalAmount.value,
      booking_id: bookingStore.booking_id,
      customer_email: bookingStore.contactInfo.email || 'test@example.com',
      customer_name: `${bookingStore.contactInfo.firstName || 'Customer'} ${bookingStore.contactInfo.lastName || ''}`.trim(),
      customer_phone: bookingStore.contactInfo.phone || '09171234567'
    };

    const response = await api.post('create-checkout-session/', paymentData);

    if (response.data && response.data.success === true && response.data.checkout_url) {
      localStorage.setItem('payment_session', JSON.stringify({
        checkout_url: response.data.checkout_url,
        booking_id: bookingStore.booking_id,
        booking_reference: bookingStore.booking_reference,
        amount: totalAmount.value,
        timestamp: Date.now()
      }));

      loading.value = false;
      loadingMessage.value = "";
      
      setTimeout(() => {
        window.location.href = response.data.checkout_url;
      }, 500);
      
    } else {
      let errorMsg = 'Failed to create checkout session';
      
      if (response.data && response.data.error) {
        if (typeof response.data.error === 'string') {
          errorMsg = response.data.error;
        } else if (typeof response.data.error === 'object') {
          errorMsg = JSON.stringify(response.data.error);
        }
      } else if (response.data && response.data.message) {
        errorMsg = response.data.message;
      }
      
      showToastMessage(`Payment setup failed: ${errorMsg}`);
      loading.value = false;
    }

  } catch (error) {
    console.error("PayMongo Checkout Error:", error);
    
    let errorMsg = "Payment initialization failed.";
    
    if (error.response) {
      if (error.response.status === 400) {
        if (error.response.data?.error) {
          if (typeof error.response.data.error === 'string') {
            errorMsg = error.response.data.error;
          } else if (typeof error.response.data.error === 'object') {
            errorMsg = 'PayMongo API error: ' + JSON.stringify(error.response.data.error);
          }
        }
      } else if (error.response.status === 404) {
        errorMsg = "Payment service endpoint not found.";
      } else if (error.response.data?.message) {
        errorMsg = error.response.data.message;
      }
    } else if (error.request) {
      errorMsg = "Network error. Please check your internet connection.";
    } else {
      errorMsg = error.message;
    }
    
    showToastMessage(`Payment Error: ${errorMsg}`);
    loading.value = false;
  }
};

/**
 * Handle Direct GCash Payment
 */
const handleDirectGCash = async () => {
  if (!paymentService.isPayMongoConfigured()) {
    showToastMessage("GCash payment is not available at the moment.");
    return;
  }

  loading.value = true;
  loadingMessage.value = "Preparing GCash payment...";

  try {
    const result = await paymentService.processGcashPayment({
      amount: totalAmount.value,
      booking_id: bookingStore.booking_id,
      booking_reference: bookingStore.booking_reference,
      contactInfo: bookingStore.contactInfo
    }, {
      name: `${bookingStore.contactInfo.firstName} ${bookingStore.contactInfo.lastName}`,
      email: bookingStore.contactInfo.email,
      phone: bookingStore.contactInfo.phone
    });

    if (result.success && result.next_action?.redirect?.url) {
      window.location.href = result.next_action.redirect.url;
    } else {
      throw new Error(result.error || 'GCash payment failed');
    }

  } catch (error) {
    console.error('GCash payment error:', error);
    showToastMessage(`GCash Error: ${error.message}`);
    loading.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  restoreBookingData();
  checkPaymentCallback();
});

/**
 * Check for payment callback parameters
 */
const checkPaymentCallback = () => {
  const urlParams = new URLSearchParams(window.location.search);
  
  const success = urlParams.get('success');
  const error = urlParams.get('error');
  const bookingId = urlParams.get('booking_id');
  
  if (success === 'true' && bookingId) {
    showToastMessage('Payment successful! Your booking has been confirmed.');
    window.history.replaceState({}, document.title, window.location.pathname);
  } else if (error) {
    showToastMessage(`Payment failed: ${decodeURIComponent(error)}`);
    window.history.replaceState({}, document.title, window.location.pathname);
  }
};

onUnmounted(() => {
  // Clean up
});
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

/* Pulse animation for status */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Button hover effects */
button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Card hover effects */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}
</style>