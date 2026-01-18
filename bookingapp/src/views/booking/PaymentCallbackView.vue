<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { paymentPollingService } from '@/services/booking/paymentPollingService';
import api from '@/services/booking/api';

const route = useRoute();
const router = useRouter();
const bookingStore = useBookingStore();

const loading = ref(true);
const success = ref(false);
const errorMessage = ref('');
const paymentId = ref('');
const bookingReference = ref('');
const amountPaid = ref(0);
const pollingCount = ref(0);
const maxPollingAttempts = 15;
const pollingInterval = ref(null);
const processingStatus = ref('');
const showIncompleteState = ref(false);

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

// In PaymentCallbackView.vue

// Update the pollPaymentStatus function:
const pollPaymentStatus = async (bookingId) => {
  if (pollingCount.value >= maxPollingAttempts) {
    clearInterval(pollingInterval.value);
    showIncompleteState.value = true;
    loading.value = false;
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
      // Payment confirmed!
      clearInterval(pollingInterval.value);
      success.value = true;
      paymentId.value = result.data.payment_id;
      bookingReference.value = result.data.booking_reference || `BK${bookingId.toString().padStart(8, '0')}`;
      amountPaid.value = bookingStore.booking_total || bookingStore.grandTotal;
      processingStatus.value = 'Payment confirmed!';
      
      // Clear the booking store
      bookingStore.resetBooking();
      localStorage.removeItem('current_booking');
      localStorage.removeItem('payment_session');
      
      loading.value = false;
      
      // Update URL to remove parameters
      window.history.replaceState({}, document.title, window.location.pathname);
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
    
    // FIXED: Use the correct endpoint
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
          // Payment processed successfully!
          success.value = true;
          paymentId.value = verifyResponse.data.payment_id;
          bookingReference.value = verifyResponse.data.booking_reference || `BK${bookingId.toString().padStart(8, '0')}`;
          amountPaid.value = bookingStore.booking_total || bookingStore.grandTotal;
          
          // Clear the booking store
          bookingStore.resetBooking();
          localStorage.removeItem('current_booking');
          localStorage.removeItem('payment_session');
          
          loading.value = false;
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
  // 1. Clear Pinia Store
  bookingStore.resetBooking();

  // 2. Clear LocalStorage keys
  localStorage.removeItem('current_booking');
  localStorage.removeItem('payment_session');
  // Add any other keys you use, e.g., 'pending_booking_id'
  
  // 3. Navigate to Home
  router.push({ name: 'Home' }); // Match the name 'home' in your routes
};

const viewBooking = () => {
  if (bookingReference.value) {
    router.push({ name: 'BookingDetails', params: { reference: bookingReference.value } });
  } else {
    goHome();
  }
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
  if (confirm('Are you sure you want to cancel this booking?')) {
    try {
      await api.post(`cancel-booking/${bookingStore.booking_id}/`);
      bookingStore.resetBooking();
      localStorage.removeItem('current_booking');
      localStorage.removeItem('payment_session');
      router.push({ name: 'Home' });
    } catch (error) {
      alert('Failed to cancel booking: ' + error.message);
    }
  }
};
</script>

<template>
  <div class="callback-page">
    <!-- Loading State -->
    <div v-if="loading" class="status-card">
      <div class="spinner"></div>
      <p class="processing-status">{{ processingStatus }}</p>
      <p v-if="pollingCount < maxPollingAttempts">
        {{ getLoadingMessage() }}
      </p>
      <p v-else>
        Taking longer than expected... Still verifying your payment.
      </p>
      <div v-if="pollingCount > 0" class="polling-info">
        <small>Attempt {{ pollingCount }} of {{ maxPollingAttempts }}</small>
      </div>
    </div>

    <!-- Incomplete Payment State -->
    <div v-else-if="showIncompleteState" class="status-card incomplete">
      <div class="icon">🔄</div>
      <h1>Payment Not Completed</h1>
      <p class="message">It looks like you didn't complete the payment on PayMongo's checkout page.</p>
      
      <div class="instructions">
        <p><strong>What happened:</strong></p>
        <ul>
          <li>You were redirected to PayMongo's secure payment page</li>
          <li>The payment was not completed</li>
          <li>You returned to this page without finishing the transaction</li>
        </ul>
      </div>
      
      <div class="booking-info">
        <p><strong>Booking Reference:</strong> {{ bookingStore.booking_reference || `BK${bookingId?.toString().padStart(8, '0')}` }}</p>
        <p><strong>Amount:</strong> ₱{{ bookingStore.booking_total?.toLocaleString() || bookingStore.grandTotal?.toLocaleString() }}</p>
        <p><strong>Status:</strong> <span class="badge pending-badge">Payment Pending</span></p>
      </div>
      
      <div class="actions">
        <button @click="retryPayment" class="btn-retry">
          Complete Payment Now
        </button>
        <button @click="cancelBooking" class="btn-cancel">
          Cancel Booking
        </button>
      </div>
      
      <p class="note">
        Your booking will be held for 24 hours. Complete payment to confirm your seats.
      </p>
    </div>

    <!-- Success State -->
    <div v-else-if="success" class="status-card success">
      <div class="icon">✈️</div>
      <h1>Booking Confirmed!</h1>
      <p class="success-message">Your flight booking has been successfully confirmed.</p>
      
      <div class="booking-details">
        <div class="detail-row">
          <span class="label">Booking Reference:</span>
          <span class="value">{{ bookingReference }}</span>
        </div>
        <div class="detail-row" v-if="paymentId">
          <span class="label">Payment ID:</span>
          <span class="value">{{ paymentId }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Amount Paid:</span>
          <span class="value">₱ {{ amountPaid.toLocaleString() }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Status:</span>
          <span class="status-badge confirmed">Confirmed</span>
        </div>
      </div>

      <p class="instructions">
        Your booking details and e-ticket have been sent to your email.
        Please check your inbox (and spam folder).
      </p>

      <div class="actions">
        <button @click="goHome" class="btn-home">Return to Home</button>
        <button @click="viewBooking" class="btn-view">View My Booking</button>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="status-card error">
      <div class="icon">❌</div>
      <h1>Payment Unsuccessful</h1>
      <p class="error-message">{{ errorMessage || 'We couldn\'t confirm your payment.' }}</p>
      
      <div class="actions">
        <button @click="retryPayment" class="btn-retry">Try Payment Again</button>
        <button @click="goHome" class="btn-home-secondary">Return to Home</button>
      </div>
      
      <p class="support-note">
        If this issue persists, please contact our support team at 
        <a href="mailto:support@airlines.com">support@airlines.com</a>
      </p>
    </div>
  </div>
</template>



<style scoped>
/* Add polling info style */
.polling-info {
  margin-top: 1rem;
  color: #6c757d;
  font-size: 0.85rem;
}

/* Rest of your styles remain the same */
.callback-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.status-card {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.success .icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error .icon {
  font-size: 4rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

h1 {
  color: #003870;
  margin-bottom: 1rem;
  font-weight: 700;
}

.success-message {
  color: #28a745;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.error-message {
  color: #dc3545;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.booking-details {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  margin: 1.5rem 0;
  text-align: left;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e9ecef;
}

.detail-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #495057;
}

.value {
  color: #003870;
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-badge.confirmed {
  background: #d4edda;
  color: #155724;
}

.instructions {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 1.5rem 0;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-home, .btn-view, .btn-retry, .btn-home-secondary {
  flex: 1;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 1rem;
}

.btn-home {
  background: #003870;
  color: white;
}

.btn-home:hover {
  background: #002b58;
}

.btn-view {
  background: #28a745;
  color: white;
}

.btn-view:hover {
  background: #218838;
}

.btn-retry {
  background: #007bff;
  color: white;
}

.btn-retry:hover {
  background: #0056b3;
}

.btn-home-secondary {
  background: #6c757d;
  color: white;
}

.btn-home-secondary:hover {
  background: #545b62;
}

.support-note {
  margin-top: 1.5rem;
  font-size: 0.85rem;
  color: #6c757d;
}

.support-note a {
  color: #007bff;
  text-decoration: none;
}

.support-note a:hover {
  text-decoration: underline;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: #007bff;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .status-card {
    padding: 1.5rem;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .btn-home, .btn-view, .btn-retry, .btn-home-secondary {
    width: 100%;
  }
}
</style>