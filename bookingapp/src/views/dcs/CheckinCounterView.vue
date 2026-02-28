<template>
  <div class="max-w-3xl mx-auto">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center p-20 space-y-4">
      <div class="w-12 h-12 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin"></div>
      <p class="text-gray-400 font-medium animate-pulse">Retrieving flight party data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-white rounded-lg shadow-xl overflow-hidden p-10 text-center border border-red-100">
      <div class="text-5xl mb-4">⚠️</div>
      <h3 class="text-xl font-bold text-gray-900 mb-2">PNR Not Found</h3>
      <p class="text-gray-500 mb-6">{{ error }}</p>
      <button @click="goBack" class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2 rounded-md font-bold transition-all">
        Return to Manifest
      </button>
    </div>

    <!-- Success State -->
    <div v-else-if="checkinSuccess" class="bg-white rounded-lg shadow-2xl overflow-hidden flex flex-col border border-green-100">
        <div class="bg-[#0E8028] p-10 relative overflow-hidden flex flex-col items-center">
            <!-- Data Visualization instead of gimmicks -->
            <div class="w-full max-w-xl mb-8 bg-white/10 rounded-xl p-6 border border-white/20 backdrop-blur-sm shadow-xl">
                <div class="flex justify-between items-end mb-4">
                    <div class="text-left">
                        <div class="text-[10px] font-black text-green-200 uppercase tracking-widest mb-1">Processing Summary</div>
                        <div class="text-2xl font-black text-white">{{ schedule?.flight_number }}</div>
                    </div>
                    <div class="text-right">
                        <div class="flex items-baseline gap-1 justify-end">
                            <span class="text-3xl font-black text-white">{{ passengers.filter(p => p.status === 'checkin').length + selectedPassengers.length }}</span>
                            <span class="text-lg text-green-200 font-bold">/ {{ passengers.length }}</span>
                        </div>
                        <div class="text-[10px] font-bold text-green-200 uppercase tracking-widest mt-1">Party Checked In</div>
                    </div>
                </div>
                
                <!-- Party Check-in Progress Bar -->
                <div class="h-2 w-full bg-black/20 rounded-full overflow-hidden flex mb-6">
                    <div class="h-full bg-white transition-all duration-1000 ease-out" 
                         :style="{ width: ((passengers.filter(p => p.status === 'checkin').length + selectedPassengers.length) / passengers.length * 100) + '%' }">
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-black/10 rounded-lg p-4 text-left border border-white/5">
                        <div class="text-[10px] text-green-200 font-bold uppercase tracking-widest mb-1">Currently Processed</div>
                        <div class="flex items-center gap-2">
                           <span class="text-2xl font-black text-white">{{ selectedPassengers.length }}</span>
                           <span class="text-xs font-bold text-green-200">PAX</span>
                        </div>
                    </div>
                    <div class="bg-black/10 rounded-lg p-4 text-left border border-white/5">
                        <div class="text-[10px] text-green-200 font-bold uppercase tracking-widest mb-1">Baggage Cleared</div>
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-2">
                                <span class="text-2xl font-black text-white">{{ numericWeight }}</span>
                                <span class="text-xs font-bold text-green-200">KG</span>
                            </div>
                            <span v-if="excessWeight > 0" class="text-[9px] font-black bg-white text-green-800 px-2 py-0.5 rounded uppercase tracking-widest">Fee Paid</span>
                        </div>
                    </div>
                </div>
            </div>

            <h2 class="text-2xl font-black text-white mb-2">Check-in Processed Successfully</h2>
            <p class="text-green-100 text-sm font-medium">Boarding passes have been issued and manifest updated.</p>
        </div>
        
        <div class="p-8 space-y-6">
            <div class="bg-blue-50 border border-blue-100 rounded-lg p-6 flex items-start gap-4 shadow-sm">
                <div class="text-3xl">📧</div>
                <div>
                    <h4 class="text-blue-900 font-bold mb-1">Digital Delivery Active</h4>
                    <p class="text-blue-700 text-sm leading-relaxed">Passengers just received their boarding passes in their <strong>p@gmail.com</strong>. They can show the PDF QR code on their phone at the gate.</p>
                </div>
            </div>

            <div class="space-y-3">
                <h4 class="text-xs font-black text-gray-400 uppercase tracking-widest pl-1">Physical Backup / Manual Print</h4>
                <div class="grid grid-cols-1 gap-3">
                    <div v-for="p in selectedPassengers" :key="p.id" class="flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors">
                        <div>
                            <div class="font-bold text-gray-900">{{ p.passenger_name }}</div>
                            <div class="text-[10px] text-gray-400 font-mono tracking-widest">{{ pnr }} · SEAT {{ p.seat || 'TBA' }}</div>
                        </div>
                        <button @click="downloadPass(p.booking_detail_id)" class="flex items-center gap-2 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-xs font-black hover:border-pink-500 hover:text-pink-600 transition-all shadow-sm">
                            📥 DOWNLOAD PASS
                        </button>
                    </div>
                </div>
            </div>

            <button @click="goBack" class="w-full bg-gray-900 hover:bg-black text-white py-4 rounded-lg font-black text-lg transition-all shadow-lg active:scale-95 flex items-center justify-center gap-3">
                FINISH & EXIT <span>✨</span>
            </button>
        </div>
    </div>

    <div v-else class="bg-white rounded-lg shadow-2xl overflow-hidden flex flex-col border border-gray-100">
      <!-- Header -->
      <div class="bg-pink-500 px-6 py-5 flex justify-between items-center shrink-0">
        <div>
          <h3 class="text-white font-bold text-lg flex items-center gap-2">
            <span>👩‍💼</span> Check-in Counter — Agent Simulation
          </h3>
          <p class="text-pink-100 text-sm mt-0.5">
            PNR: <span class="font-mono font-bold">{{ pnr }}</span>
            &nbsp;·&nbsp;
            {{ schedule?.flight_number }} {{ schedule?.origin }} → {{ schedule?.destination }}
          </p>
        </div>
        <button @click="goBack" class="text-white/80 hover:text-white transition-colors p-2 rounded-lg hover:bg-pink-600/50 flex items-center gap-2 text-sm font-bold">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Exit
        </button>
      </div>

      <!-- Step Progress Bar -->
      <div class="bg-gray-50 border-b border-gray-200 px-8 py-5 shrink-0">
        <div class="flex items-center gap-0">
          <div
            v-for="(step, idx) in steps"
            :key="idx"
            class="flex items-center"
            :class="idx < steps.length - 1 ? 'flex-1' : ''"
          >
            <div class="flex flex-col items-center">
              <div :class="[
                'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all shadow-sm',
                currentStep > idx
                  ? 'bg-pink-500 text-white'
                  : currentStep === idx
                    ? 'bg-pink-500 text-white ring-4 ring-pink-100 scale-110'
                    : 'bg-white border border-gray-200 text-gray-400'
              ]">
                <svg v-if="currentStep > idx" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                </svg>
                <span v-else>{{ idx + 1 }}</span>
              </div>
              <div class="text-[10px] mt-2 font-bold text-center max-w-[64px] leading-tight uppercase tracking-tighter" :class="currentStep >= idx ? 'text-pink-600' : 'text-gray-400'">
                {{ step.shortLabel }}
              </div>
            </div>
            <div v-if="idx < steps.length - 1" class="flex-1 h-0.5 mb-5 mx-2 rounded-full" :class="currentStep > idx ? 'bg-pink-400' : 'bg-gray-200'"></div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="p-8 min-h-[450px]">

        <!-- STEP 0: Identification & Group Selection -->
        <div v-if="currentStep === 0" class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 bg-pink-50 rounded-md flex items-center justify-center text-xl shrink-0">🪪</div>
            <div>
              <h4 class="text-gray-900 font-bold text-lg mb-0.5">Step 1 — Group Verification</h4>
              <p class="text-gray-400 text-sm">Select the passengers present at the counter. Checking in as a group ensures baggage pooling and seat proximity.</p>
            </div>
          </div>

          <!-- Selection List -->
          <div class="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
            <div class="bg-gray-50 px-4 py-2 flex justify-between items-center border-b border-gray-200">
              <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Travel Party Members</span>
              <button @click="toggleSelectAll" class="text-pink-600 text-[10px] font-black uppercase hover:underline">
                {{ allSelected ? 'Deselect All' : 'Select All' }}
              </button>
            </div>
            <div class="divide-y divide-gray-100">
              <label 
                v-for="p in passengers" 
                :key="p.booking_detail_id" 
                class="flex items-center gap-4 p-4 cursor-pointer hover:bg-pink-50 transition-colors"
                :class="selectedIds.has(p.booking_detail_id) ? 'bg-pink-50/50' : ''"
              >
                <input 
                  type="checkbox" 
                  :checked="selectedIds.has(p.booking_detail_id)" 
                  @change="togglePassenger(p.booking_detail_id)"
                  :disabled="p.status === 'checkin'"
                  class="w-5 h-5 rounded border-gray-300 text-pink-500 focus:ring-pink-400"
                >
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-gray-900">{{ p.passenger_name }}</span>
                    <span v-if="p.status === 'checkin'" class="bg-green-100 text-green-700 text-[10px] px-1.5 py-0.5 rounded-full font-bold uppercase">Already Checked-In</span>
                  </div>
                  <div class="text-xs text-gray-400">{{ p.passenger_type }} · Seat: {{ p.seat || 'TBA' }}</div>
                </div>
                <div class="text-right">
                  <div class="text-[10px] font-bold text-gray-400 uppercase mb-0.5">Allowance</div>
                  <div class="text-xs font-black text-gray-700">{{ p.allowed_baggage_weight }} KG</div>
                </div>
              </label>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-3">
            <label v-for="(check, key) in step0Checks" :key="key" class="flex items-start gap-4 cursor-pointer group p-4 rounded-lg border-2 border-gray-100 hover:border-pink-300 hover:bg-pink-50/30 transition-all shadow-sm">
              <input type="checkbox" v-model="checks[key]" class="mt-1 w-5 h-5 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
              <div>
                <div class="text-sm font-bold text-gray-800 group-hover:text-pink-600 transition-colors">{{ check.label }}</div>
                <div class="text-xs text-gray-400 mt-1 leading-relaxed">{{ check.desc }}</div>
              </div>
            </label>
          </div>
        </div>

        <!-- STEP 1: Document Verification -->
        <div v-if="currentStep === 1" class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 bg-pink-50 rounded-md flex items-center justify-center text-xl shrink-0">🛂</div>
            <div>
              <h4 class="text-gray-900 font-bold text-lg mb-0.5">Step 2 — Document Verification</h4>
              <p class="text-gray-400 text-sm">Review travel documents for all <span class="text-pink-600 font-bold">{{ selectedIds.size }}</span> selected passengers.</p>
            </div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4 flex flex-wrap gap-2">
             <div v-for="p in selectedPassengers" :key="p.id" class="bg-white border border-gray-200 px-3 py-1.5 rounded-lg shadow-sm flex items-center gap-2">
                <span class="text-xs font-bold text-gray-700">{{ p.passenger_name }}</span>
                <span class="w-2 h-2 rounded-full bg-green-500"></span>
             </div>
          </div>

          <div class="grid grid-cols-1 gap-3">
            <label v-for="(check, key) in step1Checks" :key="key" class="flex items-start gap-4 cursor-pointer group p-4 rounded-lg border-2 border-gray-100 hover:border-pink-300 hover:bg-pink-50/30 transition-all shadow-sm">
              <input type="checkbox" v-model="checks[key]" class="mt-1 w-5 h-5 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
              <div>
                <div class="text-sm font-bold text-gray-800 group-hover:text-pink-600 transition-colors">{{ check.label }}</div>
                <div class="text-xs text-gray-400 mt-1 leading-relaxed">{{ check.desc }}</div>
              </div>
            </label>
          </div>
        </div>

        <!-- STEP 2: Seat Confirmation -->
        <div v-if="currentStep === 2" class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 bg-pink-50 rounded-md flex items-center justify-center text-xl shrink-0">💺</div>
            <div>
              <h4 class="text-gray-900 font-bold text-lg mb-0.5">Step 3 — Proximity Check</h4>
              <p class="text-gray-400 text-sm">Group check-in prioritizes keeping party members together.</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div v-for="p in selectedPassengers" :key="p.id" class="bg-white border-2 border-pink-50 rounded-lg p-6 flex flex-col items-center justify-center shadow-sm relative overflow-hidden group">
              <div class="absolute top-0 right-0 p-2 opacity-5 text-4xl transform rotate-12 transition-transform group-hover:rotate-0">💺</div>
              <div class="text-[10px] text-pink-400 font-black uppercase tracking-widest mb-1">{{ p.passenger_name }}</div>
              <div class="text-4xl font-black text-pink-600 font-mono tracking-tighter">{{ p.seat || 'TBA' }}</div>
            </div>
          </div>

          <label class="flex items-start gap-4 cursor-pointer group p-5 rounded-lg border-2 border-pink-100 bg-pink-50/20 hover:border-pink-300 transition-all shadow-sm">
            <input type="checkbox" v-model="checks.seatConfirmed" class="mt-1 w-5 h-5 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
            <div>
              <div class="text-sm font-bold text-gray-800 group-hover:text-pink-600 transition-colors">Group Seating Confirmed</div>
              <div class="text-xs text-gray-400 mt-1 leading-relaxed">Passengers have confirmed they are satisfied with their current proximity.</div>
            </div>
          </label>
        </div>

        <!-- STEP 3: Baggage Pooling -->
        <div v-if="currentStep === 3" class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 bg-pink-50 rounded-md flex items-center justify-center text-xl shrink-0">💼</div>
            <div>
              <h4 class="text-gray-900 font-bold text-lg mb-0.5">Step 4 — Allowance Pooling</h4>
              <p class="text-gray-400 text-sm">Real-world efficiency: We've combined the individual baggage limits of all <span class="text-pink-600 font-bold">{{ selectedIds.size }}</span> members.</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <!-- Pooled Allowance -->
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 relative overflow-hidden">
               <div class="absolute -right-4 -bottom-4 opacity-5 text-8xl transform -rotate-12">📦</div>
              <div class="text-xs text-gray-400 font-black uppercase tracking-widest mb-1">Total Group Allowance</div>
              <div class="text-sm font-bold text-gray-500 mb-3">POOLED LIMIT</div>
              <div class="flex items-baseline gap-2">
                <div class="text-5xl font-black text-pink-500">{{ totalAllowedWeight }}</div>
                <div class="text-xl font-bold text-gray-400">KG</div>
              </div>
              <div class="mt-4 pt-4 border-t border-gray-200">
                 <div class="flex justify-between text-[10px] text-gray-400 font-bold uppercase mb-1">
                    <span>Contributors</span>
                    <span>Individual</span>
                 </div>
                 <div v-for="p in selectedPassengers" :key="p.booking_detail_id" class="flex justify-between text-xs py-1">
                    <span class="text-gray-600 truncate w-32">{{ p.passenger_name }}</span>
                    <span class="font-mono text-gray-400">{{ p.allowed_baggage_weight }} KG</span>
                 </div>
              </div>
            </div>

            <!-- Group Scale -->
            <div class="bg-gray-900 rounded-lg p-6 shadow-2xl overflow-hidden relative border-4 border-gray-800">
              <div class="absolute top-0 right-0 p-3 opacity-10 text-white text-5xl">⚖️</div>
              <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-3">🔢 Digital Scale (Total)</label>
              <div class="relative">
                <input
                  type="number"
                  v-model="actualWeight"
                  min="0"
                  step="0.5"
                  placeholder="0.0"
                  class="w-full bg-transparent border-b-2 border-gray-700 text-white text-5xl font-mono tracking-widest font-black py-2 outline-none focus:border-pink-500 transition-all font-mono"
                >
                <div class="absolute right-0 bottom-3 text-gray-500 font-black text-xl font-mono">KG</div>
              </div>
              <div class="mt-4 flex items-center gap-2">
                <div class="w-2 h-2 rounded-full" :class="numericWeight > 0 ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]' : 'bg-gray-700'"></div>
                <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">POOLED SCALE ACTIVE</span>
              </div>
            </div>
          </div>

          <!-- Pooled weight status -->
          <div v-if="actualWeight !== ''" class="flex justify-center">
            <div v-if="excessWeight > 0" class="bg-red-50 text-red-600 px-4 py-2 rounded-full font-black text-sm animate-bounce shadow-sm flex items-center gap-2">
              ⚠️ {{ excessWeight.toFixed(1) }} KG OVER GROUP LIMIT
            </div>
            <div v-else class="bg-green-50 text-green-600 px-4 py-2 rounded-full font-black text-sm shadow-sm flex items-center gap-2">
              ✅ POOLED WEIGHT OK ({{ (totalAllowedWeight - numericWeight).toFixed(1) }} KG REMAINING)
            </div>
          </div>

          <div v-if="excessWeight > 0" class="bg-red-50 border-2 border-red-100 rounded-lg p-6 shadow-sm">
            <div class="flex items-center gap-3 mb-2">
              <span class="text-2xl">💰</span>
              <h5 class="text-base font-black text-red-800 uppercase tracking-tight">Excess Weight Charge</h5>
            </div>
            <p class="text-sm text-red-600 leading-relaxed mb-4 font-medium">
              The group's total weight exceeds their combined allowance. Please process the excess baggage fee for <strong>{{ excessWeight.toFixed(1) }} KG</strong>.
            </p>
            <label class="flex items-center gap-3 p-3 bg-red-100/50 rounded-md cursor-pointer hover:bg-red-100 transition-colors border border-red-200">
              <input type="checkbox" v-model="excessFeePaid" class="w-5 h-5 rounded border-red-300 text-red-600 focus:ring-red-500">
              <span class="text-sm font-black text-red-800">Excess fee collected for group baggage</span>
            </label>
          </div>

          <label class="flex items-start gap-4 cursor-pointer group p-5 rounded-lg border-2 border-gray-100 hover:border-pink-300 hover:bg-pink-50/30 transition-all shadow-sm">
            <input type="checkbox" v-model="checks.baggageTagPrinted" class="mt-1 w-5 h-5 rounded border-gray-300 text-pink-500 focus:ring-pink-400">
            <div>
              <div class="text-sm font-bold text-gray-800 group-hover:text-pink-600 transition-colors">Multiple baggage tags issued and attached</div>
              <div class="text-xs text-gray-400 mt-1 leading-relaxed">Prepare tags for each checked suitcase in the party.</div>
            </div>
          </label>
        </div>

        <!-- STEP 4: Group Issue -->
        <div v-if="currentStep === 4" class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 bg-pink-50 rounded-md flex items-center justify-center text-xl shrink-0">🖨️</div>
            <div>
              <h4 class="text-gray-900 font-bold text-lg mb-0.5">Final Confirmation — Bulk Issuance</h4>
              <p class="text-gray-400 text-sm">Review the summary. Handing over all boarding passes in a stack is the preferred agent workflow.</p>
            </div>
          </div>

          <div class="bg-white border-2 border-gray-100 rounded-lg overflow-hidden shadow-lg">
            <div class="bg-gray-900 px-6 py-4 flex justify-between items-center">
              <span class="text-pink-500 font-black tracking-[0.2em] text-xs">GROUP BOARDING PASSES</span>
              <span class="text-white font-mono text-sm opacity-50">QTY: {{ selectedIds.size }}</span>
            </div>
            <div class="divide-y divide-gray-100 max-h-[300px] overflow-y-auto">
                <div v-for="p in selectedPassengers" :key="p.booking_detail_id" class="p-6 flex justify-between items-center">
                    <div>
                        <div class="text-xs font-black text-gray-400 uppercase tracking-widest mb-0.5">Passenger</div>
                        <div class="text-lg font-bold text-gray-900">{{ p.passenger_name }}</div>
                        <div class="text-[10px] text-gray-400">{{ p.passenger_type }}</div>
                    </div>
                    <div class="text-right">
                        <div class="text-xs font-black text-pink-400 uppercase tracking-widest mb-0.5">Seat</div>
                        <div class="text-xl font-black text-gray-900">{{ p.seat || 'TBA' }}</div>
                    </div>
                </div>
            </div>
            <div class="px-8 pb-8 pt-6 border-t border-dashed border-gray-200">
              <div class="bg-green-50 rounded-lg p-4 flex items-center justify-between border border-green-100">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white shadow-lg shadow-green-200">
                    <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                    </svg>
                  </div>
                  <div>
                    <div class="text-sm font-black text-green-800 uppercase tracking-tight">Party Ready</div>
                    <div class="text-[10px] font-bold text-green-600">ALL DOCUMENTS & POOLED BAGGAGE VERIFIED</div>
                  </div>
                </div>
                <div v-if="numericWeight > 0" class="text-right">
                  <div class="text-[10px] font-black text-green-400 uppercase">Pooled Luggage</div>
                  <div class="text-sm font-black text-green-800">{{ numericWeight }} KG</div>
                </div>
              </div>
            </div>
          </div>
          <p class="text-center text-gray-400 text-[10px] italic">Boarding passes will be printed in sequence for efficient distribution by the agent.</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-8 py-6 bg-gray-50 border-t border-gray-200 shrink-0 flex items-center justify-between">
        <div class="flex items-center gap-3">
            <div class="text-xs font-black text-gray-400 uppercase tracking-widest">Steps</div>
            <div class="flex gap-1">
                <div v-for="i in steps.length" :key="i" class="w-4 h-1 rounded-full transition-all duration-500" :class="i <= currentStep + 1 ? 'bg-pink-500 w-6' : 'bg-gray-200'"></div>
            </div>
        </div>

        <div class="flex gap-4">
          <button
            v-if="currentStep > 0"
            @click="currentStep--"
            class="px-6 py-2.5 rounded-md text-gray-500 font-bold hover:bg-gray-100 transition-colors text-sm border border-gray-200"
          >
            ← Back
          </button>

          <button
            v-if="currentStep < steps.length - 1"
            @click="goNext"
            :disabled="!canProceed"
            :class="[
              'px-8 py-2.5 rounded-md font-black text-sm transition-all shadow-md active:scale-95',
              canProceed ? 'bg-pink-500 hover:bg-pink-600 text-white shadow-pink-200' : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'
            ]"
          >
            Next Step →
          </button>

          <button
            v-if="currentStep === steps.length - 1"
            @click="processCheckin"
            :disabled="isProcessing"
            :class="[
              'px-10 py-2.5 rounded-md font-black text-sm flex items-center gap-3 transition-all active:scale-95 shadow-lg',
              !isProcessing ? 'bg-pink-500 hover:bg-pink-600 text-white shadow-pink-200' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            ]"
          >
            <span v-if="isProcessing" class="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span v-else class="flex items-center gap-2 tracking-tight">🖨️ ISSUE ALL TICKETS</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDcsStore } from '@/stores/dcs'
