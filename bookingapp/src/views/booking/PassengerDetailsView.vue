<template>
  <div class="min-h-screen bg-slate-50 pb-20 lg:pb-10 font-sans">
    <BookingStatusHeader />
    
    <div class="max-w-[1500px] mx-auto px-5 lg:px-10 mt-10">
      <div class="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-8">
        
        <!-- Main Content -->
        <main class="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-8 items-start">
          
          <!-- Left Sidebar - Passenger Selection -->
          <PassengerSidebar 
            :total-travelers="totalTravelers"
            :active-index="activeIndex"
            :infant-count="infantCount"
            :completed-count="completedPassengersCount"
            :completion-percentage="completionPercentage"
            :all-infants-assigned="allInfantsAssigned"
            :unassigned-infants-count="unassignedInfantsCount"
            :is-passenger-complete="isPassengerComplete"
            :has-passenger-error="hasPassengerError"
            :get-passenger-type="getPassengerType"
            :get-infant-adult-name="getInfantAdultName"
            @select="handleTabChange"
          />

          <!-- Forms Content Area -->
          <div class="flex flex-col gap-8">
            <!-- Header -->
            <div class="flex flex-col sm:flex-row justify-between items-start border-b border-slate-200 pb-5 gap-4">
              <h1 class="text-2xl font-bold text-slate-900">Passenger Details</h1>
              <div class="text-right sm:text-right">
                <span class="block text-[11px] text-slate-500 mb-1">Currently editing:</span>
                <span class="text-lg font-bold text-rose-500 flex items-center gap-3">
                  Passenger {{ activeIndex }} - {{ getPassengerType(activeIndex) }}
                  
                  <span v-if="getPassengerType(activeIndex) === 'Infant' && getInfantAdultName(activeIndex)" class="text-sm font-normal text-slate-500 ml-2">
                    (with {{ getInfantAdultName(activeIndex) }})
                  </span>
                </span>
              </div>
            </div>

            <div class="flex flex-col gap-4">
              <!-- Passenger Information -->
              <div class="bg-white rounded-lg p-6 border border-slate-200 shadow-sm">
                <h2 class="text-xl font-bold text-slate-900 mb-1">Personal Information</h2>
                <p class="text-[11px] text-slate-500 mb-6">Please enter details exactly as they appear on official ID</p>
                
                <div class="mb-8">
                  <div v-for="n in totalTravelers" :key="'form-'+n">
                    <div v-show="activeIndex === n">
                      <PassengerForm 
                        :ref="el => { if (el) passengerFormRefs[`pax_${n}`] = el }"
                        :type="getPassengerType(n)" 
                        :index="n"
                        :show-validation="showValidation"
                        :adult-passengers="availableAdultsForInfant(n)"
                        @update="(data) => updatePassengerData(getPassengerType(n), n, data)"
                        @validation="handlePassengerValidation"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Contact Information -->
              <ContactForm 
                v-model="contact"
                :show-validation="showValidation"
                :passenger1="passengers.find(p => p.key === 'pax_1')"
              />

              <!-- Navigation -->
              <div class="flex flex-col sm:flex-row justify-between items-center pt-6 border-t border-slate-200 gap-4">
                <div class="flex gap-3 w-full sm:w-auto">
                  <button 
                    v-if="activeIndex > 1"
                    type="button" 
                    class="flex-1 sm:flex-none py-3 px-5 border border-slate-300 bg-white rounded-md text-sm font-medium text-slate-600 hover:border-slate-400 hover:text-slate-800 transition-colors"
                    @click="handleTabChange(activeIndex - 1)"
                  >
                    ← Previous
                  </button>
                  
                  <button 
                    v-if="activeIndex < totalTravelers" 
                    type="button" 
                    class="flex-1 sm:flex-none py-3 px-5 border border-rose-500 text-rose-500 bg-white rounded-md text-sm font-medium hover:bg-rose-500 hover:text-white transition-all"
                    @click="goToNextGuest"
                  >
                    Next →
                  </button>
                </div>
                
                <button 
                  type="button" 
                  class="w-full sm:w-auto py-3.5 px-8 bg-rose-500 text-white rounded-md text-sm font-bold hover:bg-rose-600 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                  @click="handleContinueToAddons"
                  :disabled="isSaving"
                >
                  <span v-if="isSaving">Saving...</span>
                  <span v-else>Continue to Add-ons</span>
                </button>
              </div>
            </div>
          </div>
        </main>

        <!-- Right Sidebar - Booking Summary -->
        <aside class="sticky top-10 h-fit space-y-6">
          <BookingTimer variant="sidebar" />
          <BookingSummaryCard 
            :is-multi-city="bookingStore.isMultiCity"
            :multi-city-segments="bookingStore.multiCitySegments"
            :selected-flight="selectedFlight"
            :selected-return="selectedReturn"
            :is-round-trip="isRoundTrip"
            :adult-count="adultCount"
            :child-count="childCount"
            :infant-count="infantCount"
            :adult-total="bookingStore.grandTotalForAdults"
            :child-total="bookingStore.grandTotalForChildren"
            :infant-total="bookingStore.grandTotalForInfants"
            :total-amount="calculateTotal()"
          />
        </aside>
      </div>
    </div>
    
    <MobileBookingFooter 
      button-text="Continue to Add-ons" 
      :loading="isSaving"
      @next="handleContinueToAddons" 
    />

    <LoadingOverlay 
      :show="isSaving" 
      title="Saving Traveler Details"
      subtitle="Please wait while we validate and save your information."
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch, nextTick } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useNotificationStore } from '@/stores/notification';
import { useRouter } from 'vue-router';
import PassengerForm from '@/components/booking/PassengerForm.vue';
import BookingTimer from '@/components/booking/BookingTimer.vue';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import MobileBookingFooter from '@/components/booking/MobileBookingFooter.vue';
import PassengerSidebar from '@/components/booking/PassengerSidebar.vue';
import ContactForm from '@/components/booking/ContactForm.vue';
import BookingSummaryCard from '@/components/booking/BookingSummaryCard.vue';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();
const router = useRouter();

