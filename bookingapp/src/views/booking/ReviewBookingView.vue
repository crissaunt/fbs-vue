<template>
  <div class="review-booking-container pb-20 lg:pb-0">
    <BookingStatusHeader />

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your booking details...</p>
    </div>

    <!-- No Data State -->
    <div v-else-if="!hasFlightData" class="no-data-message">
      <h3>No flight data found</h3>
      <p>Please go back and select a flight first.</p>
      <button @click="$router.push({ name: 'SearchFlights' })" class="btn-back">
        Back to Flight Search
      </button>
    </div>

    <!-- Main Content -->
    <div v-else class="container review-layout">
      <main class="main-content">
        <h2 class="page-title">Review Your Booking</h2>

        <div class="itinerary-header mb-8">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-lg border border-gray-100 shadow-sm">
            <div>
              <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Electronic Ticket Identification (PNR)</p>
              <h2 class="text-3xl font-mono font-black text-pink-500 tracking-tighter">{{ generatedPNR }}</h2>
            </div>
            <div class="text-right">
              <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Booking Status</p>
              <span class="px-3 py-1 bg-amber-50 text-amber-700 text-xs font-bold rounded-md border border-amber-100 uppercase">Awaiting Confirmation</span>
            </div>
          </div>
        </div>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">✈️</span>
            <h3>Flight Itinerary</h3>
            <span class="trip-type-badge" :class="{ 
              'round-trip': bookingStore.isRoundTrip, 
              'one-way': bookingStore.tripType === 'one_way',
              'multi-city': bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city'
            }">
              {{ 
                bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city' 
                  ? 'Multi-City' 
                  : (bookingStore.isRoundTrip ? 'Round Trip' : 'One Way') 
              }}
            </span>
          </div>
          
          <div class="space-y-4">
            <div v-for="(segment, index) in flightSegments" :key="index" class="boarding-pass-card bg-white rounded-lg border border-gray-100 shadow-sm overflow-hidden flex flex-col md:flex-row">
              <div class="pass-left p-6 flex-1 relative border-r border-dashed border-gray-200">
                <div class="absolute -top-3 -right-3 w-6 h-6 bg-gray-50 rounded-full"></div>
                <div class="absolute -bottom-3 -right-3 w-6 h-6 bg-gray-50 rounded-full"></div>
                
                <div class="flex items-center justify-between mb-6">
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-0.5 bg-gray-900 text-white text-[10px] font-bold rounded uppercase tracking-tighter">{{ segment.flight_number }}</span>
                    <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">{{ segment.label }}</span>
                  </div>
                  <span class="text-xs font-black text-gray-900 uppercase">Confirmed</span>
                </div>

                <div class="flex items-center justify-between gap-4">
                  <div class="text-center md:text-left">
                    <h4 class="text-3xl font-black text-gray-900 tracking-tighter">{{ segment.origin }}</h4>
                    <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">Departure</p>
                  </div>
                  
                  <div class="flex-1 flex flex-col items-center">
                    <div class="w-full border-t-2 border-dashed border-gray-200 relative">
                      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 px-2 bg-white">
                        <svg class="w-4 h-4 text-pink-500 rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                      </div>
                    </div>
                  </div>

                  <div class="text-center md:text-right">
                    <h4 class="text-3xl font-black text-gray-900 tracking-tighter">{{ segment.destination }}</h4>
                    <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">Arrival</p>
                  </div>
                </div>

                <div class="mt-8 grid grid-cols-2 md:grid-cols-3 gap-6">
                  <div>
                    <label class="text-[9px] font-bold text-gray-400 uppercase tracking-[0.2em] block mb-1">Departure Date</label>
                    <p class="text-xs font-bold text-gray-800">{{ formatDate(segment.departure_time) }}</p>
                  </div>
                  <div>
                    <label class="text-[9px] font-bold text-gray-400 uppercase tracking-[0.2em] block mb-1">Class & Fare</label>
                    <p class="text-xs font-bold text-gray-800 uppercase tracking-tighter">
                      {{ segment.class_type || 'Economy' }} 
                      <span v-if="bookingStore.fareFamilies[segment.key]" class="text-pink-600 ml-1">
                        ({{ bookingStore.fareFamilies[segment.key] === 'premium' ? 'Premium' : 'Basic' }})
                      </span>
                    </p>
                  </div>
                  <div>
                    <label class="text-[9px] font-bold text-gray-400 uppercase tracking-[0.2em] block mb-1">Gate/Terminal</label>
                    <p class="text-xs font-bold text-gray-800 uppercase tracking-tighter">Terminal 2</p>
                  </div>
                </div>
              </div>
              
              <div class="pass-right bg-pink-50/30 p-6 md:w-56 flex flex-col justify-center border-t md:border-t-0 md:border-l border-gray-100">
                <div class="space-y-4">
                  <div>
                    <label class="text-[9px] font-bold text-gray-400 uppercase tracking-[0.2em] block mb-1">Boarding Info</label>
                    <div class="flex items-center gap-2">
                      <div class="w-10 h-10 bg-white rounded-md flex items-center justify-center border border-pink-100">
                        <span class="text-sm font-black text-pink-500">B</span>
                      </div>
                      <p class="text-[11px] font-bold text-gray-900 leading-tight">Zone 3<br><span class="text-pink-600">Standard</span></p>
                    </div>
                  </div>
                  <div class="pt-4 mt-4 border-t border-pink-100/50">
                    <p class="text-[10px] font-mono font-bold text-pink-400 tracking-widest text-center truncate">BARCODE DATA: {{ segment.flight_number }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">👥</span>
            <h3>Passengers & Add-ons</h3>
          </div>
          
          <div v-for="(segment, index) in flightSegments" :key="'addons-' + index" class="review-card" :class="{ 'mt-3': index > 0 }">
            <div class="segment-header">
              <h4>{{ segment.label }} Add-ons</h4>
              <span class="flight-badge" :class="{ 'return': segment.isReturn, 'multi': segment.isMulti }">
                {{ segment.flight_number }}
              </span>
            </div>
            <table class="review-table">
              <thead>
                <tr>
                  <th>Passenger</th>
                  <th>Seat</th>
                  <th>Baggage</th>
                  <th>Meal</th>
                  <th>Assistance</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in bookingStore.passengers" :key="p.key">
                  <td>
                    <strong>{{ formatTitle(p.title) }} {{ p.firstName }} {{ p.lastName }}</strong>
                    <div class="sub-text">
                      {{ p.type }}
                      <span v-if="p.phDiscountType === 'senior'" class="text-xs text-pink-600 ml-1 font-bold">(Senior Citizen)</span>
                      <span v-if="p.phDiscountType === 'pwd'" class="text-xs text-pink-600 ml-1 font-bold">(PWD)</span>
                    </div>
                  </td>
                  <td>{{ getSeatLabel(p.key, segment.key) }}</td>
                  <td>{{ getBaggageLabel(p.key, segment.key) }}</td>
                  <td>{{ getMealLabel(p.key, segment.key) }}</td>
                  <td>{{ getAssistanceLabel(p.key, segment.key) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">📜</span>
            <h3>Fare Rules & Conditions</h3>
          </div>
          <div class="bg-gray-50 border border-gray-100 rounded-lg p-5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="flex items-start gap-3">
                <div class="w-2 h-2 rounded-full bg-red-400 mt-1.5 flex-shrink-0"></div>
                <div>
                  <p class="text-xs font-bold text-gray-800 uppercase">Cancellation / Refund</p>
                  <p class="text-[11px] text-gray-500 mt-0.5 leading-relaxed">This fare is non-refundable. Cancellations will result in forfeiture of the total amount unless travel insurance covers the reason.</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-2 h-2 rounded-full bg-amber-400 mt-1.5 flex-shrink-0"></div>
                <div>
                  <p class="text-xs font-bold text-gray-800 uppercase">Change Policy</p>
                  <p class="text-[11px] text-gray-500 mt-0.5 leading-relaxed">Changes allowed up to 24 hours before departure with a ₱2,500 fee plus any fare difference.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">📧</span>
            <h3>Contact Information</h3>
          </div>
          <div class="review-card contact-grid">
            <div class="contact-item">
              <label>Full Name</label>
              <p>{{ formatTitle(bookingStore.contactInfo.title) }} {{ bookingStore.contactInfo.firstName }} {{ bookingStore.contactInfo.lastName }}</p>
            </div>
            <div class="contact-item">
              <label>Email Address</label>
              <p>{{ bookingStore.contactInfo.email }}</p>
            </div>
            <div class="contact-item">
              <label>Phone Number</label>
              <p>{{ bookingStore.contactInfo.phone }}</p>
            </div>
          </div>
        </section>

        <div class="footer-nav">
          <button class="btn-back" @click="$router.back()">EDIT DETAILS</button>
          <button class="btn-continue" @click="confirmBooking" :disabled="isProcessing">
            <span v-if="isProcessing">Processing...</span>
            <span v-else>PROCEED TO PAYMENT</span>
          </button>
        </div>
      </main>

      <aside class="sidebar">
        <BookingTimer variant="sidebar" />
        <div class="summary-card sticky">
          <div class="summary-header">Payment Summary</div>
          <div class="summary-body">
            <!-- Flight Base Fares Breakdown -->
            <div class="flight-base-summary" v-if="hasFlightData">
              <!-- Adults Breakdown -->
              <div class="price-line" v-if="bookingStore.passengerCount.adults > 0">
                <span>{{ bookingStore.passengerCount.adults }} Adult(s) (Total Base Fare)</span> 
                <AnimatedNumber :value="bookingStore.grandTotalForAdults" prefix="₱" />
              </div>
              
              <!-- Children Breakdown -->
              <div class="price-line" v-if="bookingStore.passengerCount.children > 0">
                <span>{{ bookingStore.passengerCount.children }} Child(ren) (Total Base Fare)</span> 
                <AnimatedNumber :value="bookingStore.grandTotalForChildren" prefix="₱" />
              </div>
              
              <!-- Infants Breakdown (50% Base Fare) -->
              <div class="price-line infant-line" v-if="bookingStore.passengerCount.infants > 0">
                <span>{{ bookingStore.passengerCount.infants }} Infant(s) (50% Base Fare)</span> 
                <AnimatedNumber :value="bookingStore.grandTotalForInfants" prefix="₱" />
              </div>

              
              <!-- Granular Taxes Breakdown -->
              <div v-if="backendTaxDetails && Object.keys(backendTaxDetails).length > 0">
                <div v-for="(amount, label) in backendTaxDetails" :key="label" class="price-line tax-detail-line">
                  <span class="tax-label">{{ label }}</span>
                  <AnimatedNumber :value="amount" prefix="₱" />
                </div>
              </div>
              
              <!-- Fallback to single line if no breakdown yet -->
              <div v-else class="price-line taxes-line">
                <span>Verification / Taxes & Fees (VAT)</span>
                <AnimatedNumber :value="bookingStore.totalTaxes" prefix="₱" />
              </div>
            </div>

            <!-- Add-ons -->
            <div class="addons-summary">
              <div class="price-line" v-if="totalSeatsPrice > 0">
                <span>Seat Selection</span>
                <AnimatedNumber :value="totalSeatsPrice" prefix="₱" />
              </div>
              <div class="price-line" v-if="totalBaggagePrice > 0">
                <span>Extra Baggage</span>
                <AnimatedNumber :value="totalBaggagePrice" prefix="₱" />
              </div>
              <div class="price-line" v-if="totalMealsPrice > 0">
                <span>Meal Selection</span>
                <AnimatedNumber :value="totalMealsPrice" prefix="₱" />
              </div>
              <div class="price-line" v-if="totalAssistancePrice > 0">
                <span>Special Assistance</span>
                <AnimatedNumber :value="totalAssistancePrice" prefix="₱" />
              </div>
              <div class="price-line" v-if="insurancePrice > 0">
                <span>Travel Insurance</span>
                <AnimatedNumber :value="insurancePrice" prefix="₱" />
              </div>
            </div>

            <hr>
            <div class="total-row">
              <span>Grand Total</span>
              <span class="final-amt">
                <AnimatedNumber :value="grandTotal" prefix="₱" />
              </span>
            </div>
            <div class="passenger-count">
              <small>{{ payingPassengerCount }} paying passengers</small>
            </div>
          </div>
        </div>
      </aside>
    </div>

      @next="handleConfirmBooking" 
    />

    <LoadingOverlay 
      :show="isProcessing" 
      title="Finalizing Your Booking"
      subtitle="Just a few seconds while we create your official reservation."
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import { addonService } from '@/services/booking/addonService';
import { bookingService } from '@/services/booking/bookingService';
import { useNotificationStore } from '@/stores/notification';
import BookingTimer from '@/components/booking/BookingTimer.vue';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import MobileBookingFooter from '@/components/booking/MobileBookingFooter.vue';
import AnimatedNumber from '@/components/common/AnimatedNumber.vue';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

const bookingStore = useBookingStore();
const router = useRouter();
const notificationStore = useNotificationStore();

const isLoading = ref(true);
const isProcessing = ref(false);
const baggageOptions = ref([]);
const mealOptions = ref([]);
const assistanceOptions = ref([]);
const generatedPNR = ref(Math.random().toString(36).substring(2, 8).toUpperCase());

// Backend Price Data (kept for potential future use but no longer used for display)
const backendTotal = ref(null);
const backendBreakdown = ref(null);
const backendTaxDetails = ref(null);
const isCalculatingPrice = ref(false);

onMounted(async () => {
  try {

    bookingStore.loadBookingFromStorage();
    
    // Debug: Log current store state
    console.log('📊 ========== PINIA STORE STATE ==========');
    console.log('🎫 Trip Type:', bookingStore.tripType, '(Round Trip:', bookingStore.isRoundTrip + ')');
    console.log('📋 Booking ID:', bookingStore.booking_id);
    console.log('📋 Booking Reference:', bookingStore.booking_reference);
    console.log('📋 Booking Status:', bookingStore.booking_status);
    console.log('💰 Booking Total:', bookingStore.booking_total);
    // Debug: Log current store state
    console.log('📊 ========== PINIA STORE STATE ==========');
    console.log('🎫 Trip Type:', bookingStore.tripType, '(Round Trip:', bookingStore.isRoundTrip + ')');
    
    // Flight data
    console.log('✈️ Outbound Flight:', bookingStore.selectedOutbound);
    console.log('🔄 Return Flight:', bookingStore.selectedReturn);
    
    // Passenger data
    console.log('👥 Passenger Count:', bookingStore.passengerCount);
    console.log('📋 Passengers:', JSON.parse(JSON.stringify(bookingStore.passengers)));
    
    // Contact info
    console.log('📞 Contact Info:', JSON.parse(JSON.stringify(bookingStore.contactInfo)));
    
    // Add-ons (deep clone to avoid reactivity issues)
    console.log('🎯 Add-ons Structure:', JSON.parse(JSON.stringify(bookingStore.addons)));
    
    // Financial calculations
    console.log('💰 Financial Summary:');
    console.log('  - Combined Base Price:', bookingStore.combinedBasePrice);
    console.log('  - Total Add-ons Price:', bookingStore.totalAddonsPrice);
    console.log('  - Grand Total (computed):', bookingStore.grandTotal);
    console.log('  - Booking Total (stored):', bookingStore.booking_total);
    
    // Session info
    const sessionStatus = bookingStore.checkSession();
    console.log('⏰ Session Status:', sessionStatus);
    
    console.log('📊 ========== END PINIA STORE ==========');

    // Rest of your existing code...
    bookingStore.migrateAddonsToNewFormat();
    
    const airlineId = bookingStore.selectedOutbound?.airline_code || bookingStore.selectedOutbound?.airline;
    if (!airlineId) {
      isLoading.value = false;
      return;
    }

    const results = await Promise.allSettled([
      addonService.getBaggageOptions(airlineId),
      addonService.getMealOptions(airlineId),
      addonService.getAssistanceServices(airlineId)
    ]);

    if (results[0].status === 'fulfilled') {
      const data = results[0].value.data;
      baggageOptions.value = Array.isArray(data) ? data : (data?.results || []);
    }
    if (results[1].status === 'fulfilled') {
      const data = results[1].value.data;
      mealOptions.value = Array.isArray(data) ? data : (data?.results || []);
    }
    if (results[2].status === 'fulfilled') {
      const data = results[2].value.data;
      assistanceOptions.value = Array.isArray(data) ? data : (data?.results || []);
    }

    // Fetch backend price to show authoritative breakdown
    await fetchBackendPrice();

  } catch (error) {
    console.error("Review page data fetch error:", error);
  } finally {
    isLoading.value = false;
  }
});

// Not called anymore — kept for reference in case we need it later.
const fetchBackendPrice = async () => {
  if (!hasFlightData.value) return;
  
  isCalculatingPrice.value = true;
  try {
    const response = await bookingService.calculatePrice(bookingStore);
    if (response.success) {
      backendTotal.value = response.total_amount;
      backendBreakdown.value = response.breakdown;
      backendTaxDetails.value = response.tax_details || null;
      console.log('✅ Backend price confirmed:', response.total_amount);
      console.log('📑 Tax Details:', backendTaxDetails.value);
    }
  } catch (error) {
    console.error('Error fetching backend price:', error);
  } finally {
    isCalculatingPrice.value = false;
  }
};

const taxesLine = computed(() => {
  if (!backendBreakdown.value) return null;
  return backendBreakdown.value.taxes || 0;
});

const insuranceLine = computed(() => {
  if (!backendBreakdown.value) return null;
  return backendBreakdown.value.insurance || 0;
});

// Helper functions
const getItemById = (list, id) => {
  if (!id || !list) return null;
  return list.find(item => item.id === id);
};

const getOptionById = (list, id) => {
  if (!id || !list) return null;
  return list.find(item => item.id == id);
};

const getBaggageLabel = (passengerKey, segment = 'depart') => {
  const p = bookingStore.passengers.find(p => p.key === passengerKey);
  if (p?.type === 'Infant') return 'Incl. in Adult Allowance';

  const isPremium = bookingStore.fareFamilies[segment] === 'premium';
  const baggage = bookingStore.addons?.baggage?.[segment]?.[passengerKey];
  
  if (!baggage) {
    return isPremium ? 'Included (20kg)' : 'Standard (7kg hand-carry only)';
  }
  
  if (typeof baggage === 'object' && baggage.formatted_weight) {
    const price = isPremium && parseFloat(baggage.weight_kg || 0) <= 20 ? 0 : parseFloat(baggage.price);
    return `${baggage.formatted_weight} (₱${price.toLocaleString()})`;
  }
  
  const option = baggageOptions.value.find(o => o.id == baggage);
  if (option) {
    const price = isPremium && parseFloat(option.weight_kg || 0) <= 20 ? 0 : parseFloat(option.price);
    return `${option.formatted_weight} (₱${price.toLocaleString()})`;
  }
  
  return isPremium ? 'Included (20kg)' : 'Standard (7kg hand-carry only)';
};

const getMealLabel = (passengerKey, segment = 'depart') => {
  const p = bookingStore.passengers.find(p => p.key === passengerKey);
  if (p?.type === 'Infant') return 'Not Available';

  const meal = bookingStore.addons?.meals?.[segment]?.[passengerKey];
  if (!meal) return 'No meal';
  
  if (typeof meal === 'object' && meal.name) {
    return meal.name;
  }
  
  const option = mealOptions.value.find(m => m.id == meal);
  return option ? option.name : 'Pre-ordered Meal';
};

const getAssistanceLabel = (passengerKey, segment = 'depart') => {
  const p = bookingStore.passengers.find(p => p.key === passengerKey);
  if (p?.type === 'Infant') return 'Not Available';

  const assistanceId = bookingStore.addons?.wheelchair?.[segment]?.[passengerKey];
  if (!assistanceId || !Array.isArray(assistanceOptions.value)) return 'No assistance';
  
  const option = assistanceOptions.value.find(a => a.id == assistanceId);
  return option ? option.name : 'Special Assistance';
};

const getSeatLabel = (passengerKey, segmentKey = 'depart') => {
  const p = bookingStore.passengers.find(p => p.key === passengerKey);
  if (p?.type === 'Infant') {
    const adultKey = bookingStore.infantAdultMapping[passengerKey];
    if (adultKey && bookingStore.addons?.seats?.[segmentKey]?.[adultKey]) {
      const adultSeat = bookingStore.addons.seats[segmentKey][adultKey];
      return `Lap (${adultSeat.seat_code})`;
    }
    return 'On Lap';
  }

  const isPremium = bookingStore.fareFamilies[segmentKey] === 'premium';
  const seat = bookingStore.addons?.seats?.[segmentKey]?.[passengerKey] || bookingStore.addons?.seats?.[passengerKey];
  
  if (!seat) return 'Not selected';
  
  const seatCode = seat.seat_code || 'N/A';
  const price = isPremium ? 0 : (parseFloat(seat.seat_price) || 0);
  
  return `${seatCode} (₱${price.toLocaleString()})`;
};

// Computed Properties
const flightSegments = computed(() => {
  const tripType = bookingStore.tripType;
  
  const getAirportLabel = (airport) => {
    if (!airport) return 'N/A';
    if (typeof airport === 'string') return airport;
    // Check if it's an object with city or name
    return airport.city || airport.name || airport.code || 'N/A';
  };

  if (tripType === 'multi_city' || tripType === 'multi-city') {
    return bookingStore.multiCitySegments.map((seg, idx) => ({
      key: idx.toString(),
      label: `Flight ${idx + 1}`,
      origin: getAirportLabel(seg.origin),
      destination: getAirportLabel(seg.destination),
      flight_number: seg.selectedFlight?.flight_number || 'N/A',
      departure_time: seg.selectedFlight?.departure_time,
      class_type: seg.selectedFlight?.class_type,
      price: seg.selectedFlight?.price || 0,
      isMulti: true
    }));
  }

  const segments = [];
  if (bookingStore.selectedOutbound) {
    segments.push({
      key: 'depart',
      label: 'Depart',
      origin: getAirportLabel(bookingStore.selectedOutbound.origin),
      destination: getAirportLabel(bookingStore.selectedOutbound.destination),
      flight_number: bookingStore.selectedOutbound.flight_number,
      departure_time: bookingStore.selectedOutbound.departure_time,
      class_type: bookingStore.selectedOutbound.class_type,
      price: bookingStore.selectedOutbound.price || 0,
      isReturn: false
    });
  }
  
  if (bookingStore.isRoundTrip && bookingStore.selectedReturn) {
    segments.push({
      key: 'return',
      label: 'Return',
      origin: getAirportLabel(bookingStore.selectedReturn.origin),
      destination: getAirportLabel(bookingStore.selectedReturn.destination),
      flight_number: bookingStore.selectedReturn.flight_number,
      departure_time: bookingStore.selectedReturn.departure_time,
      class_type: bookingStore.selectedReturn.class_type,
      price: bookingStore.selectedReturn.price || 0,
      isReturn: true
    });
  }
  
  return segments;
});

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  try {
    return new Date(dateStr).toLocaleString('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid date';
  }
};

const formatTitle = (titleCode) => {
  if (!titleCode) return '';
  const map = {
    'MR': 'Mr.',
    'MRS': 'Mrs.',
    'MS': 'Ms.',
    'CHD': 'Mstr/Miss',
    'INF': 'Infant'
  };
  return map[titleCode.toUpperCase()] || titleCode;
};

// Computed Properties
const hasFlightData = computed(() => {
  if (bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city') {
    return bookingStore.multiCitySegments && 
           bookingStore.multiCitySegments.length > 0 && 
           bookingStore.multiCitySegments.every(seg => seg.selectedFlight);
  }
  const outbound = bookingStore.selectedOutbound;
  return !!outbound && typeof outbound === 'object' && 'price' in outbound;
});

const payingPassengerCount = computed(() => bookingStore.payingPassengerCount);
const departBaseFare = computed(() => bookingStore.departBaseFare);
const returnBaseFare = computed(() => bookingStore.returnBaseFare);
const totalSeatsPrice = computed(() => bookingStore.totalSeatsPrice);
const totalBaggagePrice = computed(() => bookingStore.totalBaggagePrice);
const totalMealsPrice = computed(() => bookingStore.totalMealsPrice);
const totalAssistancePrice = computed(() => bookingStore.totalAssistancePrice);
const insurancePrice = computed(() => bookingStore.insurancePrice);
const combinedBasePriceTotal = computed(() => bookingStore.combinedBasePriceTotal);

const taxesPrice = computed(() => {
  // If backend provided taxes, use them. Otherwise estimate 12%
  if (backendBreakdown.value && backendBreakdown.value.taxes) {
    return parseFloat(backendBreakdown.value.taxes);
  }
  return bookingStore.totalTaxes;
});

const grandTotal = computed(() => {
  // Use backend confirmed total if available
  if (backendTotal.value !== null && !isNaN(backendTotal.value)) {
    return backendTotal.value;
  }
  // Otherwise use the store's computed grandTotal as fallback
  return bookingStore.grandTotal;
});

// Validation function
const validateBooking = () => {
  const errors = [];
  const tripType = bookingStore.tripType;
  
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    bookingStore.multiCitySegments.forEach((seg, idx) => {
      if (!seg.selectedFlight) {
        errors.push(`Please select a flight for Segment ${idx + 1}`);
      }
    });
  } else {
    if (!bookingStore.selectedOutbound) {
      errors.push('Please select an outbound flight');
    }
    
    if (bookingStore.isRoundTrip && !bookingStore.selectedReturn) {
      errors.push('Please select a return flight for round trip');
    }
  }
  
  if (!bookingStore.passengers || bookingStore.passengers.length === 0) {
    errors.push('Please add passenger information');
  }
  
  // Validate each passenger
  bookingStore.passengers.forEach((p, index) => {
    const passengerNum = index + 1;
    
    if (!p.firstName || p.firstName.trim() === '') {
      errors.push(`Passenger ${passengerNum}: First name is required`);
    }
    
    if (!p.lastName || p.lastName.trim() === '') {
      errors.push(`Passenger ${passengerNum}: Last name is required`);
    }
    
    if (!p.title) {
      errors.push(`Passenger ${passengerNum}: Title (Mr/Ms/Mrs) is required`);
    }
    
    if (!p.dateOfBirth) {
      errors.push(`Passenger ${passengerNum}: Date of birth is required`);
    } else {
      const date = new Date(p.dateOfBirth);
      if (isNaN(date.getTime())) {
        errors.push(`Passenger ${passengerNum}: Invalid date of birth format`);
      }
    }
    
    if (!p.key) {
      errors.push(`Passenger ${passengerNum}: Missing passenger key`);
    }
  });
  
  // Validate contact info
  if (!bookingStore.contactInfo?.firstName || bookingStore.contactInfo?.firstName.trim() === '') {
    errors.push('Contact person first name is required');
  }
  
  if (!bookingStore.contactInfo?.lastName || bookingStore.contactInfo?.lastName.trim() === '') {
    errors.push('Contact person last name is required');
  }
  
  if (!bookingStore.contactInfo?.email || !/\S+@\S+\.\S+/.test(bookingStore.contactInfo.email)) {
    errors.push('Please enter a valid email address');
  }
  
  if (!bookingStore.contactInfo?.phone || bookingStore.contactInfo.phone.length < 7) {
    errors.push('Please enter a valid phone number');
  }
  
  return errors;
};

// Helper to get default date of birth
const getDefaultDOB = () => {
  const date = new Date();
  date.setFullYear(date.getFullYear() - 20);
  return date.toISOString().split('T')[0];
};

// Prepare passengers for submission
const preparePassengersForSubmission = () => {
  console.log('🔍 Preparing passengers for submission...');
  
  const preparedPassengers = bookingStore.passengers.map((p, index) => {
    let dateOfBirth = p.dateOfBirth;
    if (dateOfBirth) {
      const parsedDate = new Date(dateOfBirth);
      if (isNaN(parsedDate.getTime())) {
        dateOfBirth = getDefaultDOB();
      } else {
        dateOfBirth = parsedDate.toISOString().split('T')[0];
      }
    } else {
      dateOfBirth = getDefaultDOB();
    }
    
    return {
      key: p.key || `pax_${index + 1}`,
      firstName: p.firstName || '',
      lastName: p.lastName || '',
      middleName: p.middleName || '',
      title: p.title || 'MR',
      dateOfBirth: dateOfBirth,
      nationality: p.nationality || 'Philippines',
      passportNumber: p.passportNumber || '',
      phDiscountType: p.phDiscountType || 'none',
      phDiscountId: p.phDiscountId || '',
      type: p.type || 'Adult'
    };
  });
  
  console.log('✅ Prepared passengers:', preparedPassengers);
  return preparedPassengers;
};


const confirmBooking = async () => {
  isProcessing.value = true;
  
  try {
    // 1. Prepare data using your existing formatBookingData
    const bookingData = bookingService.formatBookingData(bookingStore);
    
    // 2. Check for an existing ID (from store or local storage)
    const existingBookingId = bookingStore.booking_id || 
                             JSON.parse(localStorage.getItem('current_booking'))?.id;

    let response;
    
    if (existingBookingId) {
      // SCENARIO: User went back from Add-ons/Review to change details
      console.log('🔄 Updating existing booking:', existingBookingId);
      response = await bookingService.updateBooking(existingBookingId, bookingData);
    } else {
      // SCENARIO: First time clicking "Confirm"
      console.log('🆕 Creating new booking...');
      response = await bookingService.createBooking(bookingData);
    }
    
    console.log('📊 FULL BOOKING RESPONSE:', response);
    
    if (response.success) {
      // 3. Save ALL booking data to the store using saveBookingConfirmation
      bookingStore.saveBookingConfirmation({
        booking_id: response.booking_id,
        booking_reference: response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`,
        status: response.status || 'pending',
        total_amount: response.total_amount || bookingStore.grandTotal
      });
      
      // 4. Also set individual fields (for backward compatibility)
      bookingStore.setBookingId(response.booking_id);
      bookingStore.booking_reference = response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`;
      bookingStore.booking_status = response.status || 'pending';
      
      // 5. Persist to LocalStorage so a page refresh doesn't lose the ID
      localStorage.setItem('current_booking', JSON.stringify({
        id: response.booking_id,
        reference: response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`,
        total: response.total_amount || bookingStore.grandTotal,
        status: response.status || 'pending'
      }));
      
      console.log('✅ Booking saved to store:', {
        id: bookingStore.booking_id,
        reference: bookingStore.booking_reference,
        status: bookingStore.booking_status,
        total: bookingStore.booking_total
      });
      
      // 6. Move to Payment — pass confirmed amount so Payment doesn't re-derive it.
      const confirmedAmount = bookingStore.booking_total || bookingStore.grandTotal;
      router.push({ 
        name: 'Payment', 
        query: { 
          bookingId: response.booking_id,
          bookingReference: response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`,
          amount: confirmedAmount
        } 
      });
    }
  } catch (error) {
    console.error("Booking critical failure:", error);
    // Global axios interceptor handles specific mapping/toast
  } finally {
    isProcessing.value = false;
  }
};

/**
 * Extracted error handler to keep confirmBooking clean
 */
const handleBookingError = (error) => {
  let errorMessage = 'Failed to process booking. Please try again.';
  
  if (error?.response?.data?.errors) {
    errorMessage = 'Validation errors:\n' + 
      Object.entries(error.response.data.errors)
        .map(([field, errs]) => `• ${field}: ${Array.isArray(errs) ? errs.join(', ') : errs}`)
        .join('\n');
  } else if (typeof error === 'string') {
    errorMessage = error;
  }
  
  notificationStore.error(errorMessage);
};
</script>



<style scoped>
.pal-bg { 
  background: #f4f7f9; 
  min-height: 100vh; 
  padding: 40px 0; 
}

.review-layout { 
  display: grid; 
  grid-template-columns: 1fr 350px; 
  gap: 30px; 
  max-width: 1100px; 
  margin: 0 auto; 
}

.page-title { 
  color: #003870; 
  font-weight: 800; 
  margin-bottom: 25px; 
  font-size: 1.8rem;
}

.review-section { 
  margin-bottom: 30px; 
}

.section-header { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  margin-bottom: 15px; 
}

.section-header h3 { 
  color: #003870; 
  margin: 0; 
  font-size: 1.2rem; 
}

.review-card { 
  background: white; 
  border-radius: 12px; 
  padding: 25px; 
  box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
  border: 1px solid #eee; 
}

.review-card.no-padding { 
  padding: 0; 
  overflow: hidden; 
}

.badge { 
  background: #003870; 
  color: white; 
  padding: 2px 8px; 
  border-radius: 4px; 
  font-size: 0.7rem; 
  text-transform: uppercase; 
  margin-right: 10px; 
}

.badge.return { 
  background: #d11241; 
}
 
.badge.multi {
  background: #FF579A;
}

.trip-type-badge.multi-city {
  background: #FFE6F1;
  color: #FF579A;
  border: 2px solid #FF579A;
}

.flight-summary { 
  padding-bottom: 15px; 
}

.detail-grid { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  margin-top: 10px; 
  color: #555; 
}

.review-table { 
  width: 100%; 
  border-collapse: collapse; 
}

.review-table th { 
  background: #f8f9fa; 
  text-align: left; 
  padding: 12px 20px; 
  font-size: 0.85rem; 
  color: #666; 
}

.review-table td { 
  padding: 15px 20px; 
  border-top: 1px solid #eee; 
  font-size: 0.95rem; 
}

.sub-text { 
  font-size: 0.75rem; 
  color: #888; 
}

.contact-grid { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  gap: 20px; 
}

.contact-item label { 
  display: block; 
  font-size: 0.75rem; 
  color: #888; 
  text-transform: uppercase; 
}

.contact-item p { 
  margin: 5px 0 0; 
  font-weight: 600; 
  color: #333; 
}

/* Sticky Sidebar */
.summary-card { 
  background: white; 
  border-radius: 12px; 
  box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
}

.sticky { 
  position: sticky; 
  top: 20px; 
}

.summary-header { 
  background: #003870; 
  color: white; 
  padding: 20px; 
  text-align: center; 
  font-weight: 700; 
  border-radius: 12px 12px 0 0; 
}

.summary-body { 
  padding: 20px; 
}

.price-line { 
  display: flex; 
  justify-content: space-between; 
  margin-bottom: 10px; 
  font-size: 0.9rem; 
}

.total-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-top: 15px; 
  font-weight: 700; 
}

.final-amt { 
  color: #d11241; 
  font-size: 1.4rem; 
}

.footer-nav { 
  display: flex; 
  justify-content: space-between; 
  margin-top: 30px; 
}

.btn-back { 
  padding: 12px 25px; 
  border: 1px solid #ccc; 
  background: white; 
  border-radius: 6px; 
  cursor: pointer; 
  font-weight: 600;
}

.btn-continue { 
  padding: 12px 40px; 
  background: #d11241; 
  color: white; 
  border: none; 
  border-radius: 6px; 
  font-weight: 700; 
  cursor: pointer; 
}

.btn-continue:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Loading and Error States */
.loading-state, .no-data-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  padding: 40px;
}

.loading-state p {
  color: #666;
  font-size: 1.2rem;
  margin-top: 15px;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #003870;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data-message {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  margin: 40px auto;
  padding: 40px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.no-data-message h3 {
  color: #003870;
  margin-bottom: 15px;
  font-size: 1.5rem;
}

.no-data-message p {
  color: #666;
  margin-bottom: 25px;
  font-size: 1rem;
}

.no-data-message .btn-back {
  background: #003870;
  color: white;
  border: none;
  padding: 12px 30px;
}

/* Responsive Styles */
@media (max-width: 768px) {
  .review-layout {
    grid-template-columns: 1fr;
  }
  
  .contact-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .footer-nav {
    flex-direction: column;
    gap: 10px;
  }
  
  .footer-nav button {
    width: 100%;
  }
  
  .review-table {
    display: block;
    overflow-x: auto;
  }
}

@media (max-width: 480px) {
  .pal-bg {
    padding: 20px 0;
  }
  
  .review-card {
    padding: 15px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}

.trip-type-badge {
  margin-left: auto;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.trip-type-badge.round-trip {
  background: #e3f2fd;
  color: #1565c0;
  border: 1px solid #1565c0;
}

.trip-type-badge.one-way {
  background: #f3e5f5;
  color: #7b1fa2;
  border: 1px solid #7b1fa2;
}

.segment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.segment-header h4 {
  margin: 0;
  color: #003870;
  font-size: 1.1rem;
}

.flight-badge {
  background: #003870;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.flight-badge.return {
  background: #d11241;
}

.flight-base-summary {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #eee;
}

.flight-base-summary .price-line {
  font-size: 0.85rem;
  color: #666;
}

.addons-summary {
  margin-top: 10px;
}

.passenger-count {
  text-align: center;
  margin-top: 10px;
  color: #888;
  font-size: 0.85rem;
}

.tax-detail-line {
  font-size: 0.85rem;
  color: #666;
  padding-left: 1rem;
  margin-top: 4px;
}

.tax-label {
  font-style: italic;
  opacity: 0.8;
}

.taxes-line {
  font-weight: 600;
  margin-top: 10px;
}

.mt-3 {
  margin-top: 15px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .segment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .trip-type-badge {
    margin-left: 0;
    align-self: flex-start;
  }
}

/* Price Loading Styles */
.price-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 10px;
  text-align: center;
}

.price-loading p {
  margin-top: 15px;
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
}

.loading-dots {
  display: flex;
  gap: 6px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background-color: #003870;
  border-radius: 50%;
  display: inline-block;
  animation: dot-pulse 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes dot-pulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}
</style>