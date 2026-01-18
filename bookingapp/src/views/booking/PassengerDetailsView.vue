<template>
  <div class="pal-bg">
    <div class="container pal-layout">
      
      <main class="main-content">
        <h2 class="page-title">Passenger Details</h2>

        <div class="passenger-card">
          <aside class="passenger-nav">
            <div 
              v-for="n in totalTravelers" 
              :key="n"
              :class="['nav-item', { active: activeIndex === n }]"
              @click="handleTabChange(n)"
            >
              <div class="active-indicator"></div>
              Passenger {{ n }}
              <span v-if="isPassengerComplete(n)" class="check-mark">✓</span>
            </div>
          </aside>

          <section class="form-pane">
            <div class="pane-header">
              <h3 class="pane-title">Name</h3>
              <p class="pane-subtitle">
                Please make sure that you enter your name exactly as it is shown on your Valid ID
              </p>
            </div>

            <div class="forms-container">
              <div v-for="n in totalTravelers" :key="'form-'+n">
                <div v-show="activeIndex === n">
                  <PassengerForm 
                    :type="getPassengerType(n)" 
                    :index="n"
                    @update="(data) => updatePassengerData(getPassengerType(n), n, data)"
                  />
                </div>
              </div>
            </div>

            <div class="extra-options">
              <label class="check-container">
                <input type="checkbox"> I have a declaration / request
              </label>
              <label class="check-container">
                <input type="checkbox"> I am a Person with Disability
              </label>
            </div>

            <div class="pane-footer">
              <button 
                v-if="activeIndex < totalTravelers" 
                type="button" 
                class="next-guest"
                @click="goToNextGuest"
              >
                Next guest ❯
              </button>
            </div>
          </section>
        </div>

        <section class="contact-section mt-4">
          <h3 class="group-title">Contact Information</h3>
          <div class="pal-card contact-card">
            <div class="pal-card-body">
              <p class="contact-info-text">
                Your booking details and ticket will be sent to this email address.
              </p>
              <div class="form-grid">
                <div class="field">
                  <label>First Name*</label>
                  <input v-model="contact.firstName" type="text" placeholder="First Name" required>
                </div>
                <div class="field">
                  <label>Last Name*</label>
                  <input v-model="contact.lastName" type="text" placeholder="Last Name" required>
                </div>
                <div class="field">
                  <label>Email Address*</label>
                  <input v-model="contact.email" type="email" placeholder="email@example.com" required>
                </div>
                <div class="field phone-field">
                  <label>Phone Number*</label>
                  <div class="phone-input-group">
                    <span class="country-code">+63</span>
                    <input v-model="contact.phone" type="tel" placeholder="9XXXXXXXXX" required>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="main-footer">
          <button 
            type="button" 
            class="btn-continue-form"
            @click="handleContinueToAddons"
          >
            CONTINUE TO ADD-ONS
          </button>
        </div>
      </main>

      <aside class="sidebar">
        <div class="sticky-summary">
          <div class="summary-card">
            <div class="summary-header">Booking Summary</div>
            <div class="summary-body">
              
              <div class="flight-leg-section">
                <p class="leg-label">DEPARTURE</p>
                <div class="flight-route">
                  <strong>{{ selectedFlight?.origin }}</strong> 
                  <span class="plane-icon">✈</span> 
                  <strong>{{ selectedFlight?.destination }}</strong>
                </div>
                <div class="flight-date">{{ selectedFlight?.departure_date }}</div>
                <div class="leg-price">₱{{ Number(selectedFlight?.price || 0).toLocaleString() }} / pax</div>
              </div>

              <div v-if="isRoundTrip && selectedReturn" class="flight-leg-section mt-3">
                <p class="leg-label">RETURN</p>
                <div class="flight-route">
                  <strong>{{ selectedReturn?.origin }}</strong> 
                  <span class="plane-icon">✈</span> 
                  <strong>{{ selectedReturn?.destination }}</strong>
                </div>
                <div class="flight-date">{{ selectedReturn?.departure_date }}</div>
                <div class="leg-price">₱{{ Number(selectedReturn?.price || 0).toLocaleString() }} / pax</div>
              </div>

              <hr class="divider" />

              <div class="traveler-list">
                <p class="section-label">Travelers Price Breakdown</p>
                
                <div class="price-line">
                  <span>{{ adultCount }} Adult(s)</span>
                  <span>₱{{ (bookingStore.grandTotalForAdults).toLocaleString() }}</span>
                </div>
                
                <div v-if="childCount > 0" class="price-line">
                  <span>{{ childCount }} Child(ren)</span>
                  <span>₱{{ (bookingStore.grandTotalForChildren).toLocaleString() }}</span>
                </div>

                <div v-if="infantCount > 0" class="price-line">
                  <span>{{ infantCount }} Infant(s)</span>
                  <span>₱{{ (bookingStore.grandTotalForInfants).toLocaleString() }}</span>
                </div>
              </div>

              <div class="total-row">
                <span class="total-label">Total Amount</span>
                <span class="total-price">₱{{ calculateTotal().toLocaleString() }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import PassengerForm from '@/components/booking/PassengerForm.vue';

const bookingStore = useBookingStore();
const router = useRouter();

// --- STATE ---
const activeIndex = ref(1);
const passengers = ref([]);
const contact = reactive({ 
  title: 'MR', // Add default title
  firstName: '', 
  middleName: '',
  lastName: '', 
  email: '', 
  phone: '' 
});

// --- COMPUTED ---
const selectedFlight = computed(() => bookingStore.selectedOutbound);
const selectedReturn = computed(() => bookingStore.selectedReturn); 
const isRoundTrip = computed(() => bookingStore.tripType === 'round_trip'); 
const adultCount = computed(() => bookingStore.passengerCount.adults || 1);
const childCount = computed(() => bookingStore.passengerCount.children || 0);
const infantCount = computed(() => bookingStore.passengerCount.infants || 0);
const totalTravelers = computed(() => adultCount.value + childCount.value + infantCount.value);

// Initialize data from store if it exists (for back-navigation)
onMounted(() => {
  if (bookingStore.passengers.length > 0) {
    passengers.value = [...bookingStore.passengers];
  }
  if (bookingStore.contactInfo.email) {
    Object.assign(contact, bookingStore.contactInfo);
  }
  
  // Debug: Log what's in the store
  console.log('🔍 PassengerDetails mounted - Store data:');
  console.log('Passengers in store:', bookingStore.passengers);
  console.log('Addons in store:', bookingStore.addons);
  console.log('Passenger keys in store:', bookingStore.passengers.map(p => p.key));
});

// --- DATA METHODS ---
const getPassengerType = (n) => {
  if (n <= adultCount.value) return 'Adult';
  if (n <= adultCount.value + childCount.value) return 'Child';
  return 'Infant';
};

const updatePassengerData = (type, index, data) => {
  // Use consistent key format that will match with addons
  // Format: "pax_1", "pax_2", etc. for consistent matching
  const key = data.key || `pax_${index}`;
  
  const idx = passengers.value.findIndex(p => p.key === key);
  
  const passengerEntry = { 
    ...data, 
    key,  // Use consistent key format
    type,
    
  };

  // Ensure dateOfBirth is properly formatted
  if (!passengerEntry.dateOfBirth) {
    // Set default date of birth if not provided
    const defaultDate = new Date();
    defaultDate.setFullYear(defaultDate.getFullYear() - 20);
    passengerEntry.dateOfBirth = defaultDate.toISOString().split('T')[0];
  }

  if (idx > -1) {
    passengers.value[idx] = passengerEntry;
  } else {
    passengers.value.push(passengerEntry);
  }
  
  // Debug log
  console.log(`Updated passenger ${index}:`, passengerEntry);
  console.log('All passengers:', passengers.value);
};

const calculateTotal = () => {
  return bookingStore.grandTotal;
};

// --- VALIDATION LOGIC ---
const isPassengerComplete = (index) => {
  const key = `pax_${index}`;
  const data = passengers.value.find(p => p.key === key);
  
  // Validation criteria: checks if data exists and required fields are filled
  return !!(
    data && 
    data.firstName?.trim() && 
    data.lastName?.trim() && 
    data.title &&
    data.dateOfBirth // Add date of birth validation
  );
};

const validateCurrentTab = () => {
  if (!isPassengerComplete(activeIndex.value)) {
    alert(`Please complete details for Passenger ${activeIndex.value} first.`);
    return false;
  }
  return true;
};

const handleTabChange = (n) => {
  // Allow going back freely, but validate when trying to skip ahead
  if (n > activeIndex.value) {
    if (validateCurrentTab()) activeIndex.value = n;
  } else {
    activeIndex.value = n;
  }
};

const goToNextGuest = () => {
  if (validateCurrentTab()) {
    activeIndex.value++;
  }
};

const handleContinueToAddons = () => {
  // 1. Final Passenger Validation
  for (let i = 1; i <= totalTravelers.value; i++) {
    if (!isPassengerComplete(i)) {
      alert(`Passenger ${i} information is incomplete. Please fill all required fields.`);
      activeIndex.value = i;
      return;
    }
  }

  // 2. Contact Info Validation
  const isContactValid = 
    contact.firstName.trim() && 
    contact.lastName.trim() && 
    contact.email.includes('@') && 
    contact.phone.length >= 7;

  if (!isContactValid) {
    alert("Please provide valid contact information (Name, Email, and Phone).");
    return;
  }

  // 3. Add title to contact info if not set
  if (!contact.title) {
    contact.title = 'MR'; // Default value
  }

  // 4. Log before committing
  console.log('📝 Committing to Pinia Store:');
  console.log('Passengers to store:', passengers.value);
  console.log('Contact info to store:', contact);
  console.log('Passenger keys:', passengers.value.map(p => p.key));

    console.log('📝 BEFORE Committing to Pinia Store:');
  console.log('Local passengers array:', passengers.value);
  console.log('Local passengers count:', passengers.value.length);
  
  // Check if we actually have passenger data
  if (passengers.value.length === 0) {
    alert('No passenger data found. Please fill in passenger details.');
    return;
  }
  
  // Check each passenger has required fields
  const incompletePassengers = passengers.value.filter(p => 
    !p.firstName?.trim() || !p.lastName?.trim() || !p.dateOfBirth
  );
  
  if (incompletePassengers.length > 0) {
    alert(`Please complete all required fields for all passengers.`);
    return;
  }

  // 5. Commit to Pinia Store
  bookingStore.setPassengers(passengers.value);
  bookingStore.setContactInfo(contact);

  // 6. Verify store update
  console.log('✅ Store updated:');
  console.log('Store passengers:', bookingStore.passengers);
  console.log('Store passenger keys:', bookingStore.passengers.map(p => p.key));

  // 7. Navigate
  router.push({ name: 'Addons' });
};
</script>

<style scoped>
/* Previous styles remain the same */
.pal-bg { background-color: #f4f7f9; min-height: 100vh; padding: 40px 0; font-family: 'Inter', sans-serif; }
.pal-layout { display: grid; grid-template-columns: 1fr 350px; gap: 30px; align-items: start; }

/* PASSENGER CARD NAV */
.check-mark { color: #28a745; margin-left: 8px; font-weight: bold; }

/* CONTACT INFORMATION DESIGN */
.contact-card { border-top: 4px solid #003870; }
.contact-info-text { font-size: 0.9rem; color: #666; margin-bottom: 20px; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.field { display: flex; flex-direction: column; }
.field label { font-size: 0.8rem; font-weight: 700; color: #444; margin-bottom: 6px; }
.field input { padding: 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 0.95rem; transition: border 0.3s; }
.field input:focus { border-color: #003870; outline: none; }

.phone-input-group { display: flex; border: 1px solid #ccc; border-radius: 4px; overflow: hidden; }
.country-code { background: #eee; padding: 12px; font-size: 0.95rem; color: #555; border-right: 1px solid #ccc; }
.phone-input-group input { border: none; flex: 1; }

/* FOOTER BUTTON */
.main-footer { margin-top: 40px; text-align: right; }
.btn-continue-form { 
  background: #d11241; 
  color: white; 
  border: none; 
  padding: 18px 40px; 
  font-weight: 800; 
  border-radius: 4px; 
  cursor: pointer; 
  font-size: 1rem;
  letter-spacing: 0.5px;
  transition: background 0.3s;
}
.btn-continue-form:hover { background: #b00f37; }

/* STYLES FROM PREVIOUS CODE (Preserved) */
.passenger-card { display: flex; background: white; border-radius: 4px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; min-height: 550px; }
.passenger-nav { width: 160px; background: #f0f0f0; border-right: 1px solid #e0e0e0; }
.nav-item { padding: 22px 20px; font-size: 0.9rem; font-weight: 700; color: #999; cursor: pointer; position: relative; border-bottom: 1px solid #e5e5e5; }
.nav-item.active { background: white; color: #003870; }
.nav-item.active .active-indicator { position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background: linear-gradient(to bottom, #d11241 50%, #003870 50%); }
.form-pane { flex: 1; padding: 40px; }
.next-guest { float: right; background: none; border: none; color: #d11241; font-weight: 800; cursor: pointer; font-size: 1rem; }

.leg-label {
  font-size: 0.7rem;
  font-weight: 800;
  color: #003870;
  margin-bottom: 4px;
}
.flight-leg-section {
  padding-bottom: 10px;
}
.leg-price {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}
.mt-3 { margin-top: 15px; }
.divider { margin: 15px 0; border: 0; border-top: 1px solid #eee; }
.section-label { font-size: 0.75rem; font-weight: 700; color: #888; text-transform: uppercase; margin-bottom: 10px; }
</style>