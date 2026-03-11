<template>
  <div class="min-h-screen bg-[#0f172a] text-white py-12 px-4 sm:px-6 lg:px-8 font-sans selection:bg-blue-500/30">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12 animate-in fade-in slide-in-from-top duration-700">
        <h1 class="text-4xl font-black tracking-tight mb-2 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
          CHECK-IN ONLINE
        </h1>
        <p class="text-slate-400 font-medium">Fast, secure, and ready for departure.</p>
      </div>

      <!-- Step Indicator -->
      <div class="flex items-center justify-between mb-12 max-w-2xl mx-auto">
        <div v-for="(step, idx) in 3" :key="idx" class="flex flex-col items-center flex-1 relative">
          <div 
            :class="[
              'w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all duration-500 z-10',
              currentStep > idx + 1 ? 'bg-blue-500 text-white' : 
              currentStep === idx + 1 ? 'bg-blue-600 ring-4 ring-blue-500/20 text-white shadow-lg shadow-blue-500/40 scale-110' : 
              'bg-slate-800 text-slate-500 border border-slate-700'
            ]"
          >
            <span v-if="currentStep > idx + 1">✓</span>
            <span v-else>{{ idx + 1 }}</span>
          </div>
          <span :class="['text-[10px] font-black uppercase tracking-widest mt-3 transition-colors duration-500', currentStep >= idx + 1 ? 'text-blue-400' : 'text-slate-600']">
            {{ ['Identify', 'Security', 'Boarding'][idx] }}
          </span>
          <!-- Connector -->
          <div v-if="idx < 2" class="absolute top-5 left-1/2 w-full h-[2px] bg-slate-800 -z-0">
            <div 
              class="h-full bg-blue-500 transition-all duration-700" 
              :style="{ width: currentStep > idx + 1 ? '100%' : '0%' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Main Card -->
      <div class="bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden relative group">
        <!-- Decoration -->
        <div class="absolute -top-24 -right-24 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl group-hover:bg-blue-600/20 transition-colors duration-700"></div>
        <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-cyan-600/10 rounded-full blur-3xl group-hover:bg-cyan-600/20 transition-colors duration-700"></div>

        <div class="p-8 md:p-12 relative">
          
          <!-- STEP 1: IDENTIFICATION -->
          <Transition name="fade-slide" mode="out-in">
            <div v-if="currentStep === 1" key="step1" class="space-y-8">
              <div class="text-left">
                <h2 class="text-2xl font-bold mb-2">Find your booking</h2>
                <p class="text-slate-400 text-sm">Enter your booking reference (PNR) and passenger last name.</p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">Booking Reference (PNR)</label>
                  <input 
                    v-model="form.pnr"
                    type="text" 
                    placeholder="e.g. ABC123" 
                    maxlength="6"
                    class="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-5 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all uppercase font-mono tracking-widest"
                  >
                </div>
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">Last Name</label>
                  <input 
                    v-model="form.lastName"
                    type="text" 
                    placeholder="Surname" 
                    class="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-5 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all font-medium"
                  >
                </div>
              </div>

              <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm flex items-center gap-3">
                <span class="text-xl">⚠️</span> {{ error }}
              </div>

              <button 
                @click="lookupBooking"
                :disabled="isLoading || !form.pnr || !form.lastName"
                class="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-black py-4 rounded-xl transition-all shadow-lg shadow-blue-500/20 active:scale-[0.98] flex items-center justify-center gap-3"
              >
                <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span v-else>SEARCH BOOKING</span>
              </button>
            </div>

            <!-- STEP 1.5: BOOKING SELECTION -->
            <div v-else-if="currentStep === 1.5" key="step15" class="space-y-8">
              <div class="text-left">
                <h2 class="text-2xl font-bold mb-2">Select Passenger</h2>
                <p class="text-slate-400 text-sm">Choose the passenger you wish to check-in.</p>
              </div>

              <div class="space-y-3">
                <div 
                  v-for="booking in foundBookings" 
                  :key="booking.id"
                  @click="selectBooking(booking)"
                  :class="[
                    'p-6 border-2 rounded-2xl cursor-pointer transition-all flex items-center justify-between group',
                    selectedBooking?.id === booking.id ? 'border-blue-500 bg-blue-500/10' : 'border-slate-800 bg-slate-800/30 hover:border-slate-700'
                  ]"
                >
                  <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center text-xl group-hover:scale-110 transition-transform">👤</div>
                    <div>
                      <div class="font-bold text-lg">{{ booking.passenger_name }}</div>
                      <div class="text-xs text-slate-500 font-mono">{{ booking.flight_number }} · {{ booking.origin }} → {{ booking.destination }}</div>
                    </div>
                  </div>
                  <div v-if="booking.is_checked_in" class="bg-green-500/10 text-green-400 text-[10px] font-black uppercase px-2 py-1 rounded-full border border-green-500/20">
                    Checked In
                  </div>
                  <div v-else-if="selectedBooking?.id === booking.id" class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs">
                    ✓
                  </div>
                </div>
              </div>

              <div class="flex gap-4">
                <button 
                  @click="currentStep = 1"
                  class="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold py-4 rounded-xl transition-all"
                >
                  BACK
                </button>
                <button 
                  @click="currentStep = 2"
                  :disabled="!selectedBooking || selectedBooking.is_checked_in"
                  class="flex-[2] bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-black py-4 rounded-xl transition-all shadow-lg shadow-blue-500/20"
                >
                  CONTINUE
                </button>
              </div>
            </div>

            <!-- STEP 2: SAFETY DECLARATION -->
            <div v-else-if="currentStep === 2" key="step2" class="space-y-8">
              <div class="text-left">
                <h2 class="text-2xl font-bold mb-2">Safety & Security</h2>
                <p class="text-slate-400 text-sm">Please confirm you are not carrying any prohibited items.</p>
              </div>

              <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 space-y-6">
                <!-- Prohibited Items Mockup -->
                <div class="grid grid-cols-4 gap-4 mb-4 text-center">
                  <div v-for="item in ['🔥', '🔋', '🧪', '🔫']" :key="item" class="bg-slate-900 aspect-square rounded-xl flex items-center justify-center text-2xl border border-white/5 grayscale opacity-50">
                    {{ item }}
                  </div>
                </div>
                <div class="text-xs text-slate-400 leading-relaxed text-left">
                  For safety reasons, dangerous goods such as compressed gases, corrosives, explosives, flammable liquids and solids, radioactive materials, oxidizing materials, poisons, infectious substances and briefcases with installed alarm devices are strictly prohibited.
                </div>

                <label class="flex items-start gap-4 p-4 rounded-xl bg-blue-600/5 border border-blue-500/20 cursor-pointer group hover:bg-blue-600/10 transition-colors text-left">
                  <input 
                    v-model="form.hasDeclaredSafety"
                    type="checkbox" 
                    class="mt-1 w-5 h-5 rounded border-slate-700 bg-slate-800 text-blue-500 focus:ring-blue-500/50"
                  >
                  <span class="text-sm font-medium text-slate-300 group-hover:text-blue-200 transition-colors">
                    I acknowledge that I have read and understood the restricted items policy and confirm that my baggage does not contain any prohibited items.
                  </span>
                </label>

                <!-- Documents Section -->
                <div class="pt-6 border-t border-slate-800 space-y-6">
                   <div class="text-left">
                      <h3 class="text-sm font-black uppercase tracking-widest text-blue-400">Travel Documents</h3>
                      <p class="text-xs text-slate-500 mt-1">Required for security and verification.</p>
                   </div>
                   
                   <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div class="space-y-2">
                         <label class="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">Passport Expiry</label>
                         <input v-model="form.passport_expiry" type="date" class="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all font-medium text-sm">
                      </div>
                      <div v-if="selectedBooking?.ph_discount_type === 'pwd'" class="space-y-2">
                         <label class="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">PWD ID Number</label>
                         <input v-model="form.pwd_id_number" type="text" placeholder="Enter ID Number" class="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all font-medium text-sm">
                      </div>
                      <div v-if="selectedBooking?.ph_discount_type === 'senior'" class="space-y-2">
                         <label class="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">Senior ID Number</label>
                         <input v-model="form.senior_id_number" type="text" placeholder="Enter ID Number" class="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all font-medium text-sm">
                      </div>
                   </div>
                </div>
              </div>

              <div class="flex gap-4">
                <button 
                  @click="currentStep = 1.5"
                  class="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold py-4 rounded-xl transition-all"
                >
                  BACK
                </button>
                <button 
                  @click="processCheckin"
                  :disabled="isLoading || !form.hasDeclaredSafety"
                  class="flex-[2] bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-black py-4 rounded-xl transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-3"
                >
                  <span v-if="isLoading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  <span v-else>COMPLETE CHECK-IN</span>
                </button>
              </div>
            </div>

            <!-- STEP 3: COMPLETION -->
            <div v-else-if="currentStep === 3" key="step3" class="space-y-8 animate-in zoom-in duration-500">
              <div class="flex flex-col items-center">
                <div class="w-24 h-24 bg-green-500/20 rounded-full flex items-center justify-center mb-6 border border-green-500/30">
                  <span class="text-4xl">🎉</span>
                </div>
                <h2 class="text-3xl font-black mb-2">You're all set!</h2>
                <p class="text-slate-400">Check-in complete. Have a pleasant flight, {{ selectedBooking?.passenger_name }}.</p>
              </div>

              <div class="bg-white text-slate-900 rounded-3xl overflow-hidden shadow-2xl relative">
                <!-- Boarding Pass Mockup -->
                <div class="bg-blue-600 p-6 text-white flex justify-between items-center">
                  <div>
                    <div class="text-[10px] font-black uppercase tracking-widest opacity-70">Flight Number</div>
                    <div class="text-2xl font-black">{{ checkinResult?.flight_number }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-[10px] font-black uppercase tracking-widest opacity-70">Gate</div>
                    <div class="text-2xl font-black">{{ checkinResult?.gate_number || 'TBA' }}</div>
                  </div>
                </div>
                <div class="p-8 space-y-6">
                  <div class="flex justify-between items-center text-left">
                    <div class="flex-1">
                      <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Origin</div>
                      <div class="text-2xl font-black">{{ checkinResult?.origin || selectedBooking?.origin }}</div>
                    </div>
                    <div class="px-4 text-2xl">✈️</div>
                    <div class="flex-1 text-right">
                      <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Destination</div>
                      <div class="text-2xl font-black">{{ checkinResult?.destination || selectedBooking?.destination }}</div>
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-3 gap-4 border-t border-slate-100 pt-6">
                    <div class="text-left">
                      <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Boarding</div>
                      <div class="text-lg font-bold">45m Prior</div>
                    </div>
                    <div class="text-center">
                      <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Seat</div>
                      <div class="text-lg font-bold text-blue-600">{{ checkinResult?.seat_number || 'TBA' }}</div>
                    </div>
                    <div class="text-right">
                      <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Zone</div>
                      <div class="text-lg font-bold">Priority</div>
                    </div>
                  </div>
                </div>
                <!-- Perforation -->
                <div class="h-px w-full border-t-2 border-dashed border-slate-200 relative">
                  <div class="absolute -left-3 -top-3 w-6 h-6 bg-slate-900 rounded-full"></div>
                  <div class="absolute -right-3 -top-3 w-6 h-6 bg-slate-900 rounded-full"></div>
                </div>
                <div class="p-6 bg-slate-50 flex flex-col items-center">
                  <div class="bg-white p-2 rounded-xl border border-slate-200 shadow-sm mb-4">
                    <img 
                      :src="`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${checkinResult?.boarding_pass}`" 
                      alt="Boarding Pass QR"
                      class="w-32 h-32"
                    >
                  </div>
                  <div class="text-[10px] font-mono text-slate-400 tracking-widest">{{ checkinResult?.boarding_pass }}</div>
                </div>
              </div>

              <div class="flex flex-col gap-3">
                <button 
                  @click="downloadBoardingPass"
                  class="w-full bg-blue-600 hover:bg-blue-500 text-white font-black py-4 rounded-xl transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-3"
                >
                  📥 DOWNLOAD PDF PASS
                </button>
                <button 
                  @click="reset"
                  class="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold py-4 rounded-xl transition-all"
                >
                  DONE
                </button>
              </div>
            </div>
          </Transition>

        </div>
      </div>
      
      <!-- Footer Info -->
      <div class="mt-8 text-slate-500 text-xs text-center max-w-lg mx-auto leading-relaxed">
        Check-in usually closes 45 minutes before domestic departures and 60 minutes for international flights. Please ensure you have sufficient time for security and boarding.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const currentStep = ref(1)
const isLoading = ref(false)
const error = ref(null)

const form = reactive({
  pnr: '',
  lastName: '',
  hasDeclaredSafety: false,
  passport_expiry: '',
  pwd_id_number: '',
  senior_id_number: ''
})

const foundBookings = ref([])
const selectedBooking = ref(null)
const checkinResult = ref(null)

const lookupBooking = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await axios.post('http://localhost:8000/api/checkin/lookup/', {
      pnr: form.pnr,
      last_name: form.lastName
    })
    foundBookings.value = response.data
    currentStep.value = 1.5
  } catch (err) {
    error.value = err.response?.data?.error || 'Could not find your booking. Please check your details.'
  } finally {
    isLoading.value = false
  }
}