// --- STATE ---
const activeIndex = ref(1);
const passengers = ref([]);
const showValidation = ref(false);
const isSaving = ref(false);
const passengerValidation = ref({});
const passengerFormRefs = ref({});

const contact = ref({ 
  title: bookingStore.contactInfo.title || '',
  firstName: bookingStore.contactInfo.firstName || '', 
  middleName: bookingStore.contactInfo.middleName || '',
  lastName: bookingStore.contactInfo.lastName || '', 
  email: bookingStore.contactInfo.email || '', 
  phone: bookingStore.contactInfo.phone || '' 
});

// --- COMPUTED ---
const selectedFlight = computed(() => bookingStore.selectedOutbound);
const selectedReturn = computed(() => bookingStore.selectedReturn); 
const isRoundTrip = computed(() => bookingStore.isRoundTrip); 
const adultCount = computed(() => bookingStore.passengerCount.adults || 1);
const childCount = computed(() => bookingStore.passengerCount.children || 0);
const infantCount = computed(() => bookingStore.passengerCount.infants || 0);
const totalTravelers = computed(() => adultCount.value + childCount.value + infantCount.value);

// Infant assignment tracking
const infantAdultMapping = ref({});

// Adult passengers for infant assignment
const adultPassengers = computed(() => {
  return passengers.value.filter(p => p.type === 'Adult');
});

const allInfantsAssigned = computed(() => {
  const infants = passengers.value.filter(p => p.type === 'Infant');
  if (infants.length === 0) return true;
  return infants.every(infant => infantAdultMapping.value[infant.key] && adultPassengers.value.some(adult => adult.key === infantAdultMapping.value[infant.key]));
});

const unassignedInfantsCount = computed(() => {
  const infants = passengers.value.filter(p => p.type === 'Infant');
  return infants.filter(infant => !infantAdultMapping.value[infant.key]).length;
});

const isValidEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
};

const isValidPhone = (phone) => {
  if (!phone) return false;
  let digitsOnly = phone.replace(/\D/g, '');
  if (digitsOnly.startsWith('0')) digitsOnly = digitsOnly.substring(1);
  return digitsOnly.length === 10;
};

const completedPassengersCount = computed(() => {
  let count = 0;
  for (let i = 1; i <= totalTravelers.value; i++) {
    if (isPassengerComplete(i)) count++;
  }
  return count;
});

const completionPercentage = computed(() => {
  return totalTravelers.value > 0 ? (completedPassengersCount.value / totalTravelers.value) * 100 : 0;
});

const hasPassengerError = (index) => {
  return passengerValidation.value[`pax_${index}`] === false && showValidation.value;
};

// --- METHODS ---
const getPassengerType = (n) => {
  if (n <= adultCount.value) return 'Adult';
  if (n <= adultCount.value + childCount.value) return 'Child';
  return 'Infant';
};

const getInfantAdultName = (infantIndex) => {
  const infantKey = `pax_${infantIndex}`;
  const adultKey = infantAdultMapping.value[infantKey];
  if (!adultKey) return null;
  const adultNumber = adultKey.replace('pax_', '');
  const adult = passengers.value.find(p => p.key === adultKey);
  return adult ? `Adult ${adultNumber} (${adult.firstName} ${adult.lastName})` : `Adult ${adultNumber}`;
};

const availableAdultsForInfant = (infantIndex) => {
  const infantKey = `pax_${infantIndex}`;
  const currentAdultKey = infantAdultMapping.value[infantKey];
  const adultInfantCount = {};
  Object.values(infantAdultMapping.value).forEach(adultKey => {
    adultInfantCount[adultKey] = (adultInfantCount[adultKey] || 0) + 1;
  });
  return adultPassengers.value.map(adult => {
    const hasOtherInfant = adultInfantCount[adult.key] > 0 && adult.key !== currentAdultKey;
    return {
      ...adult,
      key: adult.key,
      number: parseInt(adult.key.replace('pax_', '')),
      name: `${adult.firstName || ''} ${adult.lastName || ''}`.trim() || `Adult ${parseInt(adult.key.replace('pax_', ''))}`,
      isCurrent: adult.key === currentAdultKey,
      isAvailable: !hasOtherInfant || adult.key === currentAdultKey,
      alreadyHasInfant: hasOtherInfant && adult.key !== currentAdultKey
    };
  });
};

