<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { paymentPollingService } from '@/services/booking/paymentPollingService';
import api from '@/services/booking/api';
import { useNotificationStore } from '@/stores/notification';
import { useModalStore } from '@/stores/modal';

const route = useRoute();
const router = useRouter();
const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();
const modalStore = useModalStore();

const loading = ref(true);
const errorMessage = ref('');
const pollingCount = ref(0);
const maxPollingAttempts = 15;
const pollingInterval = ref(null);
const processingStatus = ref('');
const showIncompleteState = ref(false);
const hasRedirected = ref(false); // Guard against double-redirects
const isPolling = ref(false); // Mutex lock

// Get parameters from URL
const urlParams = new URLSearchParams(window.location.search);
const paymentSuccess = urlParams.get('payment_success');
const sessionIdFromUrl = urlParams.get('session_id');
const bookingId = urlParams.get('booking_id') || bookingStore.booking_id;
const paymentIntentId = urlParams.get('payment_intent_id');

console.log('Payment callback parameters:', { 
  paymentSuccess, 
  bookingId, 
  sessionId: sessionIdFromUrl,
  paymentIntentId 
});

const getLoadingMessage = () => {
  const messages = [
    "Verifying your payment...",
    "Confirming transaction details...",
    "Processing your booking...",
    "Almost there...",
    "Finalizing confirmation..."
  ];
  return messages[pollingCount.value % messages.length];
};

// Poll payment status - REDIRECTS TO SUCCESS PAGE WHEN PAID
const pollPaymentStatus = async (bookingId) => {
  // Stop if we've already redirected or if a poll is currently running
  if (hasRedirected.value || isPolling.value) {
    if (hasRedirected.value) clearInterval(pollingInterval.value);
    return;
  }
  
  isPolling.value = true;

  if (pollingCount.value >= maxPollingAttempts) {
    clearInterval(pollingInterval.value);
    showIncompleteState.value = true;
    loading.value = false;
    isPolling.value = false;
    return;
  }

  pollingCount.value++;
  processingStatus.value = `Checking payment status (Attempt ${pollingCount.value}/${maxPollingAttempts})...`;

  try {
    console.log(`Polling attempt ${pollingCount.value} for booking ${bookingId}`);
    
    // Use the new polling service
    const result = await paymentPollingService.checkPaymentStatusOnce(bookingId);
    
    console.log('Polling result:', result);

    if (result.paid === true) {
      // Payment confirmed! Navigate to success page
      clearInterval(pollingInterval.value);
      hasRedirected.value = true;
      
      // Prepare data for success page
      const bookingReference = result.data.booking_reference || `CSUCC${bookingId.toString().padStart(8, '0')}`;
      const paymentId = result.data.payment_id;
      const amount = bookingStore.booking_total || bookingStore.grandTotal;
      
      console.log('Payment successful! Navigating to success page with:', {
        ref: bookingReference,
        payment_id: paymentId,
        amount: amount
      });
      
      // Defer clearing the booking store until the user leaves the success page
      // This prevents the router guard from redirecting to dashboard prematurely
      // bookingStore.clearActivityCodeValidation();
      // bookingStore.resetBooking();
      // localStorage.removeItem('current_booking');
      // localStorage.removeItem('payment_session');
      
      // Navigate to success page
      router.push({
        name: 'BookingSuccess',
        query: {
          ref: bookingReference,
          payment_id: paymentId,
          amount: amount,
          booking_id: bookingId
        }
      });
      
    } else if (result.success === false) {
      // Error from backend
      clearInterval(pollingInterval.value);
      errorMessage.value = result.error || 'Payment verification failed.';
      loading.value = false;
    }
    // If paid is false, continue polling
    
  } catch (error) {
    console.error('Polling error:', error);
    processingStatus.value = 'Connection error, retrying...';
  } finally {
    isPolling.value = false;
  }
};

const startPolling = (bookingId) => {
  console.log(`Starting polling for booking ${bookingId}`);
  pollingCount.value = 0;
  processingStatus.value = 'Starting payment verification...';
  
  // Start immediate poll
  pollPaymentStatus(bookingId);
  
  // Set up interval for subsequent polls
  pollingInterval.value = setInterval(() => {
    pollPaymentStatus(bookingId);
  }, 2000);
};

const verifyPaymentWithSession = async () => {
  if (!sessionIdFromUrl || sessionIdFromUrl.includes('{')) {
    console.log('Invalid session ID, skipping verification');
    return false;
  }
  
  try {
    console.log(`Verifying payment with session: ${sessionIdFromUrl}`);
    
    const response = await api.post('verify-session-payment/', {
      booking_id: bookingId,
      session_id: sessionIdFromUrl
    });
    
    console.log('Session verification response:', response.data);
    
    if (response.data.success) {
      return {
        success: true,
        data: response.data
      };
    }
  } catch (error) {
    console.error('Session verification error:', error);
  }
  
  return { success: false };
};

