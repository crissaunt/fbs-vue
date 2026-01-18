<template>
  <div class="pal-bg">
    <div class="container payment-wrapper">
      <div class="payment-card">
        <!-- Loading State -->
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
          <p>{{ loadingMessage }}</p>
        </div>

        <!-- Session Expired -->
        <div v-else-if="!isSessionValid" class="session-expired">
          <div class="expired-icon">⏰</div>
          <h3>Session Expired</h3>
          <p>Your booking session has expired. Please restart your booking.</p>
          <button @click="restartBooking" class="btn-restart">
            Start New Booking
          </button>
        </div>

        <!-- Payment Form -->
        <div v-else>
          <h2 class="title">Secure Payment</h2>
          
          <!-- Price Banner -->
          <div class="price-banner">
            <span class="label">Amount to Pay:</span>
            <span class="amount">₱ {{ totalAmount.toLocaleString() }}</span>
          </div>

          <!-- Booking Summary -->
          <div class="booking-summary">
            <p><strong>Booking Reference:</strong> {{ bookingReference || 'N/A' }}</p>
            <p><strong>Passenger:</strong> {{ contactName }}</p>
            <p><strong>Status:</strong> <span class="status-badge">{{ bookingStatus }}</span></p>
            <p><strong>Trip Type:</strong> {{ tripTypeLabel }}</p>
          </div>

          <!-- Flight Summary -->
          <div class="flight-summary" v-if="hasFlightInfo">
            <h4>Flight Details</h4>
            <div v-if="bookingStore.selectedOutbound" class="flight-item">
              <span class="flight-label">Depart:</span>
              <span>{{ bookingStore.selectedOutbound.origin }} → {{ bookingStore.selectedOutbound.destination }}</span>
              <span class="flight-number">{{ bookingStore.selectedOutbound.flight_number }}</span>
            </div>
            <div v-if="bookingStore.selectedReturn" class="flight-item">
              <span class="flight-label">Return:</span>
              <span>{{ bookingStore.selectedReturn.origin }} → {{ bookingStore.selectedReturn.destination }}</span>
              <span class="flight-number">{{ bookingStore.selectedReturn.flight_number }}</span>
            </div>
          </div>

          <!-- Payment Method Selection (Optional - can skip this if going directly to PayMongo) -->
          <div v-if="showPaymentMethods" class="payment-methods">
            <h3>Select Payment Method</h3>
            <p class="method-description">You'll be redirected to our secure payment partner to complete the transaction.</p>
            
            <div class="methods-grid">
              <div class="method-card" @click="handlePayMongoCheckout">
                <div class="method-icon">💳</div>
                <div class="method-info">
                  <h4>Pay with Multiple Options</h4>
                  <p>GCash, Maya, Credit/Debit Cards, and more</p>
                </div>
                <div class="method-arrow">→</div>
              </div>
              
              <div v-if="paymentService.isPayMongoConfigured()" class="method-card" @click="handleDirectGCash">
                <div class="method-icon">📱</div>
                <div class="method-info">
                  <h4>GCash Direct</h4>
                  <p>Pay directly using your GCash wallet</p>
                </div>
                <div class="method-arrow">→</div>
              </div>
            </div>
          </div>

          <!-- Payment Notice -->
          <p class="notice" v-if="!showPaymentMethods">
            You'll be redirected to a secure payment page to complete your transaction.
            We support <strong>GCash, Maya, QRPH, and Credit/Debit Cards</strong>.
          </p>

          <!-- Action Buttons -->
          <div class="actions" v-if="!showPaymentMethods">
            <button @click="goBack" class="btn-secondary" :disabled="loading">
              Back to Review
            </button>
            <button @click="handlePayMongoCheckout" class="btn-pay" :disabled="loading || !bookingId">
              Proceed to Secure Payment
            </button>
          </div>

          <!-- Debug Info -->
          <div v-if="showDebugInfo" class="debug-info">
            <small>Debug: Booking ID: {{ bookingId }} | Session Valid: {{ isSessionValid }} | Total: ₱{{ totalAmount.toLocaleString() }}</small>
          </div>
        </div>
      </div>
    </div>
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
const showPaymentMethods = ref(false); // Set to true to show method selection

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

// Session validation
const isSessionValid = computed(() => {
  if (!bookingStore.sessionExpiry) return false;
  return Date.now() < bookingStore.sessionExpiry;
});

/**
 * Restores booking data from localStorage if store is empty
 */
