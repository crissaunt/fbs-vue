<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 p-4 md:p-8 relative overflow-hidden">
    <!-- Background Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 right-0 w-1/3 h-1/3 bg-gradient-to-br from-[#FF579A]/5 to-transparent rounded-md blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-1/3 h-1/3 bg-gradient-to-tr from-gray-400/5 to-transparent rounded-md blur-3xl"></div>
    </div>

    <!-- Main Container -->
    <div class="relative max-w-6xl mx-auto">
      <BookingStatusHeader />
      <!-- Content States -->
      <LoadingOverlay 
        v-if="loading"
        :show="true" 
        :title="loadingMessage || 'Securing Payment'"
        subtitle="Please do not refresh or close this window."
      />

      <!-- Session Expired -->
      <div v-else-if="!isSessionValid" class="bg-white rounded-lg border border-gray-100 shadow-xl p-12 text-center max-w-lg mx-auto mt-20">
        <div class="w-20 h-20 bg-amber-50 rounded-lg flex items-center justify-center mx-auto mb-8 float-animation">
          <span class="text-3xl">⏰</span>
        </div>
        <h3 class="text-2xl font-black text-gray-900 mb-3">SESSION EXPIRED</h3>
        <p class="text-gray-400 text-sm mb-10 leading-relaxed font-medium">
          Your secure booking session has timed out. Please restart the booking process to ensure your seat remains available.
        </p>
        <button @click="restartBooking" 
                class="w-full bg-gray-900 hover:bg-black text-white py-4 rounded-lg font-bold transition-all active:scale-[0.98] shadow-lg shadow-gray-200">
          Start New Booking
        </button>
      </div>

      <!-- Main Content -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <!-- Left Column - Booking details & Summary -->
        <div class="lg:col-span-8 space-y-6">
          
          <!-- Retry Alert Banner -->
          <div v-if="isRetrying" class="bg-amber-50 border-l-4 border-amber-500 rounded-lg p-5 flex items-start shadow-sm mb-6">
            <div class="flex-shrink-0 mt-0.5">
              <svg class="h-5 w-5 text-amber-500" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3 text-sm">
              <h3 class="font-bold text-amber-800">Action Required: Payment Not Completed</h3>
              <p class="mt-1 text-amber-700 font-medium">
                Your previous payment attempt was unsuccessful or cancelled. Don't worry, we've saved your entire booking securely! Your seats are reserved while your session is active.
              </p>
            </div>
          </div>

          <!-- Premium Amount Display -->
          <div class="relative overflow-hidden bg-white rounded-lg border border-gray-100 shadow-sm p-1">
            <div class="absolute top-0 right-0 p-4">
              <div class="flex items-center space-x-2 px-3 py-1 bg-green-50 text-green-700 rounded-md text-xs font-bold border border-green-100 uppercase tracking-tighter">
                <span class="w-1.5 h-1.5 bg-green-500 rounded-md animate-pulse mr-1"></span>
                Secure Session
              </div>
            </div>
            
            <div class="bg-gradient-to-br from-gray-50/50 to-white p-8 rounded-md">
              <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                  <h2 class="text-sm font-bold text-gray-400 uppercase tracking-[0.2em] mb-3">Total Amount to Pay</h2>
                  <div class="flex items-baseline">
                    <span class="text-2xl font-light text-gray-400 mr-2">₱</span>
                    <span class="text-6xl font-black text-gray-900 tracking-tight">{{ totalAmount.toLocaleString() }}</span>
                  </div>
                  <p class="text-gray-400 text-xs mt-3 flex items-center">
                    <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    Final price inclusive of taxes and surcharge
                  </p>
                </div>
                
                <div class="flex flex-col items-end">
                  <div class="text-right mb-4">
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Booking Ref</p>
                    <p class="text-xl font-mono font-black text-[#FF579A]">{{ bookingReference || 'N/A' }}</p>
                  </div>
                  <div class="px-4 py-2 bg-amber-50 rounded-lg border border-amber-100 flex items-center">
                    <span class="text-amber-700 text-xs font-bold uppercase tracking-wider">{{ bookingStatus }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Trip Overview -->
          <div class="bg-white rounded-lg border border-gray-100 shadow-sm overflow-hidden">
            <div class="border-b border-gray-50 px-8 py-5 flex items-center justify-between bg-gray-50/30">
              <h3 class="text-lg font-bold text-gray-800">Trip Overview</h3>
              <div class="flex items-center space-x-2">
                <span class="text-xs font-bold px-3 py-1 bg-[#FF579A]/10 text-[#FF579A] rounded-md uppercase tracking-wider">
                  {{ tripTypeLabel }}
                </span>
              </div>
            </div>
            
            <div class="p-8">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
                <!-- Flight Info -->
                <div class="space-y-6">
                  <!-- Depart -->
                  <div v-if="bookingStore.selectedOutbound" class="relative pl-8">
                    <div class="absolute left-0 top-1 w-6 h-6 bg-pink-50 rounded-md flex items-center justify-center">
                      <svg class="w-3 h-3 text-[#FF579A] rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </div>
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Outbound Flight</p>
                    <p class="text-lg font-bold text-gray-900 leading-tight">
                      {{ bookingStore.selectedOutbound.origin }} 
                      <span class="text-gray-300 mx-2">→</span>
                      {{ bookingStore.selectedOutbound.destination }}
                    </p>
                    <p class="text-xs text-gray-500 font-medium">Flight {{ bookingStore.selectedOutbound.flight_number }}</p>
                  </div>

                  <!-- Return -->
                  <div v-if="bookingStore.selectedReturn" class="relative pl-8">
                    <div class="absolute left-0 top-1 w-6 h-6 bg-blue-50 rounded-md flex items-center justify-center">
                      <svg class="w-3 h-3 text-blue-500 -rotate-135" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </div>
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Return Flight</p>
                    <p class="text-lg font-bold text-gray-900 leading-tight">
                      {{ bookingStore.selectedReturn.origin }} 
                      <span class="text-gray-300 mx-2">→</span>
                      {{ bookingStore.selectedReturn.destination }}
                    </p>
                    <p class="text-xs text-gray-500 font-medium">Flight {{ bookingStore.selectedReturn.flight_number }}</p>
                  </div>
                </div>

                <!-- Traveler Info -->
                <div class="bg-gray-50/50 rounded-lg p-6 border border-gray-100/50">
                  <div class="flex items-center space-x-3 mb-6">
                    <div class="w-10 h-10 bg-white shadow-sm rounded-md flex items-center justify-center">
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Main Contact</p>
                      <p class="text-sm font-bold text-gray-900">{{ contactName }}</p>
                    </div>
                  </div>
                  
                  <div class="space-y-3">
                    <div class="flex items-center text-xs text-gray-500">
                      <svg class="w-3.5 h-3.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      {{ bookingStore.contactInfo.email }}
                    </div>
                    <div class="flex items-center text-xs text-gray-500">
                      <svg class="w-3.5 h-3.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      +63 {{ bookingStore.contactInfo.phone }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column - Payment Panel -->
        <div class="lg:col-span-4 space-y-6">
          <div class="bg-white rounded-lg border border-gray-100 shadow-lg shadow-pink-100/20 overflow-hidden">
            <div class="p-8">
              <h3 class="text-xl font-bold text-gray-900 mb-2">Secure Checkout</h3>
              <p class="text-xs text-gray-400 mb-6 leading-relaxed">You will be redirected to our secure PayMongo payment gateway to complete your transaction.</p>

            
              <div v-if="priceBreakdown" class="mb-8 p-6 bg-gray-50/50 rounded-xl border border-gray-100/50 space-y-4">
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Price Summary</p>
                
                <div class="space-y-2.5">
                
                  <div v-if="priceBreakdown.adult_base > 0" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Adult Base Fare</span>
                    <span class="text-gray-900 font-bold">₱{{ priceBreakdown.adult_base.toLocaleString() }}</span>
                  </div>
                  <div v-if="priceBreakdown.child_base > 0" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Child Base Fare</span>
                    <span class="text-gray-900 font-bold">₱{{ priceBreakdown.child_base.toLocaleString() }}</span>
                  </div>
                  <div v-if="priceBreakdown.infant_base > 0" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Infant Base Fare</span>
                    <span class="text-gray-900 font-bold">₱{{ priceBreakdown.infant_base.toLocaleString() }}</span>
                  </div>

               
                  <div v-if="priceBreakdown.taxes > 0" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Taxes & Fees</span>
                    <span class="text-gray-900 font-bold">₱{{ priceBreakdown.taxes.toLocaleString() }}</span>
                  </div>

              
                  <div v-if="priceBreakdown.addons > 0" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Selected Add-ons</span>
                    <span class="text-gray-900 font-bold">₱{{ priceBreakdown.addons.toLocaleString() }}</span>
                  </div>

                  
                  <div v-if="priceBreakdown.insurance > 0" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Travel Insurance</span>
                    <span class="text-gray-900 font-bold">₱{{ priceBreakdown.insurance.toLocaleString() }}</span>
                  </div>

                  <div class="border-t border-gray-200 pt-3 mt-4">
                    <div class="flex justify-between items-center">
                      <span class="text-gray-900 font-black text-lg">Total Amount</span>
                      <span class="text-3xl font-black text-gray-900 flex items-center">
                        <span class="text-pink-500 text-xl mr-1">₱</span>
                        <AnimatedNumber :value="totalAmount" />
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Promo Code -->
              <div class="mb-8">
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Promo Code</p>
                <div class="flex gap-2">
                  <input type="text" placeholder="Enter code" class="flex-1 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-1 focus:ring-pink-500 outline-none transition-all">
                  <button class="px-4 py-2 border border-gray-200 rounded-lg text-xs font-bold text-gray-400 hover:text-pink-500 hover:border-pink-200 transition-colors uppercase">Apply</button>
                </div>
              </div>

              <!-- Terms and Conditions -->
              <div class="mb-8 p-4 bg-gray-50/50 rounded-lg border border-gray-100">
                <label class="flex items-start gap-3 cursor-pointer group">
                  <div class="flex items-center h-5 mt-0.5">
                    <input type="checkbox" v-model="hasAgreedToTerms" class="w-4 h-4 text-[#FF579A] border-gray-300 rounded focus:ring-[#FF579A]/20 transition-all cursor-pointer">
                  </div>
                  <div class="text-[11px] leading-relaxed text-gray-500 group-hover:text-gray-700 transition-colors">
                    I have read and agree to the <a href="#" class="text-[#FF579A] font-bold hover:underline">Fare Rules</a>, 
                    <a href="#" class="text-[#FF579A] font-bold hover:underline">Privacy Policy</a>, and 
                    <a href="#" class="text-[#FF579A] font-bold hover:underline">Terms of Transport</a>.
                  </div>
                </label>
              </div>

              <!-- Main Action -->
              <div class="mt-8 pt-8 border-t border-gray-50">
                <button @click="handlePayMongoCheckout" 
                        :disabled="loading || !bookingId || !hasAgreedToTerms"
                        class="w-full py-4 bg-[#FF579A] hover:bg-[#FF4081] text-white rounded-lg font-bold shadow-lg shadow-pink-200 transition-all active:scale-[0.98] disabled:opacity-50 disabled:translate-y-0 disabled:shadow-none">
                  {{ loading ? 'Processing...' : 'Proceed to Payment' }}
                </button>
                
                <button @click="goBack" 
                        class="w-full mt-4 py-3 text-sm font-bold text-gray-400 hover:text-gray-600 transition-colors uppercase tracking-widest">
                  Back to Review
                </button>
              </div>
            </div>
          </div>

          <!-- Trust Badges -->
          <div class="flex items-center justify-center space-x-6 px-4">
            <div class="flex flex-col items-center opacity-30 grayscale hover:opacity-100 hover:grayscale-0 transition-all">
               <span class="text-[10px] font-black uppercase tracking-tighter">PCI DSS</span>
               <span class="text-[8px] text-gray-500 font-bold">COMPLIANT</span>
            </div>
            <div class="flex flex-col items-center opacity-30 grayscale hover:opacity-100 hover:grayscale-0 transition-all">
               <span class="text-[10px] font-black uppercase tracking-tighter">SECURE</span>
               <span class="text-[8px] text-gray-500 font-bold">256-BIT SSL</span>
            </div>
          </div>

          <!-- Help Section -->
          <div class="bg-gradient-to-br from-gray-900 to-black rounded-lg p-8 text-white relative overflow-hidden group border border-white/5">
            <div class="absolute -right-4 -bottom-4 w-24 h-24 bg-white/5 rounded-md blur-2xl group-hover:scale-150 transition-transform duration-700"></div>
            <h4 class="font-bold text-lg mb-4 flex items-center text-white">
              <span class="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center mr-3 text-sm">?</span>
              Need Help?
            </h4>
            <div class="space-y-4">
              <a href="tel:+63288558888" 
                 class="flex items-center space-x-4 text-gray-400 hover:text-white transition-all group/link">
                <div class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center group-hover/link:bg-white/10 transition-colors">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] uppercase font-black tracking-widest text-[#FF579A]">Call Us</p>
                  <p class="text-sm font-bold text-white">(02) 8855-8888</p>
                </div>
              </a>
              <a href="mailto:support@philippineairlines.com" 
                 class="flex items-center space-x-4 text-gray-400 hover:text-white transition-all group/link">
                <div class="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center group-hover/link:bg-white/10 transition-colors">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] uppercase font-black tracking-widest text-[#FF579A]">Email Us</p>
                  <p class="text-sm font-bold text-white">Payment Support</p>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 translate-y-2"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div v-if="showToast" 
           class="fixed bottom-6 right-6 bg-gradient-to-r from-[#FF579A] to-pink-500 text-white px-6 py-4 rounded-[5px] shadow-2xl flex items-center space-x-3 max-w-sm z-50">
        <div class="w-6 h-6 bg-white/20 rounded-md flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <span class="font-bold text-sm tracking-tight">{{ toastMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter, useRoute } from 'vue-router';
import api from '@/services/booking/api';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

const bookingStore = useBookingStore();
const router = useRouter();
const route = useRoute();

const loading = ref(false);
const loadingMessage = ref("");
const showToast = ref(false);
const toastMessage = ref("");
const hasAgreedToTerms = ref(false);
const isRetrying = ref(false);

// Computed properties
const bookingId = computed(() => bookingStore.booking_id);
const bookingReference = computed(() => bookingStore.booking_reference);
const bookingStatus = computed(() => bookingStore.booking_status || 'pending');
const tripTypeLabel = computed(() => bookingStore.isRoundTrip ? 'Round Trip' : 'One Way');

const contactName = computed(() => {
  const info = bookingStore.contactInfo;
  return `${info.title || ''} ${info.firstName || ''} ${info.lastName || ''}`.trim() || 'Not specified';
});

const priceBreakdown = computed(() => bookingStore.backendBreakdown?.breakdown);

const totalAmount = computed(() => {
  // Priority 1: Backend breakdown from Store (Authoritative - synced in Review page)
  if (bookingStore.backendBreakdown?.total_amount) {
    console.log('💰 PaymentView: Using Store backendBreakdown total:', bookingStore.backendBreakdown.total_amount);
    return bookingStore.backendBreakdown.total_amount;
  }
  
  // Priority 2: Amount passed as query param from Review (booking creation response.total_amount)
  const queryAmount = parseFloat(route.query.amount);
  if (Number.isFinite(queryAmount) && queryAmount > 0) {
    console.log('💰 PaymentView: Using query amount:', queryAmount);
    return queryAmount;
  }

  // Priority 3: Store's booking_total (legacy sync)
  if (bookingStore.booking_total > 0) {
    console.log('💰 PaymentView: Using Store booking_total:', bookingStore.booking_total);
    return bookingStore.booking_total;
  }
  
  // Priority 4: Client-computed grand total (fallback)
  console.log('⚠️ PaymentView: Falling back to Store grandTotal:', bookingStore.grandTotal);
  return bookingStore.grandTotal || 0;
});

const hasFlightInfo = computed(() => {
  return bookingStore.selectedOutbound || bookingStore.selectedReturn;
});

const isSessionValid = computed(() => {
  if (!bookingStore.sessionExpiry) return false;
  return Date.now() < bookingStore.sessionExpiry;
});

const syncBookingTotalFromBackend = async () => {
  try {
    if (!bookingStore.booking_id) return;
    const res = await api.get(`flightapp/booking/${bookingStore.booking_id}/`);
    if (res.data?.success && res.data?.booking) {
      const backendTotal = parseFloat(res.data.booking.total_amount);
      if (Number.isFinite(backendTotal) && backendTotal > 0) {
        bookingStore.booking_total = backendTotal;
        localStorage.setItem('current_booking_total', backendTotal);
      }
    }
  } catch (error) {
    console.error('Failed to sync booking total from backend:', error.response?.data || error.message);
  }
};

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
    showToastMessage("No booking ID found. Please complete your booking details first.");
    goBack();
    return;
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

    const response = await api.post('flightapp/create-checkout-session/', paymentData);

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
        errorMsg = typeof response.data.error === 'string' ? response.data.error : JSON.stringify(response.data.error);
      }
      showToastMessage(`Payment setup failed: ${errorMsg}`);
      loading.value = false;
    }
  } catch (error) {
    console.error("PayMongo Checkout Error:", error);
    showToastMessage("Payment Error: Failed to initialize payment gateway.");
    loading.value = false;
  }
};


// Lifecycle hooks
onMounted(() => {
  restoreBookingData();
  syncBookingTotalFromBackend();
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
  const isRetry = route.query.retry === 'true' || route.query.retry === true || urlParams.get('retry');
  
  if (isRetry) {
    isRetrying.value = true;
    showToastMessage('Payment was not completed. Your booking is safely held, please retry payment.', 5000);
    // Clean up query but keep state
    router.replace({ ...route, query: { ...route.query, retry: undefined } });
  } else if (success === 'true' && bookingId) {
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
  background: #FF579A;
  border-radius: 10px;
}

/* Transitions */
.fade-up-enter-active, .fade-up-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.float-animation {
  animation: float 6s ease-in-out infinite;
}

/* Smooth transitions */
* {
  scroll-behavior: smooth;
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

/* Button active state */
button:active {
  transform: scale(0.98);
}
</style>