onMounted(async () => {
  // Check for booking ID
  if (!bookingId) {
    errorMessage.value = 'No booking found. Please start a new booking.';
    loading.value = false;
    return;
  }

  // Check if payment was successful
  if (paymentSuccess === 'true') {
    console.log('Payment reported as successful, starting verification...');
    
    // Try to verify with session ID if available
    if (sessionIdFromUrl && !sessionIdFromUrl.includes('{')) {
      console.log(`Got valid session ID: ${sessionIdFromUrl}`);
      processingStatus.value = 'Verifying payment with session ID...';
      
      // Try direct verification first with the correct endpoint
      try {
        const verifyResponse = await api.post('verify-session-payment/', {
          booking_id: bookingId,
          session_id: sessionIdFromUrl,
          payment_success: 'true'
        });
        
        console.log('Direct verification response:', verifyResponse.data);
        
        if (verifyResponse.data.success) {
          // Payment processed successfully! Navigate to success page
          const bookingReference = verifyResponse.data.booking_reference || `CSUCC${bookingId.toString().padStart(8, '0')}`;
          const paymentId = verifyResponse.data.payment_id;
          const amount = bookingStore.booking_total || bookingStore.grandTotal;
          
          console.log('Direct verification successful! Navigating to success page');
          
          // Defer clearing the booking store until the user leaves the success page
          // bookingStore.clearActivityCodeValidation();
          // bookingStore.resetBooking();
          // localStorage.removeItem('current_booking');
          // localStorage.removeItem('payment_session');
          
          // Navigate to success page
          router.push({
            name: 'BookingSuccess',
            query: {
              ref: bookingReference,
              payment_id: paymentId,
              amount: amount,
              booking_id: bookingId
            }
          });
          
          return;
        } else {
          console.log('Direct verification failed, session status:', verifyResponse.data.session_status);
        }
      } catch (error) {
        console.log('Direct verification failed, falling back to polling:', error);
      }
    }
    
    // If direct verification fails, fall back to polling
    processingStatus.value = 'Payment verification needed, starting polling...';
    startPolling(bookingId);
    
  } else if (paymentSuccess === 'false') {
    errorMessage.value = 'Payment was cancelled or failed.';
    loading.value = false;
  } else {
    // No success parameter - maybe direct access
    console.log('No success parameter, checking payment status...');
    processingStatus.value = 'Checking payment status...';
    startPolling(bookingId);
  }
});

onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
  }
});

const goHome = () => {
  bookingStore.resetBooking();
  localStorage.removeItem('current_booking');
  localStorage.removeItem('payment_session');
  router.push({ name: 'Home' });
};

const retryPayment = () => {
  if (bookingStore.booking_id) {
    router.push({
      name: 'Payment',
      query: { 
        bookingId: bookingStore.booking_id,
        retry: true 
      }
    });
  } else {
    router.push({ name: 'SearchFlights' });
  }
};