const restoreBookingData = () => {
  if (bookingStore.booking_id) return;
  
  try {
    const savedBooking = localStorage.getItem('current_booking');
    if (savedBooking) {
      const bookingData = JSON.parse(savedBooking);
      
      // Check if this booking is still valid
      const bookingAge = Date.now() - new Date(bookingData.created_at).getTime();
      const thirtyMinutes = 30 * 60 * 1000;
      
      if (bookingAge < thirtyMinutes) {
        // Restore to store
        bookingStore.saveBookingConfirmation({
          booking_id: bookingData.id,
          booking_reference: bookingData.reference,
          status: bookingData.status,
          total_amount: bookingData.total
        });
        
        // Extend session
        bookingStore.sessionExpiry = Date.now() + (15 * 60 * 1000);
        console.log('Booking restored from localStorage');
      } else {
        console.log('Booking data expired, clearing...');
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
 * Handle PayMongo Checkout (Multiple Payment Methods)
 * This will redirect to PayMongo's hosted checkout page
 */
const handlePayMongoCheckout = async () => {
  // Validate session
  if (!isSessionValid.value) {
    alert("Booking session expired. Please restart your booking.");
    restartBooking();
    return;
  }

  // Validate booking ID exists
  if (!bookingStore.booking_id) {
    try {
      alert("No booking ID found. Please complete your booking details first.");
      goBack();
      return;
    } catch (error) {
      alert('Failed to create booking: ' + error.message);
      return;
    }
  }

  loading.value = true;
  loadingMessage.value = "Creating secure payment session...";

  try {
    console.log('🚀 Initiating PayMongo checkout:', {
      bookingId: bookingStore.booking_id,
      amount: totalAmount.value,
      reference: bookingStore.booking_reference,
      tripType: tripTypeLabel.value
    });

    // Prepare payment data - use the EXACT format that worked in Postman
    const paymentData = {
      amount: totalAmount.value,
      booking_id: bookingStore.booking_id,
      customer_email: bookingStore.contactInfo.email || 'test@example.com',
      customer_name: `${bookingStore.contactInfo.firstName || 'Customer'} ${bookingStore.contactInfo.lastName || ''}`.trim(),
      customer_phone: bookingStore.contactInfo.phone || '09171234567'
    };

    console.log('📤 Sending payment data:', paymentData);

    // Call backend to create checkout session
    const response = await api.post('create-checkout-session/', paymentData);

    console.log('📥 Checkout session response:', response.data);

    // FIX: Check for success AND checkout_url
    if (response.data && response.data.success === true && response.data.checkout_url) {
      // Store payment session info
      localStorage.setItem('payment_session', JSON.stringify({
        checkout_url: response.data.checkout_url,
        booking_id: bookingStore.booking_id,
        booking_reference: bookingStore.booking_reference,
        amount: totalAmount.value,
        timestamp: Date.now()
      }));

      console.log('🔗 Redirecting to PayMongo checkout:', response.data.checkout_url);
      
      // Clear loading state
      loading.value = false;
      loadingMessage.value = "";
      
      // Add a small delay to show the success state
      setTimeout(() => {
        // Redirect to PayMongo's hosted checkout page
        window.location.href = response.data.checkout_url;
      }, 500);
      
    } else {
      // Handle different error response formats
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
      
      console.error('❌ PayMongo checkout failed:', errorMsg);
      alert(`❌ Payment setup failed: ${errorMsg}`);
      loading.value = false;
    }

  } catch (error) {
    console.error("❌ PayMongo Checkout Error:", error);
    
    let errorMsg = "Payment initialization failed.";
    
    if (error.response) {
      console.error('📊 Error response status:', error.response.status);
      console.error('📊 Error response data:', error.response.data);
      
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
      console.error('🌐 Network error details:', error.request);
      errorMsg = "Network error. Please check your internet connection.";
    } else {
      errorMsg = error.message;
    }
    
    alert(`❌ Payment Error: ${errorMsg}`);
    loading.value = false;
  }
};

/**
 * Direct PayMongo Checkout (Fallback method)
 * Creates checkout session directly with PayMongo API
 */
const handleDirectPayMongoCheckout = async () => {
  if (!paymentService.isPayMongoConfigured()) {
    throw new Error('PayMongo is not configured');
  }

  try {
    loadingMessage.value = "Creating payment session...";
    
    // Create checkout session directly with PayMongo
    const response = await paymentService.createCheckoutSession({
      amount: totalAmount.value,
      booking_id: bookingStore.booking_id,
      booking_reference: bookingStore.booking_reference,
      customer_email: bookingStore.contactInfo.email,
      customer_name: `${bookingStore.contactInfo.firstName} ${bookingStore.contactInfo.lastName}`
    });

    if (response.success && response.checkout_url) {
      console.log('Direct PayMongo checkout URL:', response.checkout_url);
      
      // Store session info
      localStorage.setItem('payment_session', JSON.stringify({
        checkout_url: response.checkout_url,
        booking_id: bookingStore.booking_id,
        booking_reference: bookingStore.booking_reference,
        amount: totalAmount.value,
        timestamp: Date.now()
      }));

      // Redirect to PayMongo
      window.location.href = response.checkout_url;
    } else {
      throw new Error(response.error || 'Failed to create checkout session');
    }

  } catch (error) {
    console.error('Direct PayMongo checkout error:', error);
    throw error;
  }
};

/**
 * Handle Direct GCash Payment
 */
const handleDirectGCash = async () => {
  if (!paymentService.isPayMongoConfigured()) {
    alert("GCash payment is not available at the moment.");
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
      console.log('GCash redirect URL:', result.next_action.redirect.url);
      window.location.href = result.next_action.redirect.url;
    } else {
      throw new Error(result.error || 'GCash payment failed');
    }

  } catch (error) {
    console.error('GCash payment error:', error);
    alert(`GCash Error: ${error.message}`);
    loading.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  console.log('PaymentView mounted');
  console.log('Current booking store:', {
    booking_id: bookingStore.booking_id,
    booking_reference: bookingStore.booking_reference,
    sessionExpiry: bookingStore.sessionExpiry ? new Date(bookingStore.sessionExpiry).toLocaleString() : 'None',
    isSessionValid: isSessionValid.value,
    grandTotal: bookingStore.grandTotal,
    tripType: bookingStore.tripType,
    isRoundTrip: bookingStore.isRoundTrip
  });
  
  // Restore booking data if needed
  restoreBookingData();
  
  // Check for payment callback parameters
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
    alert('Payment successful! Your booking has been confirmed.');
    // Clear URL parameters
    window.history.replaceState({}, document.title, window.location.pathname);
  } else if (error) {
    alert(`Payment failed: ${decodeURIComponent(error)}`);
    window.history.replaceState({}, document.title, window.location.pathname);
  }
};

onUnmounted(() => {
  // Clean up if needed
});
</script>



<style scoped>
.payment-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.payment-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.title {
  color: #003870;
  margin-bottom: 1.5rem;
  font-weight: 700;
}

.price-banner {
  background: #f0f7ff;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid #d0e4ff;
}

.label {
  display: block;
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.amount {
  font-size: 2rem;
  font-weight: 800;
  color: #003870;
}

.booking-summary {
  text-align: left;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  color: #444;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 8px;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #ffc107;
  color: #856404;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Payment Methods Section */
.payment-methods {
  margin: 2rem 0;
  text-align: left;
}

.payment-methods h3 {
  color: #003870;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.method-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.methods-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.method-card {
  display: flex;
  align-items: center;
  padding: 1.25rem;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.method-card:hover {
  border-color: #007bff;
  box-shadow: 0 5px 15px rgba(0, 123, 255, 0.1);
  transform: translateY(-2px);
}

.method-icon {
  font-size: 2rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.method-info {
  flex: 1;
  text-align: left;
}

.method-info h4 {
  margin: 0 0 0.25rem;
  color: #003870;
  font-size: 1rem;
}

.method-info p {
  margin: 0;
  font-size: 0.875rem;
  color: #666;
}

.method-arrow {
  font-size: 1.5rem;
  color: #007bff;
  font-weight: bold;
}

.notice {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.5;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

/* Actions */
.actions {
  display: flex;
  gap: 1rem;
}

.btn-pay {
  flex: 2;
  background: #007bff;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 1rem;
}

.btn-pay:hover:not(:disabled) {
  background: #0056b3;
}

.btn-pay:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  flex: 1;
  background: #e9ecef;
  border: none;
  padding: 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
  font-size: 1rem;
}

.btn-secondary:hover {
  background: #dde1e6;
}

/* Loading State */
.loading-overlay {
  padding: 3rem 0;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #007bff;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Session Expired */
.session-expired {
  padding: 3rem 0;
  text-align: center;
}

.expired-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.session-expired h3 {
  color: #dc3545;
  margin-bottom: 1rem;
}

.session-expired p {
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.btn-restart {
  background: #003870;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-restart:hover {
  background: #002b58;
}

/* Debug Info */
.debug-info {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px dashed #ddd;
  color: #888;
  font-size: 0.75rem;
}

/* Responsive */
@media (max-width: 768px) {
  .payment-card {
    padding: 1.5rem;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .btn-pay, .btn-secondary {
    width: 100%;
  }
  
  .amount {
    font-size: 1.5rem;
  }
  
  .method-card {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .payment-wrapper {
    padding: 10px;
  }
  
  .payment-card {
    padding: 1rem;
  }
}


.trip-type-label {
  display: inline-block;
  padding: 2px 8px;
  background: #e3f2fd;
  color: #1565c0;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-left: 10px;
}

.flight-summary {
  text-align: left;
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #003870;
}

.flight-summary h4 {
  margin: 0 0 0.75rem 0;
  color: #003870;
  font-size: 1rem;
}

.flight-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #ddd;
}

.flight-item:last-child {
  border-bottom: none;
}

.flight-label {
  font-weight: 600;
  color: #003870;
  min-width: 60px;
}

.flight-number {
  background: #003870;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
}

@media (max-width: 768px) {
  .flight-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .flight-number {
    align-self: flex-start;
  }
}
</style>