import { useUserStore } from '@/stores/user'
import { dcsService } from '@/services/api/dcsService'

const route = useRoute()
const router = useRouter()
const dcsStore = useDcsStore()
const userStore = useUserStore()

const pnr = ref('')
const schedule = ref(null)
const passengers = ref([])
const selectedIds = ref(new Set())

const isLoading = ref(true)
const error = ref(null)
const checkinSuccess = ref(false)

const steps = [
  { shortLabel: 'Party' },
  { shortLabel: 'Docs' },
  { shortLabel: 'Seats' },
  { shortLabel: 'Bags' },
  { shortLabel: 'Finish' },
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

const selectedPassengers = computed(() => {
    return passengers.value.filter(p => selectedIds.value.has(p.booking_detail_id))
})

const totalAllowedWeight = computed(() => {
    return selectedPassengers.value.reduce((sum, p) => sum + (p.allowed_baggage_weight || 0), 0)
})

const excessWeight = computed(() => {
  return Math.max(0, numericWeight.value - totalAllowedWeight.value)
})

const allSelected = computed(() => {
    const checkable = passengers.value.filter(p => p.status !== 'checkin')
    return checkable.length > 0 && selectedIds.value.size === checkable.length
})

const step0Checks = {
  pnrConfirmed: { label: 'PNR verified against the system', desc: 'Confirm the booking reference matches an active group booking.' },
  idVerified: { label: 'All IDs / Passports verified', desc: 'Verify names for every selected passenger.' },
  checkinDeadlineMet: { label: 'Deadline verified', desc: 'Ensure cutoff window is respected.' }
}

const step1Checks = {
  travelDocsValid: { label: 'All travel documents valid', desc: 'Check expiry dates for entire party.' },
  visaChecked: { label: 'Visas verified for group', desc: 'Confirm entry rights for all members.' },
  specialNeedsReviewed: { label: 'Group special needs reviewed', desc: 'Assistance, infants, or elderly support confirmed.' }
}

onMounted(async () => {
    try {
        const id = route.params.booking_detail_id
        // First try to get details of the triggered passenger to find their PNR
        const initResp = await dcsService.getPassengerDetails(id)
        const initData = initResp.data
        
        pnr.value = initData.pnr
        schedule.value = initData.schedule
        
        // NOW load the full party using the new PNR endpoint
        const groupResp = await dcsService.getPnrDetails(pnr.value, schedule.value.id)
        passengers.value = groupResp.data.passengers
        
        // Auto-select the passenger we clicked from, plus any siblings not checked in
        passengers.value.forEach(p => {
            if (p.status !== 'checkin') {
                selectedIds.value.add(p.booking_detail_id)
            }
        })

    } catch (err) {
        console.error('Failed to load group:', err)
        error.value = err.response?.data?.error || 'Could not retrieve group data.'
    } finally {
        isLoading.value = false
    }
})

const togglePassenger = (id) => {
    if (selectedIds.value.has(id)) {
        selectedIds.value.delete(id)
    } else {
        selectedIds.value.add(id)
    }
}

const toggleSelectAll = () => {
    if (allSelected.value) {
        selectedIds.value.clear()
    } else {
        passengers.value.forEach(p => {
            if (p.status !== 'checkin') selectedIds.value.add(p.booking_detail_id)
        })
    }
}

const canProceed = computed(() => {
  if (selectedIds.value.size === 0) return false

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

const goBack = () => {
    if (schedule.value?.id) {
        router.push(`/dcs/manifest/${schedule.value.id}`)
    } else {
        router.push('/dcs/dashboard')
    }
}

const processCheckin = async () => {
  isProcessing.value = true
  
  const payload = Array.from(selectedIds.value).map((id, index) => ({
      booking_detail_id: id,
      actual_weight: index === 0 ? numericWeight.value : 0 
  }))

  const success = await dcsStore.processCheckin(payload)
  
  if (success) {
      setTimeout(() => {
          checkinSuccess.value = true
          isProcessing.value = false
      }, 800)
  } else {
      isProcessing.value = false
      alert("Check-in failed. Please try again.")
  }
}

const downloadPass = (id) => {
    // Open in new tab or trigger download
    window.open(`http://localhost:8000/api/dcs/boarding-pass/${id}/`, '_blank')
}
</script>

<style scoped>

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