const cancelBooking = async () => {
  const confirmed = await modalStore.confirm({
    title: 'Cancel Booking?',
    message: 'Are you sure you want to cancel this booking? This action cannot be undone.',
    confirmText: 'Yes, Cancel',
    cancelText: 'No, Keep'
  });

  if (confirmed) {
    try {
      await api.post(`cancel-booking/${bookingStore.booking_id}/`);
      bookingStore.resetBooking();
      localStorage.removeItem('current_booking');
      localStorage.removeItem('payment_session');
      router.push({ name: 'Home' });
    } catch (error) {
      notificationStore.error('Failed to cancel booking: ' + error.message);
    }
  }
};
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-pink-50 via-white to-rose-50 flex justify-center items-center p-5">
    
    <!-- Loading State - SHOWS WHILE POLLING -->
    <div v-if="loading" class="bg-white rounded-3xl border border-gray-100 shadow-2xl p-8 sm:p-12 text-center max-w-lg w-full ring-1 ring-black/5">
      <div class="relative w-16 h-16 mx-auto mb-8">
        <div class="absolute inset-0 border-4 border-pink-100 rounded-full"></div>
        <div class="absolute inset-0 border-4 border-pink-500 rounded-full animate-spin border-t-transparent shadow-lg shadow-pink-200"></div>
      </div>
      
      <p class="text-lg font-semibold text-gray-800 mb-2">{{ processingStatus }}</p>
      
      <p v-if="pollingCount < maxPollingAttempts" class="text-gray-600 mb-4">
        {{ getLoadingMessage() }}
      </p>
      <p v-else class="text-gray-600 mb-4">
        Taking longer than expected... Still verifying your payment.
      </p>
      
      <div v-if="pollingCount > 0" class="mt-4">
        <small class="text-gray-500 text-sm">Attempt {{ pollingCount }} of {{ maxPollingAttempts }}</small>
      </div>

      <div class="mt-6 pt-6 border-t border-gray-200">
        <p class="text-sm text-gray-500">
          Please do not close this window while we process your payment.
        </p>
      </div>
    </div>

    <!-- Incomplete Payment State -->
    <div v-else-if="showIncompleteState" class="bg-white rounded-3xl border border-gray-100 shadow-2xl p-8 sm:p-12 text-center max-w-2xl w-full">
      <div class="w-20 h-20 bg-rose-50 border border-rose-100 rounded-2xl flex items-center justify-center mx-auto mb-8 text-4xl shadow-inner scale-110">
        🔄
      </div>
      
      <h1 class="text-3xl font-black text-gray-900 mb-3 tracking-tight">Payment Not Completed</h1>
      
      <p class="text-[15px] text-gray-500 font-medium mb-8 max-w-lg mx-auto">
        It looks like the payment process was interrupted. Don't worry, your booking details are saved!
      </p>
      
      <div class="bg-gray-50/50 border border-gray-100 rounded-2xl p-6 text-left mb-8 space-y-4">
        <p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Next Steps</p>
        <ul class="space-y-3">
          <li class="flex items-start gap-3">
            <div class="mt-1 w-1.5 h-1.5 rounded-full bg-pink-400 shrink-0"></div>
            <p class="text-sm font-medium text-gray-600">The transaction was cancelled or timed out during the checkout process.</p>
          </li>
          <li class="flex items-start gap-3">
            <div class="mt-1 w-1.5 h-1.5 rounded-full bg-pink-400 shrink-0"></div>
            <p class="text-sm font-medium text-gray-600">You can safely retry the payment now to confirm your seats immediately.</p>
          </li>
        </ul>
      </div>
      
      <div class="bg-white border border-gray-100 rounded-2xl p-6 text-left mb-8 shadow-sm">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">Booking Reference</p>
            <p class="text-lg font-mono font-black text-pink-500">
              {{ bookingStore.booking_reference || `CSUCC${bookingId?.toString().padStart(8, '0')}` }}
            </p>
          </div>
          <div class="sm:text-right">
            <p class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">Amount</p>
            <p class="text-lg font-black text-gray-900 leading-none">
              ₱{{ bookingStore.booking_total?.toLocaleString() || bookingStore.grandTotal?.toLocaleString() }}
            </p>
            <div class="mt-2 inline-flex items-center gap-1.5 bg-amber-50 px-2 py-1 rounded-md text-amber-600 text-[10px] font-black uppercase border border-amber-100 italic">
               Payment Pending
            </div>
          </div>
        </div>
      </div>
      
      <div class="flex flex-col sm:flex-row gap-4 mb-8">
        <button @click="retryPayment" 
                class="flex-1 bg-pink-500 hover:bg-pink-600 text-white px-8 py-4 rounded-xl font-black text-sm uppercase tracking-widest transition-all shadow-xl shadow-pink-100 active:scale-[0.98]">
          Complete Payment
        </button>
        <button @click="cancelBooking" 
                class="flex-1 bg-white border-2 border-gray-100 hover:border-gray-200 px-8 py-4 rounded-xl font-black text-sm uppercase tracking-widest text-gray-400 hover:text-gray-600 transition-all active:scale-[0.98]">
          Cancel Booking
        </button>
      </div>
      
      <p class="text-[11px] text-gray-400 border-t border-gray-100 pt-6">
        Secure bookings are held while your session is active.
      </p>
    </div>

    <!-- Error State -->
    <div v-else class="bg-white rounded-3xl border border-gray-100 shadow-2xl p-8 sm:p-12 text-center max-w-lg w-full">
      <div class="w-20 h-20 bg-rose-50 border border-rose-100 rounded-2xl flex items-center justify-center mx-auto mb-8 text-4xl shadow-inner scale-110">
        ❌
      </div>
      
      <h1 class="text-3xl font-black text-gray-900 mb-3 tracking-tight">Payment Unsuccessful</h1>
      
      <p class="text-lg font-bold text-rose-500 mb-8 leading-relaxed">
        {{ errorMessage || 'We couldn\'t confirm your payment.' }}
      </p>
      
      <div class="flex flex-col gap-4 mb-8">
        <button @click="retryPayment" 
                class="w-full bg-pink-500 hover:bg-pink-600 text-white py-4 rounded-xl font-black text-sm uppercase tracking-widest transition-all shadow-xl shadow-pink-100 active:scale-[0.98]">
          Try Payment Again
        </button>
        <button @click="goHome" 
                class="w-full bg-white border-2 border-gray-100 hover:border-gray-200 py-4 rounded-xl font-black text-sm uppercase tracking-widest text-gray-400 hover:text-gray-600 transition-all active:scale-[0.98]">
          Return to Home
        </button>
      </div>
      
      <div class="pt-6 border-t border-gray-100">
        <p class="text-xs text-gray-400 font-medium">
          If issues persist, contact our support team at 
          <a href="mailto:support@airlines.com" class="font-black text-pink-500 hover:underline ml-1">
            support@airlines.com
          </a>
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Custom animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>