const selectBooking = (booking) => {
  if (booking.is_checked_in) return
  selectedBooking.value = booking
}

const processCheckin = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await axios.post('http://localhost:8000/api/checkin/self_checkin/', {
      booking_detail_id: selectedBooking.value.id,
      has_declared_safety: form.hasDeclaredSafety,
      passport_expiry: form.passport_expiry,
      pwd_id_number: form.pwd_id_number,
      senior_id_number: form.senior_id_number
    })
    checkinResult.value = response.data
    currentStep.value = 3
  } catch (err) {
    error.value = err.response?.data?.error || 'Check-in failed. Please try again or visit the counter.'
  } finally {
    isLoading.value = false
  }
}

const downloadBoardingPass = () => {
  if (checkinResult.value?.booking_detail?.id) {
    window.open(`http://localhost:8000/api/dcs/boarding-pass/${checkinResult.value.booking_detail.id}/`, '_blank')
  } else if (selectedBooking.value?.id) {
     window.open(`http://localhost:8000/api/dcs/boarding-pass/${selectedBooking.value.id}/`, '_blank')
  }
}

const reset = () => {
  currentStep.value = 1
  form.pnr = ''
  form.lastName = ''
  form.hasDeclaredSafety = false
  foundBookings.value = []
  selectedBooking.value = null
  checkinResult.value = null
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Custom Checkbox */
input[type="checkbox"] {
  @apply appearance-none transition-all duration-200;
  background-size: 100% 100%;
  background-position: center;
  background-repeat: no-repeat;
}

input[type="checkbox"]:checked {
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
  @apply bg-blue-500 border-blue-500 shadow-lg shadow-blue-500/20;
}
</style>