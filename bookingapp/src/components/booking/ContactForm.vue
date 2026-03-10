<template>
  <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md">
    <!-- Card Header -->
    <div class="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
      <div>
        <h3 class="font-bold text-slate-800 uppercase tracking-tight text-sm">
          Contact Information
        </h3>
        <p class="text-[10px] text-slate-500 font-medium">
          Booking details and E-tickets will be sent here
        </p>
      </div>
      
      <div class="flex items-center gap-2">
      </div>
    </div>

    <div class="p-6 space-y-6">
      <!-- Copy from Passenger 1 Toggle -->
      <div v-if="hasPassenger1Data" class="flex items-center justify-end">
        <button 
          @click="copyFromPassenger1"
          type="button"
          class="text-[10px] font-bold text-rose-500 hover:text-rose-600 flex items-center gap-1 transition-colors"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h8m0 0l-4-4m4 4l-4 4m0 6H8m0 0l4 4m-4-4l4-4" />
          </svg>
          Same as Passenger 1
        </button>
      </div>

      <!-- Name Row -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-5">
        <div class="md:col-span-5">
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">
            First Name <span class="text-rose-500">*</span>
          </label>
          <input 
            :value="modelValue.firstName" 
            @input="updateField('firstName', $event.target.value)"
            type="text" 
            placeholder="First Name"
            class="w-full h-11 px-4 bg-white border rounded-lg text-sm font-medium transition-all outline-none focus:ring-2 focus:ring-rose-500/20"
            :class="[showValidation && !modelValue.firstName?.trim() ? 'border-rose-500 bg-rose-50' : 'border-slate-200 hover:border-slate-300 focus:border-rose-500']"
          >
        </div>
        
        <div class="md:col-span-2">
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">M.I.</label>
          <input 
            :value="modelValue.middleName" 
            @input="updateField('middleName', $event.target.value)"
            type="text" 
            maxlength="1"
            placeholder="A"
            class="w-full h-11 px-4 border border-slate-200 rounded-lg text-sm font-medium transition-all outline-none focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20"
          >
        </div>
        
        <div class="md:col-span-5">
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">
            Last Name <span class="text-rose-500">*</span>
          </label>
          <input 
            :value="modelValue.lastName" 
            @input="updateField('lastName', $event.target.value)"
            type="text" 
            placeholder="Last Name"
            class="w-full h-11 px-4 bg-white border rounded-lg text-sm font-medium transition-all outline-none focus:ring-2 focus:ring-rose-500/20"
            :class="[showValidation && !modelValue.lastName?.trim() ? 'border-rose-500 bg-rose-50' : 'border-slate-200 hover:border-slate-300 focus:border-rose-500']"
          >
        </div>
      </div>
      
      <!-- Email and Phone Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        <div>
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">
            Email Address <span class="text-rose-500">*</span>
          </label>
          <div class="relative">
            <input 
              :value="modelValue.email" 
              @input="updateField('email', $event.target.value)"
              type="email" 
              placeholder="email@example.com"
              class="w-full h-11 pl-10 pr-4 bg-white border rounded-lg text-sm font-medium transition-all outline-none focus:ring-2 focus:ring-rose-500/20"
              :class="[showValidation && !isValidEmail(modelValue.email) ? 'border-rose-500 bg-rose-50' : 'border-slate-200 hover:border-slate-300 focus:border-rose-500']"
            >
            <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            </div>
          </div>
        </div>
        
        <div>
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">
            Phone Number <span class="text-rose-500">*</span>
          </label>
          <div class="flex h-11 rounded-lg border overflow-hidden transition-all focus-within:ring-2 focus-within:ring-rose-500/20" 
               :class="[showValidation && !isValidPhone(modelValue.phone) ? 'border-rose-500' : 'border-slate-200 focus-within:border-rose-500']">
            <div class="px-4 bg-slate-50 border-r border-slate-200 text-xs font-bold text-slate-400 flex items-center shrink-0">
              +63
            </div>
            <input 
              :value="modelValue.phone" 
              @input="updateField('phone', $event.target.value)"
              type="tel" 
              placeholder="912 345 6789"
              class="flex-1 px-4 border-none outline-none text-sm font-medium bg-white min-w-0"
              :class="[showValidation && !isValidPhone(modelValue.phone) ? 'bg-rose-50' : '']"
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  showValidation: {
    type: Boolean,
    default: false
  },
  passenger1: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:modelValue']);

const hasPassenger1Data = computed(() => {
  return props.passenger1 && props.passenger1.firstName && props.passenger1.lastName;
});

const copyFromPassenger1 = () => {
  if (!props.passenger1) return;
  
  const updatedInfo = {
    ...props.modelValue,
    firstName: props.passenger1.firstName || '',
    lastName: props.passenger1.lastName || '',
    middleName: props.passenger1.middleInitial || '', // Note: MI vs middleName naming
  };
  
  emit('update:modelValue', updatedInfo);
};

const isValidEmail = (email) => {
  if (!email) return false;
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
};

const isValidPhone = (phone) => {
  if (!phone) return false;
  let digitsOnly = phone.replace(/\D/g, '');
  if (digitsOnly.startsWith('0')) digitsOnly = digitsOnly.substring(1);
  return digitsOnly.length === 10;
};

const updateField = (field, value) => {
  emit('update:modelValue', {
    ...props.modelValue,
    [field]: value
  });
};
</script>
