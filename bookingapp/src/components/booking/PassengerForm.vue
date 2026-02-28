<template>
  <div class="pal-card">
    <div class="pal-card-header">
      PASSENGER {{ index }} - {{ type }}
      <span v-if="type === 'Infant'" class="infant-tag">(Sits on adult's lap)</span>
    </div>
    <div class="pal-card-body">
      <div class="form-row">
        <div class="field col-1">
          <label>Title</label>
          <select v-model="form.title" @change="emitData" required :class="{ 'error-border': showErrors && !form.title }">
            <option value="">Title</option>
            <option value="MR">Mr.</option>
            <option value="MRS">Mrs.</option>
          </select>
          <span v-if="showErrors && !form.title" class="small-error">Title is required</span>
        </div>
        <div class="field col-3">
          <label>First Name <span class="required">*</span></label>
          <input v-model="form.firstName" type="text" placeholder="First Name" 
                 @input="handleNameInput('firstName')" 
                 :class="{ 'error-border': showErrors && !isNameValid(form.firstName) }"
                 required>
          <span v-if="showErrors && !form.firstName.trim()" class="small-error">First name is required</span>
          <span v-else-if="showErrors && !isNameValid(form.firstName)" class="small-error">Letters, spaces, and hyphens only</span>
        </div>
        <div class="field col-1">
          <label>M.I.</label>
          <input v-model="form.middleInitial" type="text" maxlength="1" @input="debounceEmit">
        </div>
        <div class="field col-3">
          <label>Last Name <span class="required">*</span></label>
          <input v-model="form.lastName" type="text" placeholder="Last Name" 
                 @input="handleNameInput('lastName')" 
                 :class="{ 'error-border': showErrors && !isNameValid(form.lastName) }"
                 required>
          <span v-if="showErrors && !form.lastName.trim()" class="small-error">Last name is required</span>
          <span v-else-if="showErrors && !isNameValid(form.lastName)" class="small-error">Letters, spaces, and hyphens only</span>
        </div>
      </div>

      <label class="section-label">Date of Birth <span class="required">*</span></label>
      <div class="form-row">
        <div class="field">
          <select v-model="form.dobDay" @change="emitData" required>
            <option value="">Day</option>
            <option v-for="d in 31" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div class="field">
          <select v-model="form.dobMonth" @change="emitData" required>
            <option value="">Month</option>
            <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
          </select>
        </div>
        <div class="field">
          <input v-model="form.dobYear" type="number" placeholder="Year (YYYY)" min="1900" 
                :max="new Date().getFullYear()" @input="debounceEmit" 
                :class="{ 'error-border': showErrors && !isDOBValid }"
                required>
        </div>
      </div>
      <span v-if="showErrors && !isDOBValid" class="small-error">Date of birth is required</span>

      <!-- Age Display -->
      <div v-if="form.dobDay && form.dobMonth && form.dobYear" class="age-display">
        Age: {{ calculatedAge }} years old
        <span v-if="showAgeWarning" class="age-warning">
          Age indicates this should be a {{ correctPassengerType }}
        </span>
      </div>

      <div class="form-row mt-3">
        <div class="field col-2">
          <label>Nationality</label>
          <select v-model="form.nationality" @change="emitData" :class="{ 'error-border': showErrors && !form.nationality }">
            <option value="">Select Nationality</option>
            <option value="Philippines">Philippines</option>
            <option value="United States">United States</option>
            <option value="Canada">Canada</option>
            <option value="Japan">Japan</option>
            <option value="South Korea">South Korea</option>
            <option value="Singapore">Singapore</option>
            <option value="Australia">Australia</option>
            <option value="United Kingdom">United Kingdom</option>
          </select>
          <span v-if="showErrors && !form.nationality" class="small-error">Nationality is required</span>
          <p v-if="requiresPassport" class="text-[9px] text-pink-500/80 font-bold mt-1 flex items-center gap-1">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            Passport Identification Required
          </p>
          <p v-else-if="form.nationality === 'Philippines'" class="text-[9px] text-emerald-500 font-bold mt-1 uppercase tracking-tighter">
            Local ID Accepted (Domestic Flights)
          </p>
        </div>
        <div class="field col-2">
          <label>Passport Number <span class="required" v-if="requiresPassport">*</span></label>
          <input v-model="form.passport" type="text" placeholder="Passport No." @input="debounceEmit" :class="{ 'error-border': showErrors && requiresPassport && !form.passport }">
          <span v-if="showErrors && requiresPassport && !form.passport" class="small-error">Passport is required for international travel</span>
        </div>
      </div>

      <div class="form-row mt-3">
        <div class="field col-2">
          <label>Passport Expiry <span class="required" v-if="requiresPassport">*</span></label>
          <div class="expiry-grid flex gap-2">
            <select v-model="form.expiryDay" @change="emitData" :class="{ 'error-border': showErrors && requiresPassport && !form.expiryDay }" class="w-1/3">
              <option value="">Day</option>
              <option v-for="d in 31" :key="d" :value="d">{{ d }}</option>
            </select>
            <select v-model="form.expiryMonth" @change="emitData" :class="{ 'error-border': showErrors && requiresPassport && !form.expiryMonth }" class="w-1/3">
              <option value="">Month</option>
              <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
            </select>
            <input v-model="form.expiryYear" type="number" placeholder="Year" :min="new Date().getFullYear()" @input="debounceEmit" :class="{ 'error-border': showErrors && requiresPassport && !form.expiryYear }" class="w-1/3">
          </div>
          <span v-if="showErrors && requiresPassport && !passportStatus.isValid" class="small-error">
            {{ passportStatus.message }}
          </span>
        </div>
      </div>

      <!-- PH SPECIFIC: Senior / PWD -->
      <div v-if="type === 'Adult'" class="ph-discount-section">
        <label class="section-label mt-3">Special Passenger Discounts (Philippines Only)</label>
        <div class="form-row">
          <label class="discount-radio">
            <input type="radio" v-model="form.phDiscountType" value="none" @change="emitData">
            Regular Passenger (No Discount)
          </label>
          <label class="discount-radio" :class="{ 'disabled-radio': isSeniorDisabled }">
            <input type="radio" v-model="form.phDiscountType" value="senior" :disabled="isSeniorDisabled" @change="emitData">
            Senior Citizen 
            <span v-if="isSeniorDisabled" class="small-warning text-xs ml-1">(Must be 60+ years old)</span>
          </label>
          <label class="discount-radio">
            <input type="radio" v-model="form.phDiscountType" value="pwd" @change="emitData">
            Person with Disability (PWD)
          </label>
        </div>
        
        <div v-if="form.phDiscountType !== 'none'" class="form-row mt-2">
          <div class="field col-2">
            <label>{{ form.phDiscountType === 'senior' ? 'Senior Citizen ID Number' : 'PWD ID Number' }} <span class="required">*</span></label>
            <input v-model="form.phDiscountId" type="text" placeholder="ID Number" @input="debounceEmit" :class="{ 'error-border': showErrors && !form.phDiscountId }" required>
            <span v-if="showErrors && !form.phDiscountId" class="small-error">ID Number is required to claim discount</span>
          </div>
        </div>
      </div>

      <!-- INFANT ONLY: Adult Seat Assignment -->
      <div v-if="type === 'Infant'" class="infant-section">
        <label class="section-label">Select Adult to sit with <span class="required">*</span></label>
        <p class="section-note">This infant will sit on the selected adult's lap during the flight.</p>
        
        <div v-if="adultOptions && adultOptions.length > 0" class="adult-options">
          <div 
            v-for="adult in adultOptions" 
            :key="adult.key"
            :class="['adult-option', { 
              selected: form.associatedAdult === adult.number,
              unavailable: adult.alreadyHasInfant && adult.number !== form.associatedAdult
            }]"
            @click="selectAdult(adult)"
          >
            <div class="adult-info">
              <div class="adult-details">
                <div class="adult-name">{{ adult.name }}</div>
                <div class="adult-number">Adult {{ adult.number }}</div>
              </div>
              <div class="adult-status">
                <span v-if="adult.isCurrent" class="status-selected">Selected</span>
                <span v-else-if="adult.alreadyHasInfant" class="status-unavailable">
                  Already has infant
                </span>
                <span v-else class="status-available">Available</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-adults-message">
          <span>No adult passengers found. Please complete adult information first.</span>
        </div>
        <span v-if="showErrors && type === 'Infant' && !form.associatedAdult" class="small-error">Please select which adult this infant will sit with</span>
      </div>

      <!-- Validation error messages removed to be placed below inputs -->
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, onUnmounted, watch, computed, nextTick } from 'vue';
import { useBookingStore } from '@/stores/booking';

