<template>
  <div class="pal-card">
    <div class="pal-card-header">
      <span class="user-icon">👤</span> 
      PASSENGER {{ index }} - {{ type }}
    </div>
    <div class="pal-card-body">
      <div class="form-row">
        <div class="field col-1">
          <label>Title</label>
          <select v-model="form.title" @change="emitData">
            <option value="MR">Mr.</option>
            <option value="MS">Ms.</option>
            <option value="MRS">Mrs.</option>
          </select>
        </div>
        <div class="field col-3">
          <label>First Name</label>
          <input v-model="form.firstName" type="text" placeholder="First Name" @input="debounceEmit">
        </div>
        <div class="field col-1">
          <label>M.I.</label>
          <input v-model="form.middleInitial" type="text" maxlength="1" @input="debounceEmit">
        </div>
        <div class="field col-3">
          <label>Last Name</label>
          <input v-model="form.lastName" type="text" placeholder="Last Name" @input="debounceEmit">
        </div>
      </div>

      <label class="section-label">Date of Birth</label>
      <div class="form-row">
        <div class="field">
          <select v-model="form.dobDay" @change="emitData">
            <option value="">Day</option>
            <option v-for="d in 31" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div class="field">
          <select v-model="form.dobMonth" @change="emitData">
            <option value="">Month</option>
            <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
          </select>
        </div>
        <div class="field">
          <input v-model="form.dobYear" type="number" placeholder="Year (YYYY)" min="1900" :max="new Date().getFullYear()" @input="debounceEmit">
        </div>
      </div>

      <div class="form-row mt-3">
        <div class="field col-2">
          <label>Nationality</label>
          <select v-model="form.nationality" @change="emitData">
            <option value="Philippines">Philippines</option>
            <option value="United States">United States</option>
            <option value="Canada">Canada</option>
            <option value="Japan">Japan</option>
            <option value="South Korea">South Korea</option>
            <option value="Singapore">Singapore</option>
            <option value="Australia">Australia</option>
            <option value="United Kingdom">United Kingdom</option>
          </select>
        </div>
        <div class="field col-2">
          <label>Passport Number</label>
          <input v-model="form.passport" type="text" placeholder="Passport No." @input="debounceEmit">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, onUnmounted } from 'vue';

const props = defineProps(['type', 'index']);
const emit = defineEmits(['update']);

const months = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"];

const form = reactive({
    title: 'MR',
    firstName: '',
    middleInitial: '',
    lastName: '',
    dobDay: '',
    dobMonth: '',
    dobYear: '',
    nationality: 'Philippines',
    passport: ''
});

// Debounce timer
let debounceTimer = null;

// Debounced emit function for input fields
const debounceEmit = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
  
  debounceTimer = setTimeout(() => {
    emitData();
  }, 300); // 300ms delay
};

// In PassengerForm.vue, update emitData function:
const emitData = () => {
  console.log(`📤 PassengerForm ${props.index} emitting data...`);
  
  // Combine date parts into YYYY-MM-DD format
  let dateOfBirth = '';
  if (form.dobYear && form.dobMonth && form.dobDay) {
    const month = form.dobMonth.toString().padStart(2, '0');
    const day = form.dobDay.toString().padStart(2, '0');
    dateOfBirth = `${form.dobYear}-${month}-${day}`;
  }
  // REMOVED: Default date logic - now dateOfBirth will be empty if not filled

  const formattedData = {
    title: form.title,
    firstName: form.firstName,
    middleName: form.middleInitial,
    lastName: form.lastName,
    dateOfBirth: dateOfBirth, // Will be empty string if not filled
    nationality: form.nationality,
    passportNumber: form.passport,
    type: props.type,
    key: `pax_${props.index}`
  };
  
  console.log(`📤 Emitting passenger ${props.index}:`, formattedData);
  emit('update', formattedData);
};

// Initialize - REMOVED default date population
onMounted(() => {
  // Emit initial data after a brief delay
  setTimeout(() => {
    emitData();
  }, 100);
});

// Clean up timer on unmount
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
  border-radius: 4px; 
  margin-bottom: 25px; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
}
.pal-card-header { 
  background: #f0f3f5; 
  padding: 12px 20px; 
  font-weight: 800; 
  color: #003870; 
  font-size: 0.85rem; 
  border-bottom: 1px solid #ddd; 
}
.pal-card-body { 
  padding: 20px; 
}
.form-row { 
  display: flex; 
  gap: 15px; 
  margin-bottom: 15px; 
}
.section-label { 
  display: block; 
  font-size: 0.75rem; 
  font-weight: 700; 
  color: #555; 
  margin-bottom: 5px; 
  text-transform: uppercase; 
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
input, select { 
  border: 1px solid #ccc; 
  padding: 10px; 
  border-radius: 2px; 
  font-size: 0.9rem; 
  width: 100%;
  box-sizing: border-box;
}
.mt-3 { 
  margin-top: 15px; 
}
</style>