const updatePassengerData = (type, index, data) => {
  const key = data.key || `pax_${index}`;
  const idx = passengers.value.findIndex(p => p.key === key);
  const passengerEntry = { ...data, key, type };

  if (!passengerEntry.dateOfBirth && (data.dobYear && data.dobMonth && data.dobDay)) {
    passengerEntry.dateOfBirth = `${data.dobYear}-${data.dobMonth.toString().padStart(2, '0')}-${data.dobDay.toString().padStart(2, '0')}`;
  }

  if (type === 'Infant' && data.associatedAdult) {
    infantAdultMapping.value[key] = `pax_${data.associatedAdult}`;
  } else if (type === 'Infant' && !data.associatedAdult && infantAdultMapping.value[key]) {
    delete infantAdultMapping.value[key];
  }

  if (idx > -1) passengers.value[idx] = passengerEntry;
  else passengers.value.push(passengerEntry);
};

const handlePassengerValidation = ({ index, isValid }) => {
  passengerValidation.value[`pax_${index}`] = isValid;
};

const calculateTotal = () => {
  return (bookingStore.grandTotalForAdults || 0) + (bookingStore.grandTotalForChildren || 0) + (bookingStore.grandTotalForInfants || 0);
};

const isPassengerComplete = (index) => {
  const key = `pax_${index}`;
  
  // Use the form validation directly if we have it
  if (passengerValidation.value[key] !== undefined) {
    return passengerValidation.value[key];
  }

  const data = passengers.value.find(p => p.key === key) || bookingStore.passengers.find(p => p.key === key);
  if (!data) return false;
  
  // If the data object itself has the isValid flag from emit
  if (data.isValid !== undefined) {
      return data.isValid;
  }
  
  const hasBasicInfo = !!(data.firstName?.trim() && data.lastName?.trim() && data.dateOfBirth);
  if (data.type === 'Infant') {
    return hasBasicInfo && !!(infantAdultMapping.value[key] || data.associatedAdult);
  }
  return hasBasicInfo;
};

const validateCurrentTab = () => {
  if (!isPassengerComplete(activeIndex.value)) {
    showValidation.value = true;
    const passengerType = getPassengerType(activeIndex.value);
    if (passengerType === 'Infant' && !infantAdultMapping.value[`pax_${activeIndex.value}`]) {
      notificationStore.warn(`Please select which adult the infant will sit with.`);
    } else {
      notificationStore.warn(`Please complete all required fields.`);
    }
    return false;
  }
  return true;
};

const handleTabChange = (n) => {
  if (n > activeIndex.value && !isPassengerComplete(activeIndex.value)) {
    showValidation.value = true;
    notificationStore.warn(`Please complete Passenger ${activeIndex.value} before moving to the next.`);
    return;
  }
  activeIndex.value = n;
};

const goToNextGuest = () => {
  if (validateCurrentTab()) activeIndex.value++;
};

const saveAllPassengersToStore = async () => {
  try {
    isSaving.value = true;
    for (let i = 1; i <= totalTravelers.value; i++) {
        if (!isPassengerComplete(i)) throw new Error(`Passenger ${i} incomplete`);
    }
    if (!contact.value.firstName?.trim() || !contact.value.lastName?.trim() || !isValidEmail(contact.value.email) || !isValidPhone(contact.value.phone)) {
        throw new Error('Contact information invalid');
    }
    
    bookingStore.setPassengers(passengers.value);
    bookingStore.infantAdultMapping = infantAdultMapping.value;
    bookingStore.setContactInfo(contact.value);
    return true;
  } catch (error) {
    notificationStore.warn(error.message);
    return false;
  } finally {
    isSaving.value = false;
  }
};

const handleContinueToAddons = async () => {
  if (await saveAllPassengersToStore()) {
    bookingStore.snapshotToServer();
    
    // REDIRECTION LOGIC: If any segment is "Premium", go directly to Seat Selection
    // This aligns with real-world premium-first booking flows.
    const hasPremium = Object.values(bookingStore.fareFamilies).some(fare => fare === 'premium');
    
    if (hasPremium) {
      console.log('💎 Premium fare detected! Redirecting directly to Seat Selection...');
      router.push({ name: 'SeatSelection' });
    } else {
      router.push({ name: 'Addons' });
    }
  }
};

watch(contact, (newContact) => bookingStore.setContactInfo(newContact), { deep: true });

onMounted(() => {
  const session = bookingStore.checkSession();
  if (session.valid && bookingStore.passengers.length > 0) {
    passengers.value = [...bookingStore.passengers];
    infantAdultMapping.value = { ...bookingStore.infantAdultMapping };
  }
  for (let i = 1; i <= totalTravelers.value; i++) {
    if (!isPassengerComplete(i)) {
      activeIndex.value = i;
      break;
    }
  }
});
</script>