const props = defineProps({
  type: String,
  index: Number,
  showValidation: { type: Boolean, default: false },
  adultPassengers: { type: Array, default: () => [] }
});
const emit = defineEmits(['update', 'validation']);

const bookingStore = useBookingStore();

const months = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"];

const form = reactive({
    title: '',
    firstName: '',
    middleInitial: '',
    lastName: '',
    dobDay: '',
    dobMonth: '',
    dobYear: '',
    nationality: 'Philippines',
    passport: '',
    expiryDay: '',
    expiryMonth: '',
    expiryYear: '',
    phDiscountType: 'none',
    phDiscountId: '',
    associatedAdult: null
});

const requiresPassport = computed(() => {
  // 1. Mandatory for ANY international flight segment
  if (bookingStore.isInternational) return true;
  
  // 2. Mandatory for non-Philippine nationals even on domestic flights (simulation standard)
  return form.nationality && form.nationality !== 'Philippines';
});

const passportStatus = computed(() => {
  if (!form.expiryDay || !form.expiryMonth || !form.expiryYear) return { isValid: false, message: 'Complete date required', type: 'error' };
  
  const expDate = new Date(form.expiryYear, form.expiryMonth - 1, form.expiryDay);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // 1. Check if actually expired
  if (expDate <= today) {
    return { isValid: false, message: 'Passport has expired', type: 'error' };
  }

  // 2. Check 6-month rule for international travel
  if (bookingStore.isInternational) {
    const sixMonthsFromNow = new Date();
    sixMonthsFromNow.setMonth(sixMonthsFromNow.getMonth() + 6);
    
    if (expDate < sixMonthsFromNow) {
      return { 
        isValid: false, 
        message: 'Must be valid for 6 months (Int\'l Law)', 
        type: 'warning' 
      };
    }
  }

  return { isValid: true, message: '', type: 'success' };
});

