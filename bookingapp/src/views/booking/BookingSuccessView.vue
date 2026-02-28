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
      <div class="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-6 text-left">
        <div class="flex items-start gap-3">
          <span class="text-2xl mt-0.5 shrink-0">⚠️</span>
          <div>
            <h3 class="font-bold text-amber-800 text-sm mb-1">This is your E-Ticket — NOT a Boarding Pass</h3>
            <p class="text-amber-700 text-xs leading-relaxed">
              You just received proof of purchase. You <strong>cannot board your flight with this</strong>. 
              To get your actual Boarding Pass — the document with your seat number and QR code — 
              you must complete the <strong>Check-in process</strong> at the airport counter or kiosk, 
              typically 24–48 hours before departure.
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
        <div class="mt-5 pt-4 border-t border-slate-100">
          <p class="text-[10px] text-slate-400 uppercase font-bold tracking-wider mb-3">Quick Comparison</p>
          <div class="grid grid-cols-2 gap-3 text-xs">
            <div class="bg-slate-50 border border-slate-200 rounded-lg p-3">
              <div class="font-bold text-slate-700 mb-2">📄 E-Ticket (this)</div>
              <ul class="text-slate-500 space-y-1">
                <li class="flex items-center gap-1.5"><span class="text-emerald-500">✔</span> Proof of payment</li>
                <li class="flex items-center gap-1.5"><span class="text-emerald-500">✔</span> Has PNR &amp; price</li>
                <li class="flex items-center gap-1.5"><span class="text-red-400">✘</span> <span class="text-red-500 font-semibold">Cannot board with this</span></li>
              </ul>
            </div>
            <div class="bg-pink-50 border border-pink-200 rounded-lg p-3">
              <div class="font-bold text-pink-700 mb-2">🎫 Boarding Pass (after check-in)</div>
              <ul class="text-slate-500 space-y-1">
                <li class="flex items-center gap-1.5"><span class="text-emerald-500">✔</span> Has seat &amp; gate</li>
                <li class="flex items-center gap-1.5"><span class="text-emerald-500">✔</span> Has QR / barcode</li>
                <li class="flex items-center gap-1.5"><span class="text-green-600">✔</span> <span class="text-green-700 font-semibold">Required to board</span></li>
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