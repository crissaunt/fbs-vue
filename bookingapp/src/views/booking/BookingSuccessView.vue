<template>
  <div class="min-h-screen bg-slate-50 py-20 px-4 md:px-8">
    <!-- Main Content Container -->
    <div class="max-w-3xl mx-auto text-center">
      <!-- Success Header Section -->
      <div class="mb-12">
        <h1 class="text-6xl md:text-7xl font-black text-slate-900 mb-8 tracking-tighter uppercase">
          Thank You!
        </h1>
        
        <!-- Large Green Checkmark -->
        <div class="flex justify-center mb-10">
          <div class="w-32 h-32 bg-emerald-500 rounded-lg flex items-center justify-center shadow-xl shadow-emerald-200">
            <svg class="w-20 h-20 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>

        <p class="text-xl text-slate-600 font-medium mb-2">
          Your e-ticket is on its way to your email.
        </p>
      </div>

      <!-- Booking Summary Card -->
      <div class="bg-white rounded-xl border border-slate-200 p-8 mb-6 shadow-sm">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 text-left">
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-widest font-black mb-1">PNR / RECORD LOCATOR</p>
            <div class="flex items-center gap-3">
              <span class="text-2xl font-mono font-bold text-slate-900 tracking-tighter bg-slate-100 px-2 rounded">{{ bookingReference }}</span>
              <button @click="copyReference" class="text-emerald-600 text-[10px] uppercase font-black hover:text-emerald-700 transition-colors">Copy</button>
            </div>
          </div>
          
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-widest font-black mb-1">Total Amount Paid</p>
            <span class="text-2xl font-bold text-slate-900">₱{{ formattedAmount }}</span>
          </div>

          <div class="md:col-span-2 pt-4 border-t border-slate-100 flex items-center gap-4">
             <div class="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-xl">
               💳
             </div>
             <div>
               <p class="text-[10px] text-slate-400 uppercase tracking-widest font-black">Transaction ID</p>
               <p class="text-sm font-mono text-slate-600">{{ transactionId }}</p>
             </div>
          </div>
        </div>
      </div>

      <!-- ⚠️ E-Ticket vs Boarding Pass Explainer -->
      <div class="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100/50 rounded-2xl p-6 mb-8 text-left shadow-sm">
        <div class="flex flex-col sm:flex-row items-start gap-4">
          <div class="bg-white text-indigo-500 w-12 h-12 rounded-full flex items-center justify-center shrink-0 shadow-sm border border-indigo-50/50">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-indigo-950 text-base mb-1.5 tracking-tight">Your E-Ticket vs. Boarding Pass</h3>
            <p class="text-indigo-800/80 text-sm leading-relaxed">
              This document serves as your permanent proof of priority purchase. However, it <strong>cannot be used at the boarding gate</strong>. 
              To obtain your actual Boarding Pass—which contains your verified seat assignment and scanning code—you will need to complete the 
              <strong class="text-indigo-900 border-b border-indigo-200">airport Check-in process</strong> within 24–48 hours before your departure.
            </p>
          </div>
        </div>
      </div>

      <!-- What's Next Steps -->
      <div class="bg-white border border-slate-200 rounded-xl p-6 mb-8 shadow-sm text-left">
        <h3 class="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
          <span class="bg-pink-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-black">?</span>
          What Happens Next?
        </h3>

        <div class="space-y-4">
          <!-- Step 1 Done -->
          <div class="flex items-start gap-3">
            <div class="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center shrink-0 mt-0.5">
              <svg class="w-3.5 h-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
            <div>
              <div class="text-sm font-bold text-slate-800">✅ Done — Booking Confirmed</div>
              <div class="text-xs text-slate-400 mt-0.5">Payment received. Your PNR is <span class="font-mono font-bold text-slate-600">{{ bookingReference }}</span>. Save this code!</div>
            </div>
          </div>

          <div class="border-l-2 border-dashed border-slate-200 ml-3 pl-3 py-0.5 space-y-4">
            <!-- Step 2 -->
            <div class="flex items-start gap-3">
              <div class="w-6 h-6 bg-pink-100 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                <span class="text-pink-600 font-black text-xs">2</span>
              </div>
              <div>
                <div class="text-sm font-bold text-slate-700">✈️ Check In at the Airport (24–48 hrs before flight)</div>
                <div class="text-xs text-slate-400 mt-0.5">Visit the check-in counter or self-service kiosk. Present your PNR (<span class="font-mono font-semibold">{{ bookingReference }}</span>) and a valid government-issued ID. The agent will verify your identity and accept your checked baggage.</div>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="flex items-start gap-3">
              <div class="w-6 h-6 bg-slate-100 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                <span class="text-slate-400 font-black text-xs">3</span>
              </div>
              <div>
                <div class="text-sm font-bold text-slate-500">🖨️ Receive Your Boarding Pass</div>
                <div class="text-xs text-slate-400 mt-0.5">After check-in is complete, the agent issues your Boarding Pass — the only document accepted at the security gate. It contains your seat number, gate, departure time, and a scannable QR code.</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Document comparison -->
        <div class="mt-8 pt-8 border-t border-slate-100">
          <p class="text-[11px] text-slate-400 uppercase font-black tracking-widest mb-4">Travel Documents Guide</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            
            <!-- E-Ticket Card -->
            <div class="group relative overflow-hidden bg-white border border-slate-200 rounded-xl p-5 hover:border-slate-300 hover:shadow-md transition-all">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-8 h-8 rounded-lg bg-slate-100 text-slate-500 flex items-center justify-center">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                </div>
                <div class="font-bold text-slate-800">E-Ticket Itinerary</div>
              </div>
              <ul class="text-slate-600 space-y-2.5">
                <li class="flex items-start gap-2.5">
                  <svg class="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                  <span>Serves as receipt & proof of payment</span>
                </li>
                <li class="flex items-start gap-2.5">
                  <svg class="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                  <span>Features your PNR code string</span>
                </li>
                <li class="flex items-start gap-2.5">
                  <svg class="w-4 h-4 text-rose-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" /></svg>
                  <span class="text-rose-600 font-medium">Cannot be used for boarding gate</span>
                </li>
              </ul>
            </div>

            <!-- Boarding Pass Card -->
            <div class="group relative overflow-hidden bg-gradient-to-br from-[#FF579A] to-rose-500 border border-pink-400 rounded-xl p-5 hover:shadow-lg hover:shadow-pink-200 transition-all text-white">
              <div class="absolute top-0 right-0 right-4 top-4 opacity-20">
                <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>
              </div>
              <div class="flex items-center gap-3 mb-4 relative z-10">
                <div class="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" /></svg>
                </div>
                <div class="font-bold text-white">Boarding Pass</div>
              </div>
              <ul class="text-pink-50 space-y-2.5 relative z-10">
                <li class="flex items-start gap-2.5">
                  <svg class="w-4 h-4 text-white mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                  <span>Contains final seat & departure gate</span>
                </li>
                <li class="flex items-start gap-2.5">
                  <svg class="w-4 h-4 text-white mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                  <span>Scannable barcode for security</span>
                </li>
                <li class="flex items-start gap-2.5">
                  <svg class="w-4 h-4 text-white mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                  <span class="font-bold">Required to board your flight</span>
                </li>
              </ul>
            </div>

          </div>
        </div>
      </div>

      <!-- Actions Section -->
      <div class="space-y-4 max-w-sm mx-auto">
        <!-- Download Ticket Button -->
        <button @click="downloadItinerary" 
                class="w-full cursor-pointer py-5 bg-emerald-600 text-white rounded-lg font-black text-lg hover:bg-emerald-500 transition-all shadow-lg hover:shadow-emerald-200 flex items-center justify-center gap-3">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download E-Ticket / Itinerary
        </button>

        <button @click="goToDashboard" 
                class="w-full cursor-pointer py-4 bg-slate-900 text-white rounded-lg font-black text-mg hover:bg-slate-700 transition-all shadow-lg hover:shadow-slate-200 mb-2">
          Return to Dashboard
        </button>

        <div v-if="!isActivity">
          <button @click="goHome" 
                  class="w-full py-4 text-emerald-600 font-black flex items-center justify-center gap-2 hover:text-emerald-500 cursor-pointer">
            <span class="underline" >Click here to start a new booking instantly.</span>
          </button>
        </div>
        <div v-else class="p-4 bg-slate-100 rounded-lg">
          <p class="text-slate-500 text-sm font-medium italic">
            "We can't wait to see you complete your session and master the skies!"
          </p>
        </div>
      </div>

      <!-- Share Link -->
      <div class="mt-12 pt-8 border-t border-slate-100 ">
        <button @click="copyBookingLink" class="text-slate-400 hover:text-slate-600 cursor-pointer text-xs font-bold uppercase tracking-widest transition-colors flex items-center gap-2 mx-auto">
          <span>🔗 Share your journey link</span>
        </button>
      </div>
    </div>

    <!-- Minimal Toast Message -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 -translate-y-4"
      leave-to-class="opacity-0 -translate-y-4"
    >
      <div v-if="showToast" 
           class="fixed top-8 left-1/2 -translate-x-1/2 z-[100]">
        <div class="bg-slate-900 text-white px-6 py-3 rounded-full shadow-2xl flex items-center gap-3">
          <span class="text-emerald-400">✓</span>
          <p class="text-sm font-bold tracking-tight">{{ toastMessage }}</p>
        </div>
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