// Validation Regex
const nameRegex = /^[a-zA-Z\s-]+$/;

const isNameValid = (name) => {
  if (!name || !name.trim()) return false;
  return nameRegex.test(name.trim());
};

const handleNameInput = (field) => {
  // Allow typing but flag for validation
  debounceEmit();
};

// Computed properties
const showErrors = computed(() => props.showValidation);
const isDOBValid = computed(() => form.dobDay && form.dobMonth && form.dobYear);

// Age calculation
const calculatedAge = computed(() => {
  if (!form.dobYear || !form.dobMonth || !form.dobDay) return null;
  
  try {
    const birthDate = new Date(form.dobYear, form.dobMonth - 1, form.dobDay);
    const today = new Date();
    
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    const dayDiff = today.getDate() - birthDate.getDate();
    
    if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
      age--;
    }
    
    return age;
  } catch (error) {
    console.error('Error calculating age:', error);
    return null;
  }
});

// Age validation warnings
const showAgeWarning = computed(() => {
  if (!calculatedAge.value) return false;
  
  if (props.type === 'Adult' && calculatedAge.value < 12) return true;
  if (props.type === 'Child' && (calculatedAge.value < 2 || calculatedAge.value >= 12)) return true;
  if (props.type === 'Infant' && calculatedAge.value >= 2) return true;
  
  return false;
});

const correctPassengerType = computed(() => {
  if (!calculatedAge.value) return '';
  
  if (calculatedAge.value >= 12) return 'Adult';
  if (calculatedAge.value >= 2) return 'Child';
  return 'Infant';
});

// Adult options for infant assignment
const adultOptions = computed(() => {
  if (!props.adultPassengers || props.adultPassengers.length === 0) return [];
  
  return props.adultPassengers.map(adult => {
    const hasOtherInfant = adult.alreadyHasInfant && adult.number !== form.associatedAdult;
    
    return {
      ...adult,
      isCurrent: adult.number === form.associatedAdult,
      isAvailable: !hasOtherInfant || adult.number === form.associatedAdult
    };
  });
});

