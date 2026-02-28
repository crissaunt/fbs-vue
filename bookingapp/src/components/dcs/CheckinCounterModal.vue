<template>
  <div class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[94vh]">

      <!-- Modal Header -->
      <div class="bg-pink-500 px-6 py-4 flex justify-between items-center shrink-0">
        <div>
          <h3 class="text-white font-bold text-base">👩‍💼 Check-in Counter — Agent Simulation</h3>
          <p class="text-pink-100 text-xs mt-0.5">
            PNR: <span class="font-mono font-bold">{{ passenger?.pnr }}</span>
            &nbsp;·&nbsp;
            {{ passenger?.passenger_name }}
          </p>
        </div>
        <button @click="$emit('close')" class="text-white/80 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-pink-600/50">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Step Progress Bar -->
      <div class="bg-gray-50 border-b border-gray-200 px-6 py-3 shrink-0">
        <div class="flex items-center gap-0">
          <div
            v-for="(step, idx) in steps"
            :key="idx"
            class="flex items-center"
            :class="idx < steps.length - 1 ? 'flex-1' : ''"
          >
            <!-- Circle -->
            <div class="flex flex-col items-center">
              <div :class="[
                'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all',
                currentStep > idx
                  ? 'bg-pink-500 text-white'
                  : currentStep === idx
                    ? 'bg-pink-500 text-white ring-4 ring-pink-100'
                    : 'bg-gray-200 text-gray-500'
              ]">
                <svg v-if="currentStep > idx" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                </svg>
                <span v-else>{{ idx + 1 }}</span>
              </div>
              <div class="text-[9px] mt-1 font-semibold text-center max-w-[56px] leading-tight" :class="currentStep >= idx ? 'text-pink-600' : 'text-gray-400'">
                {{ step.shortLabel }}
              </div>
            </div>
            <!-- Connector Line -->
            <div v-if="idx < steps.length - 1" class="flex-1 h-0.5 mb-4 mx-1" :class="currentStep > idx ? 'bg-pink-400' : 'bg-gray-200'"></div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="p-6 overflow-y-auto flex-1">

        <!-- STEP 0: Identification -->
        <div v-if="currentStep === 0" class="space-y-5">
          <div>
            <h4 class="text-gray-900 font-bold text-base mb-0.5">Step 1 — Identification</h4>
            <p class="text-gray-400 text-sm">Ask the passenger for their Booking Reference (PNR) and a valid government-issued ID or passport.</p>
          </div>

          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-400 font-medium">Booking Reference (PNR)</span>
              <span class="font-mono font-bold text-gray-900 tracking-widest text-pink-600 bg-pink-50 px-2 py-0.5 rounded">{{ passenger?.pnr }}</span>
            </div>
            <div class="border-t border-gray-200 pt-1 mt-1 flex justify-between">
              <span class="text-gray-400 font-medium">Passenger Name</span>
              <span class="font-bold text-gray-900">{{ passenger?.passenger_name }}</span>
            </div>
            <div class="border-t border-gray-200 pt-1 mt-1 flex justify-between">
              <span class="text-gray-400 font-medium">Passenger Type</span>
              <span class="text-gray-700">{{ passenger?.passenger_type }}</span>
            </div>
          </div>

          <div class="space-y-3">
            <label class="flex items-start gap-3 cursor-pointer group p-3 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50/30 transition-all">
              <input type="checkbox" v-model="checks.pnrConfirmed" class="mt-0.5 w-4 h-4 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
              <div>
                <div class="text-sm font-semibold text-gray-800 group-hover:text-pink-600 transition-colors">PNR verified against the system</div>
                <div class="text-xs text-gray-400 mt-0.5">Confirm the booking reference matches an active confirmed booking.</div>
              </div>
            </label>
            <label class="flex items-start gap-3 cursor-pointer group p-3 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50/30 transition-all">
              <input type="checkbox" v-model="checks.idVerified" class="mt-0.5 w-4 h-4 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
              <div>
                <div class="text-sm font-semibold text-gray-800 group-hover:text-pink-600 transition-colors">Passport / Government ID presented and verified</div>
                <div class="text-xs text-gray-400 mt-0.5">Name on ID must exactly match the manifest. Check expiry date.</div>
              </div>
            </label>
            <label class="flex items-start gap-3 cursor-pointer group p-3 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50/30 transition-all">
              <input type="checkbox" v-model="checks.checkinDeadlineMet" class="mt-0.5 w-4 h-4 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
              <div>
                <div class="text-sm font-semibold text-gray-800 group-hover:text-pink-600 transition-colors">Check-in deadline verified (within 45-min cutoff)</div>
                <div class="text-xs text-gray-400 mt-0.5">Airlines enforce a strict 45–60 minute hard cutoff before departure.</div>
              </div>
            </label>
          </div>
        </div>

        <!-- STEP 1: Document Verification -->
        <div v-if="currentStep === 1" class="space-y-5">
          <div>
            <h4 class="text-gray-900 font-bold text-base mb-0.5">Step 2 — Document Verification</h4>
            <p class="text-gray-400 text-sm">Review travel documents for compliance. Flag any issues before issuing a seat.</p>
          </div>

          <div class="space-y-3">
            <label class="flex items-start gap-3 cursor-pointer group p-3 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50/30 transition-all">
              <input type="checkbox" v-model="checks.travelDocsValid" class="mt-0.5 w-4 h-4 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
              <div>
                <div class="text-sm font-semibold text-gray-800 group-hover:text-pink-600 transition-colors">Travel documents are valid and not expired</div>
                <div class="text-xs text-gray-400 mt-0.5">Passports must be valid for at least 6 months beyond the travel date for most international routes.</div>
              </div>
            </label>
            <label class="flex items-start gap-3 cursor-pointer group p-3 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50/30 transition-all">
              <input type="checkbox" v-model="checks.visaChecked" class="mt-0.5 w-4 h-4 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
              <div>
                <div class="text-sm font-semibold text-gray-800 group-hover:text-pink-600 transition-colors">Visa / entry requirements confirmed (if applicable)</div>
                <div class="text-xs text-gray-400 mt-0.5">For international routes, verify visa. Recommend passenger carry physical printouts as backup.</div>
              </div>
            </label>
            <label class="flex items-start gap-3 cursor-pointer group p-3 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50/30 transition-all">
              <input type="checkbox" v-model="checks.specialNeedsReviewed" class="mt-0.5 w-4 h-4 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
              <div>
                <div class="text-sm font-semibold text-gray-800 group-hover:text-pink-600 transition-colors">Special requirements reviewed (if any)</div>
                <div class="text-xs text-gray-400 mt-0.5">Unaccompanied minors, pets, medical devices, oversized gear, etc.</div>
              </div>
            </label>
          </div>
        </div>

        <!-- STEP 2: Seat Confirmation -->
        <div v-if="currentStep === 2" class="space-y-5">
          <div>
            <h4 class="text-gray-900 font-bold text-base mb-0.5">Step 3 — Seat Confirmation</h4>
            <p class="text-gray-400 text-sm">Confirm or modify the passenger's seat assignment before issuing a boarding pass.</p>
          </div>

          <div class="bg-pink-50 border border-pink-200 rounded-lg p-5 flex items-center justify-between">
            <div>
              <div class="text-xs text-pink-400 font-bold uppercase tracking-wide mb-1">Assigned Seat</div>
              <div class="text-4xl font-black text-pink-600 font-mono">{{ passenger?.seat || 'Unassigned' }}</div>
            </div>
            <div class="text-5xl opacity-20">💺</div>
          </div>

          <label class="flex items-start gap-3 cursor-pointer group p-3 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50/30 transition-all">
            <input type="checkbox" v-model="checks.seatConfirmed" class="mt-0.5 w-4 h-4 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
            <div>
              <div class="text-sm font-semibold text-gray-800 group-hover:text-pink-600 transition-colors">Seat assignment confirmed with passenger</div>
              <div class="text-xs text-gray-400 mt-0.5">Passenger has accepted or upgraded their seat selection.</div>
            </div>
          </label>

          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-700">
            💡 <strong>Tip:</strong> If the passenger did not select a seat during booking, this is the last opportunity to assign one before requiring the passenger to proceed to the gate.
          </div>
        </div>

        <!-- STEP 3: Baggage Drop -->
        <div v-if="currentStep === 3" class="space-y-5">
          <div>
            <h4 class="text-gray-900 font-bold text-base mb-0.5">Step 4 — Baggage Declaration & Drop</h4>
            <p class="text-gray-400 text-sm">Weigh the checked bags, verify against allowances, and print a luggage tag if applicable.</p>
          </div>

          <!-- Allowance -->
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 flex justify-between items-center">
            <div>
              <div class="text-xs text-gray-400 font-bold uppercase tracking-wide">Purchased Allowance</div>
              <div class="text-sm font-semibold text-gray-700 mt-0.5">{{ passenger?.baggage_allowance_name }}</div>
            </div>
            <div class="text-2xl font-black text-pink-500">
              {{ passenger?.allowed_baggage_weight }} <span class="text-sm font-bold text-gray-400">KG</span>
            </div>
          </div>

          <!-- Scale -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">🔢 Scale Reading — Enter Actual Weight</label>
            <div class="relative max-w-xs">
              <input
                type="number"
                v-model="actualWeight"
                min="0"
                step="0.5"
                placeholder="0.0"
                class="w-full border border-gray-300 rounded-lg pl-4 pr-14 py-3 text-2xl font-mono font-black text-gray-900 focus:ring-2 focus:ring-pink-400 focus:border-pink-400 outline-none transition-all"
              >
              <div class="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none text-gray-400 font-bold">KG</div>
            </div>
            <!-- Weight status -->
            <div class="mt-2 text-xs font-medium" v-if="actualWeight !== ''">
              <span v-if="excessWeight > 0" class="text-red-500">
                ⚠️ {{ excessWeight.toFixed(1) }} KG over limit
              </span>
              <span v-else class="text-green-600">
                ✅ Within allowance ({{ (passenger?.allowed_baggage_weight - numericWeight).toFixed(1) }} KG remaining)
              </span>
            </div>
          </div>

          <!-- Excess Warning -->
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="-translate-y-1 opacity-0"
            enter-to-class="translate-y-0 opacity-100"
          >
            <div v-if="excessWeight > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
              <div class="text-sm font-bold text-red-700 mb-0.5">Excess Baggage — Action Required</div>
              <div class="text-xs text-red-500">Passenger is <strong>{{ excessWeight.toFixed(1) }} KG</strong> over their purchased allowance. Collect excess fee before proceeding.</div>
              <label class="flex items-center gap-2 mt-3 cursor-pointer">
                <input type="checkbox" v-model="excessFeePaid" class="w-4 h-4 rounded border-red-300 text-red-500 focus:ring-red-400">
                <span class="text-xs font-bold text-red-700">Excess baggage fee has been collected at the counter</span>
              </label>
            </div>
          </Transition>

          <!-- Power Bank Reminder -->
          <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-700">
            🔋 <strong>Lithium Battery Reminder:</strong> Power banks and spare lithium batteries must be in <strong>carry-on only</strong>. Batteries over 100Wh are prohibited. Flag if found in checked luggage.
          </div>

          <label class="flex items-start gap-3 cursor-pointer group p-3 rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50/30 transition-all">
            <input type="checkbox" v-model="checks.baggageTagPrinted" class="mt-0.5 w-4 h-4 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
            <div>
              <div class="text-sm font-semibold text-gray-800 group-hover:text-pink-600 transition-colors">Luggage tag attached and bag placed on belt</div>
              <div class="text-xs text-gray-400 mt-0.5">Print and attach baggage tag. Send checked bags to the conveyor.</div>
            </div>
          </label>
        </div>

        <!-- STEP 4: Issue Boarding Pass -->
        <div v-if="currentStep === 4" class="space-y-5">
          <div>
            <h4 class="text-gray-900 font-bold text-base mb-0.5">Step 5 — Issue Boarding Pass</h4>
            <p class="text-gray-400 text-sm">All checks complete. Confirm summary and issue the boarding pass to the passenger.</p>
          </div>

          <!-- Summary Card -->
          <div class="border border-gray-200 rounded-lg overflow-hidden">
            <div class="bg-pink-500 px-4 py-2.5">
              <span class="text-white text-sm font-bold">Check-in Summary</span>
            </div>
            <div class="divide-y divide-gray-100">
              <div class="flex justify-between items-center px-4 py-3 text-sm">
                <span class="text-gray-500">PNR</span>
                <span class="font-mono font-bold text-pink-600 bg-pink-50 px-2 py-0.5 rounded">{{ passenger?.pnr }}</span>
              </div>
              <div class="flex justify-between items-center px-4 py-3 text-sm">
                <span class="text-gray-500">Passenger</span>
                <span class="font-bold text-gray-900">{{ passenger?.passenger_name }}</span>
              </div>
              <div class="flex justify-between items-center px-4 py-3 text-sm">
                <span class="text-gray-500">Seat</span>
                <span class="font-mono font-bold text-gray-900">{{ passenger?.seat || 'TBA' }}</span>
              </div>
              <div class="flex justify-between items-center px-4 py-3 text-sm">
                <span class="text-gray-500">Baggage Weight</span>
                <span :class="excessWeight > 0 ? 'text-red-600 font-bold' : 'font-bold text-gray-900'">
                  {{ numericWeight || 0 }} KG
                  <span v-if="excessWeight > 0" class="text-xs text-red-400">(+{{ excessWeight.toFixed(1) }} excess — fee collected)</span>
                </span>
              </div>
              <div class="flex justify-between items-center px-4 py-3 text-sm">
                <span class="text-gray-500">Check-in Status</span>
                <span class="text-green-600 font-bold flex items-center gap-1.5">
                  <span class="w-2 h-2 bg-green-500 rounded-full"></span> Ready to Board
                </span>
              </div>
            </div>
          </div>

          <div class="bg-green-50 border border-green-200 rounded-lg p-3 text-xs text-green-700">
            ✅ All steps verified. Clicking <strong>"Issue Boarding Pass"</strong> will update the passenger's status to <strong>Checked-In</strong> and open the boarding pass for printing.
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 shrink-0 flex items-center justify-between">
        <!-- Status indicator -->
        <div class="text-xs font-medium text-gray-400">
          Step {{ currentStep + 1 }} of {{ steps.length }}
        </div>

        <div class="flex gap-3">
          <button
            v-if="currentStep > 0"
            @click="currentStep--"
            class="px-4 py-2 rounded-lg text-gray-500 font-semibold hover:bg-gray-100 transition-colors text-sm"
          >
            ← Back
          </button>
          <button
            @click="$emit('close')"
            v-if="currentStep === 0"
            class="px-4 py-2 rounded-lg text-gray-400 font-semibold hover:bg-gray-100 transition-colors text-sm"
          >
            Cancel
          </button>

          <!-- Next Step -->
          <button
            v-if="currentStep < steps.length - 1"
            @click="goNext"
            :disabled="!canProceed"
            :class="[
              'px-5 py-2 rounded-lg font-bold text-sm transition-all shadow-sm',
              canProceed ? 'bg-pink-500 hover:bg-pink-600 text-white' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            ]"
          >
            Next →
          </button>

          <!-- Final CTA -->
          <button
            v-if="currentStep === steps.length - 1"
            @click="processCheckin"
            :disabled="isProcessing"
            :class="[
              'px-5 py-2 rounded-lg font-bold text-sm flex items-center gap-2 shadow-sm transition-all',
              !isProcessing ? 'bg-pink-500 hover:bg-pink-600 text-white' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            ]"
          >
            <span v-if="isProcessing" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span v-else>🖨️ Issue Boarding Pass</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  passenger: { type: Object, required: true }
})
const emit = defineEmits(['close', 'checkin-complete'])