const bookingReference = ref('');
const transactionId = ref('');
const amountPaid = ref(0);
const bookingId = ref(null);
const showToast = ref(false);
const toastMessage = ref('');

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
    transactionId.value = query.payment_id;
  }
  
  if (query.amount) {
    amountPaid.value = parseFloat(query.amount);
  }
  
  if (query.booking_id) {
    bookingId.value = query.booking_id;
  }
  
  if (!bookingReference.value) {
    bookingReference.value = localStorage.getItem('last_booking_ref') || 'N/A';
  }
});

const downloadItinerary = async () => {
  if (!bookingId.value) {
    showToastMessage('Booking ID missing - cannot download');
    return;
  }
  
  showToastMessage('Generating your E-Ticket...');
  
  try {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const downloadUrl = `${baseUrl}/flightapp/download-itinerary/${bookingId.value}/`;
    
    // Open in new tab or trigger download
    window.open(downloadUrl, '_blank');
  } catch (error) {
    console.error('Download error:', error);
    showToastMessage('Failed to download itinerary');
  }
};

const copyReference = () => {
  navigator.clipboard.writeText(bookingReference.value);
  showToastMessage('Booking reference copied');
};

const copyBookingLink = () => {
  const link = `${window.location.origin}/booking/${bookingReference.value}`;
  navigator.clipboard.writeText(link);
  showToastMessage('Booking link copied');
};

const showToastMessage = (message) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

const isActivity = computed(() => !!bookingStore.activityCode);

const goToDashboard = () => {
  showToastMessage('Returning to dashboard...');
  bookingStore.clearActivityCodeValidation();
  bookingStore.resetBooking();
  localStorage.removeItem('payment_session');
  localStorage.removeItem('current_booking');
  router.push({ name: 'StudentDashboard' });
};

const goHome = () => {
  if (isActivity.value) {
    showToastMessage('Action unavailable during activity');
    return;
  }
  showToastMessage('Starting new booking...');
  bookingStore.resetBooking();
  router.push({ name: 'Home' });
};
</script>

<style scoped>
/* Smooth transitions */
* {
  scroll-behavior: smooth;
}
</style>