const isFormValid = computed(() => {
  const basicValid = form.title && 
                     isNameValid(form.firstName) && 
                     isNameValid(form.lastName) && 
                     form.dobDay && 
                     form.dobMonth && 
                     form.dobYear &&
                     form.nationality &&
                     !showAgeWarning.value; // Important: Age must match type
  
  if (props.type === 'Infant' && !form.associatedAdult) return false;
  
  // 1. Validate Passport if required (International flight or Foreign National)
  if (requiresPassport.value) {
    if (!form.passport || !form.passport.trim()) return false;
    if (!passportStatus.value.isValid) return false;
  }

  // 2. Validate PH Discount ID if claimed
  if (props.type === 'Adult' && form.phDiscountType !== 'none' && !form.phDiscountId.trim()) return false;
  
  return basicValid;
});

// Computed properties for discounts
const isSeniorDisabled = computed(() => {
  return !calculatedAge.value || calculatedAge.value < 60;
});

// Watch age changes to reset senior choice if they drop below 60
watch(calculatedAge, (newAge) => {
  if (form.phDiscountType === 'senior' && (!newAge || newAge < 60)) {
    form.phDiscountType = 'none';
    form.phDiscountId = '';
    emitData();
  }
});

// Get saved passenger data for this index
const savedPassenger = computed(() => {
  const key = `pax_${props.index}`;
  return bookingStore.passengers.find(p => p.key === key);
});

const shouldLoadSavedData = computed(() => {
  if (!bookingStore.isSessionValid) return false;
  return !!savedPassenger.value;
});

// Methods
const selectAdult = (adult) => {
  if (adult.alreadyHasInfant && adult.number !== form.associatedAdult) {
    return;
  }
  
  if (form.associatedAdult === adult.number) {
    form.associatedAdult = null;
  } else {
    form.associatedAdult = adult.number;
  }
  
  emitData();
};

// Load saved data from store
const loadSavedData = () => {
  if (shouldLoadSavedData.value) {
    console.log(`📥 Loading saved data for passenger ${props.index}:`, savedPassenger.value);
    
    form.title = savedPassenger.value.title || '';
    form.firstName = savedPassenger.value.firstName || '';
    form.middleInitial = savedPassenger.value.middleName || '';
    form.lastName = savedPassenger.value.lastName || '';
    form.nationality = savedPassenger.value.nationality || 'Philippines';
    form.passport = savedPassenger.value.passportNumber || '';
    form.phDiscountType = savedPassenger.value.phDiscountType || 'none';
    form.phDiscountId = savedPassenger.value.phDiscountId || '';

    // Parse passport expiry
    if (savedPassenger.value.passportExpiry) {
      try {
        const expiry = new Date(savedPassenger.value.passportExpiry);
        if (!isNaN(expiry.getTime())) {
          form.expiryDay = expiry.getDate();
          form.expiryMonth = expiry.getMonth() + 1;
          form.expiryYear = expiry.getFullYear();
        }
      } catch (error) {
        console.error('Error parsing passport expiry:', error);
      }
    }
    
    // Parse date of birth - FIXED: Check for dateOfBirth field
    if (savedPassenger.value.dateOfBirth) {
      console.log(`📅 Found dateOfBirth in saved data: ${savedPassenger.value.dateOfBirth}`);
      try {
        const dob = new Date(savedPassenger.value.dateOfBirth);
        if (!isNaN(dob.getTime())) {
          form.dobDay = dob.getDate();
          form.dobMonth = dob.getMonth() + 1;
          form.dobYear = dob.getFullYear();
          console.log(`📅 Parsed DOB: Day=${form.dobDay}, Month=${form.dobMonth}, Year=${form.dobYear}`);
        } else {
          console.log('❌ Invalid date format in saved data');
        }
      } catch (error) {
        console.error('Error parsing date of birth:', error);
      }
    } else {
      console.log('📝 No dateOfBirth found in saved data');
    }
    
    // Load infant association
    if (props.type === 'Infant' && bookingStore.infantAdultMapping) {
      const infantKey = `pax_${props.index}`;
      const adultKey = bookingStore.infantAdultMapping[infantKey];
      if (adultKey) {
        form.associatedAdult = parseInt(adultKey.replace('pax_', ''));
        console.log(`👶 Loaded infant association: ${infantKey} -> ${adultKey}`);
      }
    }
    
    nextTick(() => {
      emitData();
    });
  } else {
    console.log(`🆕 No saved data for passenger ${props.index}, starting fresh`);
    resetForm();
  }
};