const steps = [
  { shortLabel: 'Identification' },
  { shortLabel: 'Documents' },
  { shortLabel: 'Seat' },
  { shortLabel: 'Baggage' },
  { shortLabel: 'Issue Pass' },
]

const currentStep = ref(0)
const isProcessing = ref(false)
const actualWeight = ref('')
const excessFeePaid = ref(false)

const checks = ref({
  pnrConfirmed: false,
  idVerified: false,
  checkinDeadlineMet: false,
  travelDocsValid: false,
  visaChecked: false,
  specialNeedsReviewed: false,
  seatConfirmed: false,
  baggageTagPrinted: false,
})

const numericWeight = computed(() => {
  const p = parseFloat(actualWeight.value)
  return isNaN(p) ? 0 : p
})

const excessWeight = computed(() => {
  if (!props.passenger || props.passenger.allowed_baggage_weight === undefined) return 0
  return Math.max(0, numericWeight.value - props.passenger.allowed_baggage_weight)
})

// Per-step validation
const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return checks.value.pnrConfirmed && checks.value.idVerified && checks.value.checkinDeadlineMet
  }
  if (currentStep.value === 1) {
    return checks.value.travelDocsValid && checks.value.visaChecked && checks.value.specialNeedsReviewed
  }
  if (currentStep.value === 2) {
    return checks.value.seatConfirmed
  }
  if (currentStep.value === 3) {
    const baggageOk = excessWeight.value > 0 ? excessFeePaid.value : true
    return checks.value.baggageTagPrinted && baggageOk
  }
  return true
})

const goNext = () => {
  if (canProceed.value && currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

const processCheckin = async () => {
  isProcessing.value = true
  emit('checkin-complete', {
    booking_detail_id: props.passenger.booking_detail_id,
    actual_baggage_weight: numericWeight.value
  })
}
</script>