// Reset form to initial state
const resetForm = () => {
  form.title = '';
  form.firstName = '';
  form.middleInitial = '';
  form.lastName = '';
  form.dobDay = '';
  form.dobMonth = '';
  form.dobYear = '';
  form.nationality = 'Philippines';
  form.passport = '';
  form.expiryDay = '';
  form.expiryMonth = '';
  form.expiryYear = '';
  form.phDiscountType = 'none';
  form.phDiscountId = '';
  form.associatedAdult = null;
  
  emitData();
};

// Watch for changes
watch(savedPassenger, () => {
  loadSavedData();
});

watch(() => props.index, () => {
  loadSavedData();
});

watch(() => props.adultPassengers, (newAdults) => {
  if (props.type === 'Infant') {
    // If we have an associated adult, check if they are still valid
    if (form.associatedAdult) {
      const currentAdult = newAdults.find(a => a.number === form.associatedAdult);
      if (!currentAdult || currentAdult.alreadyHasInfant) {
        form.associatedAdult = null;
        emitData();
      }
    } 
    // Auto-assign if there's exactly 1 available adult and we have none assigned
    else if (!form.associatedAdult && newAdults.length === 1 && !newAdults[0].alreadyHasInfant) {
      form.associatedAdult = newAdults[0].number;
      emitData();
    }
  }
}, { deep: true, immediate: true });

watch(() => bookingStore.isSessionValid, (isValid) => {
  if (!isValid) {
    console.log(`Session invalid, resetting form for passenger ${props.index}`);
    resetForm();
  }
});

// FIXED: Always emit validation when isFormValid changes
watch(isFormValid, (newValid) => {
  emit('validation', { index: props.index, isValid: newValid });
}, { immediate: true });

// Debounce timer
let debounceTimer = null;

// Debounced emit function
const debounceEmit = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
  
  debounceTimer = setTimeout(() => {
    emitData();
  }, 300);
};

// FIXED: Properly construct dateOfBirth string
const emitData = () => {
  console.log(`🔄 Emitting data for passenger ${props.index}`);
  console.log(`📅 DOB Fields: Day=${form.dobDay}, Month=${form.dobMonth}, Year=${form.dobYear}`);
  
  // Validate DOB - FIXED: Proper construction
  let dateOfBirth = '';
  if (form.dobYear && form.dobMonth && form.dobDay) {
    try {
      const month = form.dobMonth.toString().padStart(2, '0');
      const day = form.dobDay.toString().padStart(2, '0');
      const year = form.dobYear.toString();
      
      // Create the date string
      dateOfBirth = `${year}-${month}-${day}`;
      
      // Validate date
      const dobDate = new Date(dateOfBirth);
      if (isNaN(dobDate.getTime())) {
        console.log(`❌ Invalid date constructed: ${dateOfBirth}`);
        dateOfBirth = '';
      } else {
        console.log(`✅ Valid date constructed: ${dateOfBirth}`);
      }
    } catch (error) {
      console.error('Error formatting date of birth:', error);
      dateOfBirth = '';
    }
  } else {
    console.log('❌ Missing DOB fields');
  }

  const formattedData = {
    title: form.title,
    firstName: form.firstName.trim(),
    middleName: form.middleInitial.trim(),
    lastName: form.lastName.trim(),
    dateOfBirth: dateOfBirth,
    nationality: form.nationality,
    passportNumber: form.passport.trim(),
    passportExpiry: form.expiryYear && form.expiryMonth && form.expiryDay 
                   ? `${form.expiryYear}-${form.expiryMonth.toString().padStart(2, '0')}-${form.expiryDay.toString().padStart(2, '0')}` 
                   : '',
    phDiscountType: form.phDiscountType,
    phDiscountId: form.phDiscountId.trim(),
    type: props.type,
    key: `pax_${props.index}`,
    isValid: isFormValid.value,
    // Also include individual DOB fields for debugging
    dobDay: form.dobDay,
    dobMonth: form.dobMonth,
    dobYear: form.dobYear
  };
  
  // Add infant-specific data
  if (props.type === 'Infant') {
    formattedData.associatedAdult = form.associatedAdult;
  }
  
  console.log(`📤 Emitting passenger ${props.index}:`, formattedData);
  emit('update', formattedData);
  emit('validation', { index: props.index, isValid: isFormValid.value });
};

// Lifecycle hooks
onMounted(() => {
  console.log(`🚀 PassengerForm ${props.index} mounted`);
  
  const session = bookingStore.checkSession();
  if (!session.valid) {
    console.log('Session invalid, starting fresh');
    resetForm();
  } else {
    loadSavedData();
  }
});

onUnmounted(() => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
});
</script>

<style scoped>
.pal-card { 
  background: white; 
  border: 1px solid #ddd; 
  border-radius: 2px; 
  margin-bottom: 15px; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
  position: relative;
}
.pal-card-header { 
  background: #f0f3f5; 
  padding: 12px 20px; 
  font-weight: 800; 
  color: #FF579A; 
  font-size: 0.85rem; 
  border-bottom: 1px solid #ddd; 
  display: flex;
  align-items: center;
  gap: 8px;
}
.infant-tag {
  font-size: 0.7rem;
  font-weight: normal;
  color: #666;
  background: #FFF3CD;
  padding: 2px 6px;
  border-radius: 2px;
}
.pal-card-body { 
  padding: 20px; 
}
.form-row { 
  display: flex; 
  gap: 7px; 
  margin-bottom: 7px; 
}
.section-label { 
  display: block; 
  font-size: 0.75rem; 
  font-weight: 700; 
  color: #555; 
  margin-bottom: 2px; 
  text-transform: uppercase; 
}
.section-note {
  font-size: 0.75rem;
  color: #666;
  margin: 4px 0 12px 0;
  font-style: italic;
}
.field { 
  display: flex; 
  flex-direction: column; 
  flex: 1; 
}
.col-1 { flex: 1; } 
.col-2 { flex: 2; } 
.col-3 { flex: 3; }
label { 
  font-size: 0.75rem; 
  font-weight: 700; 
  color: #555; 
  margin-bottom: 4px; 
  text-transform: uppercase; 
}
.required {
  color: #FF579A;
}
input, select { 
  border: 1px solid #ccc; 
  padding: 10px; 
  border-radius: 2px; 
  font-size: 0.9rem; 
  width: 100%;
  box-sizing: border-box;
}
input:focus, select:focus {
  border-color: #FF579A;
  outline: none;
}
.expiry-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 5px;
}
.mt-3 { 
  margin-top: 10px; 
}

/* Age Display */
.age-display {
  margin: 8px 0;
  font-size: 0.8rem;
  color: #666;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.age-warning {
  color: #ef4444;
  font-weight: 500;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Infant section */
.infant-section {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
  border: 1px solid #e9ecef;
}

.adult-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.adult-option {
  padding: 12px 15px;
  border: 2px solid #e9ecef;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.adult-option:hover:not(.unavailable) {
  border-color: #FF579A;
  background: #fff5f7;
}

.adult-option.selected {
  border-color: #FF579A;
  background: #fff5f7;
}

.adult-option.unavailable {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f8f9fa;
}

.adult-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.adult-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.adult-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.adult-number {
  font-size: 0.75rem;
  color: #666;
}

.adult-status {
  font-size: 0.75rem;
  font-weight: 500;
}

.status-selected {
  color: #10B981;
}

.status-available {
  color: #666;
}

.status-unavailable {
  color: #ef4444;
}

.error-border {
  border-color: #ef4444 !important;
  background-color: #fef2f2;
}

.small-error {
  color: #ef4444;
  font-size: 0.7rem;
  margin-top: 4px;
  font-weight: 500;
  display: block;
}

.no-adults-message {
  padding: 12px;
  background: #fff3cd;
  border-radius: 2px;
  text-align: center;
  color: #856404;
  font-size: 0.8rem;
}

/* Validation styles */
.validation-errors {
  margin-top: 15px;
  padding: 12px;
  background-color: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 5px;
}

.error-message {
  color: #ef4444;
  font-size: 0.8rem;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
}

.error-message:before {
  margin-right: 6px;
  font-size: 0.7rem;
}

.error-message:last-child {
  margin-bottom: 0;
}

/* PH Specific Styling */
.ph-discount-section {
  padding: 15px;
  background: #fdfaf6;
  border-radius: 5px;
  border: 1px solid #f2e2ce;
  margin-top: 10px;
}

.discount-radio {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: normal;
  color: #333;
  margin-right: 15px;
  cursor: pointer;
  text-transform: none;
}

.disabled-radio {
  opacity: 0.5;
  cursor: not-allowed;
}

.small-warning {
  color: #ef4444;
}

.text-xs {
  font-size: 0.75rem;
}

.ml-1 {
  margin-left: 0.25rem;
}

</style>