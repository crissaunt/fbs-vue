<template>
  <div class="min-h-screen bg-gray-50 pb-24 lg:pb-6">
    <BookingStatusHeader />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">

      <!-- Page Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
        <div class="flex items-center gap-3">
          <button @click="$router.back()"
            class="flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-800 transition-colors">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            Add-ons
          </button>
          <span class="text-gray-300">/</span>
          <h1 class="text-base font-bold text-gray-900">Seat Selection</h1>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500 font-medium">{{ Object.keys(assignedSeats).length }}/{{ eligiblePassengers.length }} selected</span>
          <div class="h-1 bg-gray-200 rounded-full w-20 overflow-hidden">
            <div class="h-full bg-pink-500 rounded-full transition-all duration-500"
              :style="{ width: (Object.keys(assignedSeats).length / Math.max(eligiblePassengers.length, 1) * 100) + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- Flight Segment Switcher (Round Trip / Multi-City) -->
      <div v-if="bookingStore.isRoundTrip || bookingStore.tripType.includes('multi')"
        class="flex gap-2 mb-3 overflow-x-auto pb-1">
        <button
          v-for="segment in flightSegments"
          :key="segment.key"
          @click="switchFlightSegment(segment.key)"
          :class="[
            'flex items-center gap-2.5 px-4 py-2.5 rounded-sm text-sm font-semibold transition-all flex-shrink-0',
            activeFlightSegment === segment.key
              ? 'bg-[#003870] text-white shadow-md'
              : 'bg-white text-gray-600 border border-gray-200 hover:border-[#003870] hover:text-[#003870]'
          ]">
          <span>{{ segment.key === 'depart' ? '✈️' : segment.key === 'return' ? '🔄' : '📍' }}</span>
          <div class="text-left">
            <p class="leading-tight">{{ segment.label }}</p>
            <p class="text-[10px] font-normal opacity-70">{{ segment.flight }}</p>
          </div>
          <span v-if="getSeatsForSegment(segment.key).length > 0"
            class="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded"
            :class="activeFlightSegment === segment.key ? 'bg-white/20 text-white' : 'bg-green-100 text-green-700'">
            {{ getSeatsForSegment(segment.key).length }}/{{ eligiblePassengers.length }}
          </span>
        </button>
      </div>

      <!-- One-Way: compact route header -->
      <div v-else class="flex items-center gap-2 mb-5">
        <div class="w-7 h-7 rounded-sm bg-pink-100 flex items-center justify-center flex-shrink-0">
          <svg class="w-4 h-4 text-pink-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </div>
        <p class="text-sm font-semibold text-gray-700">
          {{ bookingStore.selectedOutbound?.origin }} <span class="text-pink-500 mx-1">→</span> {{ bookingStore.selectedOutbound?.destination }}
        </p>
        <span class="text-xs text-gray-400 font-mono">{{ currentFlight?.flight_number }}</span>
      </div>

      <!-- Loading -->
      <div v-if="isLoading && rawSeats.length === 0" class="flex flex-col items-center justify-center py-16 gap-4">
        <div class="w-10 h-10 border-4 border-pink-100 border-t-pink-500 rounded-full animate-spin"></div>
        <p class="text-[13px] text-gray-400 font-medium">Loading seat map...</p>
      </div>

      <!-- No Seats -->
      <div v-else-if="rawSeats.length === 0" class="flex flex-col items-center justify-center py-16 gap-4 bg-white rounded-sm border border-gray-100 shadow-sm">
        <div class="w-14 h-14 bg-gray-50 rounded-full flex items-center justify-center text-3xl">💺</div>
        <div class="text-center">
          <p class="text-sm font-bold text-gray-800">No seats available</p>
          <p class="text-xs text-gray-400 mt-1">Seat data is not available for this flight.</p>
        </div>
      </div>

      <!-- MAIN SEAT SELECTION GRID -->
      <div v-else class="flex flex-col xl:flex-row gap-5 items-start">

        <!-- LEFT: Passenger Panel -->
        <div class="w-full xl:w-64 flex-shrink-0 space-y-4">

          <!-- Passenger List -->
          <div class="bg-white rounded-sm border border-gray-100 shadow-sm overflow-hidden">
            <div class="bg-gradient-to-r from-[#003870] to-[#004f9e] px-4 py-3">
              <p class="text-xs font-bold uppercase tracking-widest text-white/70">Passengers</p>
            </div>
            <div class="divide-y divide-gray-50">
              <div
                v-for="(p, index) in eligiblePassengers"
                :key="p.key"
                @click="p.type !== 'Infant' ? activePIndex = index : null"
                :class="[
                  'px-4 py-3 flex items-center justify-between gap-2 transition-all',
                  p.type !== 'Infant' ? 'cursor-pointer' : 'cursor-default opacity-60',
                  activePIndex === index && p.type !== 'Infant'
                    ? 'bg-pink-50 border-l-2 border-l-pink-500'
                    : 'hover:bg-gray-50'
                ]">
                <div class="flex items-center gap-2.5 min-w-0">
                  <div class="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-black flex-shrink-0"
                    :class="activePIndex === index && p.type !== 'Infant' ? 'bg-pink-500 text-white' : 'bg-gray-100 text-gray-600'">
                    {{ index + 1 }}
                  </div>
                  <div class="min-w-0">
                    <p class="text-xs font-semibold text-gray-900 truncate">{{ p.firstName }} {{ p.lastName }}</p>
                    <p class="text-[10px] text-gray-400 uppercase tracking-wide">{{ p.type }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-1.5 flex-shrink-0">
                  <span v-if="p.type === 'Infant'" class="text-[10px] text-orange-600 font-semibold">
                    {{ getInfantSeat(p.key) ? `Lap: ${getInfantSeat(p.key).seat_code}` : 'Awaiting' }}
                  </span>
                  <template v-else>
                    <span class="text-[10px] font-black px-2 py-1 rounded"
                      :class="assignedSeats[p.key] ? 'bg-pink-100 text-pink-600' : 'bg-gray-100 text-gray-400'">
                      {{ assignedSeats[p.key]?.seat_code || '—' }}
                    </span>
                    <button v-if="assignedSeats[p.key]" @click.stop="changeSeat(p.key)"
                      class="w-5 h-5 rounded flex items-center justify-center text-gray-400 hover:text-pink-500 hover:bg-pink-50 transition-colors text-sm">↻</button>
                  </template>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div v-if="bookingStore.isRoundTrip" class="bg-white rounded-sm border border-gray-100 shadow-sm p-4 space-y-2">
            <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">Quick Actions</p>
            <button @click="copySeatsToReturn"
              :disabled="!hasDepartSeats"
              :class="['w-full text-xs font-semibold py-2 px-3 rounded-sm border transition-all flex items-center gap-2', hasDepartSeats ? 'border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100' : 'border-gray-200 text-gray-300 cursor-not-allowed bg-gray-50']">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
              Copy Depart → Return
            </button>
            <button @click="clearSegmentSeats"
              class="w-full text-xs font-semibold py-2 px-3 rounded-sm border border-gray-200 text-gray-500 bg-white hover:bg-red-50 hover:border-red-200 hover:text-red-600 transition-all flex items-center gap-2">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              Clear {{ activeFlightSegmentLabel }}
            </button>
          </div>

          <!-- Seat Class Legend -->
          <div class="bg-white rounded-sm border border-gray-100 shadow-sm p-4">
            <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3">Class Guide</p>
            <div class="space-y-2">
              <div v-for="sc in seatClasses" :key="sc.id" class="flex items-center gap-2.5">
                <span class="w-3 h-3 rounded-sm flex-shrink-0" :style="{ backgroundColor: getClassColor(sc.name) }"></span>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-semibold text-gray-800">{{ sc.name }}</p>
                </div>
                <span class="text-[10px] font-bold text-gray-400">×{{ sc.price_multiplier }}</span>
              </div>
              <!-- Status Legend -->
              <div class="border-t border-gray-100 pt-2 mt-2 space-y-1.5">
                <div class="flex items-center gap-2"><span class="w-5 h-5 rounded-sm border-2 border-gray-200 bg-white flex-shrink-0"></span><span class="text-[11px] text-gray-500">Available</span></div>
                <div class="flex items-center gap-2"><span class="w-5 h-5 rounded-sm border-2 border-pink-500 bg-pink-50 flex-shrink-0"></span><span class="text-[11px] text-gray-500">Selected</span></div>
                <div class="flex items-center gap-2"><span class="w-5 h-5 rounded-sm bg-gray-200 flex-shrink-0"></span><span class="text-[11px] text-gray-500">Occupied</span></div>
                <div class="flex items-center gap-2"><span class="w-5 h-5 rounded-sm border-2 border-amber-400 bg-amber-50 flex-shrink-0"></span><span class="text-[11px] text-gray-500">Extra Legroom</span></div>
              </div>
            </div>
          </div>
        </div>

        <!-- CENTER: Aircraft Seat Map -->
        <div class="flex-1 min-w-0">
          <div class="bg-white rounded-sm border border-gray-100 shadow-sm overflow-hidden">
            <!-- Aircraft Header -->
            <div class="flex items-center justify-between px-5 py-3.5 border-b border-gray-100 bg-gray-50/60">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-sm bg-[#003870] flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-bold text-gray-900">{{ aircraftModel || 'Aircraft' }}</p>
                  <p class="text-[10px] text-gray-400">{{ activeFlightSegmentLabel }} · {{ currentFlight?.flight_number || 'N/A' }} · {{ aircraftCapacity }} seats</p>
                </div>
              </div>
              <div class="flex items-center gap-2 text-xs">
                <span :class="['font-bold px-2.5 py-1 rounded-sm', Object.keys(assignedSeats).length === eligiblePassengers.length && eligiblePassengers.length > 0 ? 'bg-green-100 text-green-700' : 'bg-pink-50 text-pink-600']">
                  {{ Object.keys(assignedSeats).length }}/{{ eligiblePassengers.length }} selected
                </span>
              </div>
            </div>

            <!-- Seat Map scroll container -->
            <div class="overflow-x-auto overflow-y-auto max-h-[65vh] p-6 md:p-6">
              <div class="min-w-[300px] mx-auto" style="max-width: 450px;">

                <!-- Plane Nose SVG -->
                <div class="flex justify-center mb-4">
                  <svg width="60" height="36" viewBox="0 0 60 36" fill="none">
                    <path d="M30 0 C30 0 56 14 58 28 L2 28 C4 14 30 0 30 0Z" fill="#e5e7eb" stroke="#d1d5db" stroke-width="1"/>
                    <text x="30" y="22" text-anchor="middle" font-size="10" fill="#9ca3af" font-family="sans-serif">FRONT</text>
                  </svg>
                </div>

                <!-- Cabin Sections -->
                <div v-for="seatClass in seatClasses" :key="seatClass.id"
                  :class="['mb-6', { 'opacity-40 pointer-events-none': isClassDimmed(seatClass.name) }]">

                  <!-- Cabin divider -->
                  <div class="flex items-center gap-2 mb-3">
                    <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: getClassColor(seatClass.name) }"></span>
                    <div class="flex-1 border-t" :style="{ borderColor: getClassColor(seatClass.name) + '40' }"></div>
                    <span class="text-[10px] font-black uppercase tracking-widest px-2" :style="{ color: getClassColor(seatClass.name) }">
                      {{ seatClass.name }} · ×{{ seatClass.price_multiplier }}
                    </span>
                    <span v-if="isClassDimmed(seatClass.name)" class="text-[9px] font-bold bg-gray-200 text-gray-500 px-1.5 py-0.5 rounded">RESTRICTED</span>
                    <div class="flex-1 border-t" :style="{ borderColor: getClassColor(seatClass.name) + '40' }"></div>
                  </div>

                  <!-- Rows -->
                  <div v-for="rowGroup in getRowGroupsByClass(seatClass.id)" :key="rowGroup.row">
                    <!-- Exit Row Banner -->
                    <div v-if="rowGroup.isExitRow" class="flex items-center gap-2 my-1 px-2">
                      <div class="flex-1 h-px bg-green-200"></div>
                      <span class="text-sm font-bold text-green-600 bg-green-50 border border-green-200 px-2 py-0.5 rounded">🚪 EMERGENCY EXIT</span>
                      <div class="flex-1 h-px bg-green-200"></div>
                    </div>

                    <div class="flex items-center gap-1 mb-1.5 ">
                      <!-- Left seats -->
                      <div class="flex gap-3">
                        <button
                          v-for="seat in rowGroup.leftSeats"
                          :key="seat.id"
                          @click="assignSeat(seat)"
                          :disabled="getSeatStatus(seat) === 'occupied' || getSeatStatus(seat) === 'taken-by-other' || isClassDimmed(seat.seat_class?.name)"
                          :title="getSeatTooltip(seat)"
                          :class="[
                            'w-15 h-15 rounded-sm text-sm font-bold transition-all relative flex flex-col items-center justify-center border-2',
                            getSeatStatus(seat) === 'selected'
                              ? 'bg-pink-500 border-pink-500 text-white shadow-md'
                              : getSeatStatus(seat) === 'occupied' || getSeatStatus(seat) === 'taken-by-other'
                                ? 'bg-gray-100 border-gray-100 text-gray-400 cursor-not-allowed opacity-60'
                                : seat.has_extra_legroom
                                  ? 'bg-amber-50 border-amber-300 text-gray-700 hover:bg-amber-100 hover:scale-105'
                                  : 'bg-white border-gray-200 text-gray-700 hover:border-pink-400 hover:scale-105'
                          ]"
                          :style="getSeatStatus(seat) === 'available' && !seat.has_extra_legroom ? { borderColor: getClassColor(seatClass.name) + '60' } : {}">
                          <span class="text-[10px] leading-none">{{ seat.column }}</span>
                          <span v-if="getSeatStatus(seat) === 'occupied'" class="text-[7px] leading-none mt-0.5">🔒</span>
                          <template v-else>
                            <span v-if="seat.is_exit_row" class="text-[7px] leading-none mt-0.5">🚪</span>
                            <span v-else-if="seat.has_extra_legroom" class="text-[7px] leading-none mt-0.5">↕</span>
                            <span v-else-if="seat.is_wheelchair_accessible" class="text-[7px] leading-none mt-0.5">♿</span>
                          </template>
                        </button>
                      </div>

                      <!-- Row Number (Aisle) -->
                      <div class="w-7 text-center text-sm mx-4 font-black text-gray-300 flex-shrink-0  ">
                        {{ rowGroup.globalRow }}
                      </div>

                      <!-- Right seats -->
                      <div class="flex gap-3 ">
                        <button
                          v-for="seat in rowGroup.rightSeats"
                          :key="seat.id"
                          @click="assignSeat(seat)"
                          :disabled="getSeatStatus(seat) === 'occupied' || getSeatStatus(seat) === 'taken-by-other' || isClassDimmed(seat.seat_class?.name)"
                          :title="getSeatTooltip(seat)"
                          :class="[
                            'w-15 h-15 rounded-sm text-xs font-bold transition-all relative flex flex-col items-center justify-center border-2',
                            getSeatStatus(seat) === 'selected'
                              ? 'bg-pink-500 border-pink-500 text-white shadow-md'
                              : getSeatStatus(seat) === 'occupied' || getSeatStatus(seat) === 'taken-by-other'
                                ? 'bg-gray-100 border-gray-100 text-gray-400 cursor-not-allowed opacity-60'
                                : seat.has_extra_legroom
                                  ? 'bg-amber-50 border-amber-300 text-gray-700 hover:bg-amber-100 hover:scale-105'
                                  : 'bg-white border-gray-200 text-gray-700 hover:border-pink-400 hover:scale-105'
                          ]"
                          :style="getSeatStatus(seat) === 'available' && !seat.has_extra_legroom ? { borderColor: getClassColor(seatClass.name) + '60' } : {}">
                          <span class="text-[10px] leading-none">{{ seat.column }}</span>
                          <span v-if="getSeatStatus(seat) === 'occupied'" class="text-[7px] leading-none mt-0.5">🔒</span>
                          <template v-else>
                            <span v-if="seat.is_exit_row" class="text-[7px] leading-none mt-0.5">🚪</span>
                            <span v-else-if="seat.has_extra_legroom" class="text-[7px] leading-none mt-0.5">↕</span>
                            <span v-else-if="seat.is_wheelchair_accessible" class="text-[7px] leading-none mt-0.5">♿</span>
                          </template>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Tail -->
                <div class="flex justify-center mt-4">
                  <svg width="60" height="24" viewBox="0 0 60 24" fill="none">
                    <path d="M2 0 L58 0 C56 12 30 24 30 24 C30 24 4 12 2 0Z" fill="#e5e7eb" stroke="#d1d5db" stroke-width="1"/>
                  </svg>
                </div>

              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT: Selection Summary & Actions -->
        <div class="w-full xl:w-64 flex-shrink-0 space-y-4">

          <!-- Progress (Multi-City / Round-Trip) -->
          <div v-if="bookingStore.isRoundTrip || bookingStore.tripType.includes('multi')"
            class="bg-white rounded-sm border border-gray-100 shadow-sm p-4">
            <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3">Segment Progress</p>
            <div class="space-y-3">
              <div v-for="seg in segmentProgress" :key="seg.key">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-xs font-semibold text-gray-700">{{ seg.label }}</span>
                  <span class="text-[10px] font-bold text-gray-400">{{ seg.count }}/{{ eligiblePassengers.length }}</span>
                </div>
                <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full bg-pink-500 rounded-full transition-all duration-500" :style="{ width: seg.percent + '%' }"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Current Selection Summary -->
          <div v-if="hasSelections" class="bg-white rounded-sm border border-gray-100 shadow-sm overflow-hidden">
            <div class="bg-gray-50/80 px-4 py-3 border-b border-gray-100">
              <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Your Selection</p>
              <p class="text-[11px] text-gray-500 mt-0.5">{{ activeFlightSegmentLabel }} Flight</p>
            </div>
            <div class="px-4 py-3 space-y-2.5 max-h-64 overflow-y-auto">
              <!-- Adult seats -->
              <div v-for="(seat, pKey) in assignedSeats" :key="pKey"
                class="flex items-center justify-between gap-2 py-2 border-b border-gray-50 last:border-0">
                <div class="min-w-0">
                  <p class="text-xs font-semibold text-gray-800 truncate">{{ getPassengerName(pKey) }}</p>
                  <div class="flex items-center gap-1.5 mt-0.5">
                    <span class="text-[10px] font-black px-1.5 py-0.5 rounded bg-pink-100 text-pink-600">{{ seat.seat_code }}</span>
                    <span class="text-[10px] text-gray-400">{{ seat.seat_class?.name }}</span>
                  </div>
                </div>
                <div class="flex items-center gap-1.5 flex-shrink-0">
                  <span class="text-xs font-bold text-gray-700">₱{{ (seat.seat_price || 0).toLocaleString() }}</span>
                  <button @click="removeSeat(pKey)"
                    class="w-5 h-5 rounded text-gray-400 hover:text-red-500 hover:bg-red-50 flex items-center justify-center text-sm font-bold transition-colors">×</button>
                </div>
              </div>

              <!-- Infant seats -->
              <div v-for="infant in mappedInfants" :key="infant.key"
                class="flex items-center justify-between gap-2 py-2 border-b border-gray-50 last:border-0">
                <div class="min-w-0">
                  <p class="text-xs font-semibold text-gray-800 truncate">{{ infant.firstName }} {{ infant.lastName }}</p>
                  <span class="text-[10px] px-1.5 py-0.5 rounded bg-orange-100 text-orange-600 font-bold">Lap · {{ infant.adultName }}</span>
                </div>
                <span class="text-[10px] font-bold text-emerald-600 flex-shrink-0">FREE</span>
              </div>
            </div>

            <!-- Price Summary -->
            <div class="px-4 py-3 bg-gray-50/60 border-t border-gray-100 space-y-1.5">
              <div class="flex justify-between items-center text-xs">
                <span class="text-gray-500">{{ activeFlightSegmentLabel }} Seat Fees</span>
                <span class="font-bold text-gray-800">₱{{ segmentSeatTotal.toLocaleString() }}</span>
              </div>
              <div v-if="bookingStore.isRoundTrip" class="flex justify-between items-center text-xs border-t border-gray-200 pt-1.5 mt-1.5">
                <span class="text-gray-700 font-semibold">Total Seat Fees</span>
                <span class="font-black text-pink-500">₱{{ totalSeats.toLocaleString() }}</span>
              </div>
              <p class="text-[10px] text-gray-400">*Base fare not included</p>
            </div>
          </div>

          <!-- Next Segment Nav -->
          <div v-if="hasNextSegment">
            <button @click="goToNextSegment"
              class="w-full py-2.5 px-4 rounded-sm border-2 border-[#003870] text-[#003870] text-sm font-bold hover:bg-[#003870] hover:text-white transition-all flex items-center justify-center gap-2">
              {{ getNextSegmentLabel }}
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>

          <!-- Confirm CTA -->
          <button
            @click="confirmSeats"
            :disabled="!allPassengersHaveSeats"
            :class="[
              'hidden xl:flex w-full py-3.5 rounded-sm text-sm font-bold items-center justify-center gap-2 transition-all',
              allPassengersHaveSeats
                ? 'bg-[#FF579A] hover:bg-[#FF4081] text-white shadow-lg shadow-pink-200 active:scale-[0.98]'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            ]">
            {{ confirmButtonText }}
            <svg v-if="allPassengersHaveSeats" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>

      </div>
    </div>

    <!-- Mobile Footer -->
    <MobileBookingFooter
      :button-text="confirmButtonText"
      :disabled="!allPassengersHaveSeats"
      @next="confirmSeats"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { seatService } from '@/services/booking/seatService';
import { useModalStore } from '@/stores/modal';
import { useNotificationStore } from '@/stores/notification';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import MobileBookingFooter from '@/components/booking/MobileBookingFooter.vue';

const router = useRouter();
const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();
const modalStore = useModalStore();

const activePIndex = ref(0);
const activeFlightSegment = ref('');
const hoveredSeat = ref(null);
const rawSeats = ref([]);
const isLoading = ref(true);
const baseFlightPrice = ref(0);
const aircraftModel = ref('');
const aircraftCapacity = ref(0);
let pollInterval = null;

// Computed properties
const currentFlight = computed(() => {
  const isMulti = bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city';
  if (isMulti) {
    const idx = parseInt(activeFlightSegment.value);
    return bookingStore.multiCitySegments[idx]?.selectedFlight;
  }
  return activeFlightSegment.value === 'return' 
    ? bookingStore.selectedReturn 
    : bookingStore.selectedOutbound;
});

const activeFlightSegmentLabel = computed(() => {
  return activeFlightSegment.value === 'depart' ? 'Depart' : 'Return';
});

const flightSegments = computed(() => {
  const tripType = bookingStore.tripType;
  
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    return bookingStore.multiCitySegments.map((seg, idx) => ({
      key: idx.toString(),
      label: `Flight ${idx + 1}`,
      flight: seg.selectedFlight?.flight_number || 'N/A',
      route: `${seg.origin} → ${seg.destination}`
    }));
  }

  const segments = [
    {
      key: 'depart',
      label: 'Depart Flight',
      flight: bookingStore.selectedOutbound?.flight_number || 'N/A',
      route: bookingStore.selectedOutbound 
        ? `${bookingStore.selectedOutbound.origin} → ${bookingStore.selectedOutbound.destination}`
        : 'N/A'
    }
  ];
  
  if (bookingStore.isRoundTrip && bookingStore.selectedReturn) {
    segments.push({
      key: 'return',
      label: 'Return Flight',
      flight: bookingStore.selectedReturn.flight_number || 'N/A',
      route: `${bookingStore.selectedReturn.origin} → ${bookingStore.selectedReturn.destination}`
    });
  }
  
  return segments;
});

// Get assigned seats for current segment
const assignedSeats = computed(() => {
  return bookingStore.getSeatsBySegment(activeFlightSegment.value);
});

// Get seats count for each segment
// Multi-city progress
const segmentProgress = computed(() => {
  return flightSegments.value.map(seg => {
    const count = Object.keys(bookingStore.getSeatsBySegment(seg.key)).length;
    return {
      label: seg.label,
      key: seg.key,
      count,
      percent: (count / eligiblePassengers.value.length) * 100
    };
  });
});

// Get seats count for each segment (deprecated for multi-city but kept for compat)
const departSeatCount = computed(() => {
  return Object.keys(bookingStore.getSeatsBySegment('depart')).length;
});

const returnSeatCount = computed(() => {
  return Object.keys(bookingStore.getSeatsBySegment('return')).length;
});

// Progress percentages
const departProgress = computed(() => {
  return (departSeatCount.value / eligiblePassengers.value.length) * 100;
});

const returnProgress = computed(() => {
  return (returnSeatCount.value / eligiblePassengers.value.length) * 100;
});

// Check if depart segment has seats
const hasDepartSeats = computed(() => {
  return departSeatCount.value > 0;
});

// Seat selection progress
const allPassengersHaveSeats = computed(() => {
  const adultsAndChildren = bookingStore.passengers.filter(p => p.type !== 'Infant');
  const seats = bookingStore.getSeatsBySegment(activeFlightSegment.value) || {};
  return adultsAndChildren.every(p => seats[p.key]);
});

const allPassengersHaveAllSeats = computed(() => {
  const adultsAndChildren = bookingStore.passengers.filter(p => p.type !== 'Infant');
  const segments = flightSegments.value;
  if (segments.length === 0) return false;

  return segments.every(seg => {
    const seats = bookingStore.getSeatsBySegment(seg.key) || {};
    return adultsAndChildren.every(p => seats[p.key]);
  });
});

const mappedInfants = computed(() => {
  const infants = bookingStore.passengers.filter(p => p.type === 'Infant');
  const mapped = [];
  
  infants.forEach(inf => {
     const assignedAdultKey = bookingStore.infantAdultMapping[inf.key];
     if (assignedAdultKey) {
       const adultSeat = assignedSeats.value[assignedAdultKey];
       const adult = bookingStore.passengers.find(p => p.key === assignedAdultKey);
       if (adultSeat && adult) {
         mapped.push({
           key: inf.key,
           firstName: inf.firstName,
           lastName: inf.lastName,
           adultName: adult.firstName,
           seatCode: adultSeat.seat_code
         });
       }
     }
  });
  return mapped;
});

const getInfantSeat = (infantKey) => {
  const adultKey = bookingStore.infantAdultMapping[infantKey];
  if (adultKey && assignedSeats.value[adultKey]) {
    return assignedSeats.value[adultKey];
  }
  return null;
};

const confirmButtonText = computed(() => {
  if (bookingStore.isRoundTrip) {
    if (activeFlightSegment.value === 'depart') {
      return allPassengersHaveSeats.value 
        ? 'Continue to Return Seats' 
        : `Assign All ${activeFlightSegmentLabel.value} Seats`;
    } else {
      return allPassengersHaveSeats.value 
        ? 'Confirm All Seat Selections' 
        : `Assign All ${activeFlightSegmentLabel.value} Seats`;
    }
  } else {
    return allPassengersHaveSeats.value 
      ? 'Confirm Seat Selection' 
      : 'Assign All Seats';
  }
});

// Seat total for current segment
const segmentSeatTotal = computed(() => {
  const seats = Object.values(assignedSeats.value || {});
  
  return seats.reduce((total, seat) => {
    const seatPrice = parseFloat(seat.seat_price) || 0;
    return total + seatPrice;
  }, 0);
});

// Total seats for both/all segments
const totalSeats = computed(() => {
  let total = 0;
  
  flightSegments.value.forEach(seg => {
    Object.values(bookingStore.getSeatsBySegment(seg.key)).forEach(seat => {
      total += parseFloat(seat.seat_price) || 0;
    });
  });
  
  return total;
});

const hasSelections = computed(() => Object.keys(assignedSeats.value).length > 0);

const hasNextSegment = computed(() => {
  const tripType = bookingStore.tripType;
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    const currentIdx = parseInt(activeFlightSegment.value);
    return currentIdx < bookingStore.multiCitySegments.length - 1 && allPassengersHaveSeats.value;
  }
  return bookingStore.isRoundTrip && activeFlightSegment.value === 'depart' && allPassengersHaveSeats.value;
});

const getNextSegmentLabel = computed(() => {
  const tripType = bookingStore.tripType;
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    const currentIdx = parseInt(activeFlightSegment.value);
    return `Flight ${currentIdx + 2}`;
  }
  return 'Return Flight';
});

const goToNextSegment = () => {
  const tripType = bookingStore.tripType;
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    const currentIdx = parseInt(activeFlightSegment.value);
    switchFlightSegment((currentIdx + 1).toString());
  } else {
    switchToReturnSegment();
  }
};

// Eligible passengers for seats (excluding infants)
const eligiblePassengers = computed(() => {
  return bookingStore.passengers.filter(p => p.type !== 'Infant');
});

// Get active passenger
const activePassenger = computed(() => {
  return eligiblePassengers.value[activePIndex.value] || eligiblePassengers.value[0];
});

// Get seats for a specific segment
const getSeatsForSegment = (segment) => {
  return Object.values(bookingStore.getSeatsBySegment(segment));
};

// Fetch seat data based on active segment
const fetchSeatData = async (silent = false) => {
  const scheduleId = currentFlight.value?.id;
  if (!scheduleId) return;

  try {
    if (!silent) isLoading.value = true;
    
    // We pass the session ID to the backend so it can calculate is_locked_by_me
    const response = await seatService.getSeatsBySchedule(scheduleId, bookingStore.bookingSessionId);
    
    if (response.success) {
      const seatsData = response.seats?.results || response.seats || [];
      rawSeats.value = Array.isArray(seatsData) ? seatsData : [];
      
      baseFlightPrice.value = response.schedule_price || 0;
      // aircraftModel.value = response.aircraft_model || 'Airbus A321';
      aircraftModel.value = response.aircraft_model ;
      aircraftCapacity.value = response.aircraft_capacity || 220;
      
      console.log(`✅ Seat data loaded for ${activeFlightSegmentLabel.value}:`, {
        scheduleId,
        seatsCount: rawSeats.value.length
      });
      
      if (rawSeats.value.length === 0) {
        console.error(`❌ No seats found for ${activeFlightSegmentLabel.value} flight`, scheduleId);
      }
    } else {
      console.error(`❌ Failed to load seat data for ${activeFlightSegmentLabel.value}:`, response.error);
    }
    
  } catch (err) {
    console.error(`❌ Failed to load seat map for ${activeFlightSegmentLabel.value}`, err);
    if (err.response?.status === 400) {
      setTimeout(() => { window.location.reload(); }, 3000);
    }
  } finally {
    isLoading.value = false;
  }
};

// Layout helpers - group seats by class and row for the inline dynamic map
const getRowGroupsByClass = (classId) => {
  const classSeats = rawSeats.value.filter(s => s.seat_class?.id === classId);
  const rowMap = {};
  classSeats.forEach(seat => {
    if (!rowMap[seat.row]) rowMap[seat.row] = [];
    rowMap[seat.row].push(seat);
  });

  return Object.keys(rowMap).sort((a, b) => Number(a) - Number(b)).map(rowNum => {
    const seats = rowMap[rowNum].sort((a, b) => a.column.localeCompare(b.column));
    const mid = Math.ceil(seats.length / 2);
    return {
      row: Number(rowNum),
      globalRow: rowNum,
      leftSeats: seats.slice(0, mid),
      rightSeats: seats.slice(mid),
      isExitRow: seats.some(s => s.is_exit_row)
    };
  });
};

const seatClasses = computed(() => {
  const unique = [];
  rawSeats.value.forEach(s => {
    if (s.seat_class && !unique.find(c => c.id === s.seat_class.id)) unique.push(s.seat_class);
  });
  return unique;
});

const exitRows = computed(() => [...new Set(rawSeats.value.filter(s => s.is_exit_row).map(s => s.row))]);

// Seat tooltip helper for the dynamic map
const getSeatTooltip = (seat) => {
  const parts = [`Seat ${seat.seat_code}`, seat.seat_class?.name || ''];
  
  if (isClassDimmed(seat.seat_class?.name)) {
    parts.push(`Restricted to ${currentFlight.value?.selected_seat_class || 'your selected class'}`);
  }
  
  if (seat.is_exit_row) parts.push('Exit Row');
  if (seat.has_extra_legroom) parts.push('Extra Legroom');
  if (seat.is_wheelchair_accessible) parts.push('Wheelchair Accessible');
  if (seat.has_bassinet) parts.push('Bassinet');
  return parts.join(' • ');
};

// Helpers
const getSeatStatus = (seat) => {
  const currentPKey = bookingStore.passengers[activePIndex.value]?.key;
  
  // 1. Check if locked by ME (from API)
  if (seat.is_locked_by_me) {
    if (assignedSeats.value[currentPKey]?.id === seat.id) return 'selected';
    const isTakenByOtherMe = Object.keys(assignedSeats.value).some(k => 
      k !== currentPKey && assignedSeats.value[k]?.id === seat.id
    );
    if (isTakenByOtherMe) return 'taken-by-other';
    // If locked by me but not in my local store yet (rare race condition), still treat as selected/taken
    return 'selected';
  }

  // 2. Local store fallback (important for immediate UI feedback before poll)
  const localOccupantKey = Object.keys(assignedSeats.value).find(k => assignedSeats.value[k]?.id === seat.id);
  if (localOccupantKey) {
    return localOccupantKey === currentPKey ? 'selected' : 'taken-by-other';
  }

  // 3. Check if occupied/booked/locked by someone else
  if (seat.is_booked) return 'occupied';
  
  // 3.1 Check if locked (soft-lock) by someone else
  if (seat.is_locked && !seat.is_locked_by_me) return 'occupied';
  
  // 4. Check if permanently unavailable
  if (!seat.is_available) return 'occupied';
  
  // 5. If seat class doesn't match selected class
  if (isClassDimmed(seat.seat_class?.name)) return 'occupied';
  
  return 'available';
};

const isClassDimmed = (className) => {
  if (!currentFlight.value?.selected_seat_class) return false;
  return className.toLowerCase() !== currentFlight.value.selected_seat_class.toLowerCase();
};


const getClassColor = (name) => {
  // First try to get the color from the seat class object itself (admin-configured)
  const sc = seatClasses.value.find(c => c.name === name);
  if (sc?.color) return sc.color;
  // Fallback to name-based mapping
  const colors = { 
    'First Class': '#8B4513', 
    'Business': '#4169E1', 
    'Premium Economy': '#228B22', 
    'Economy': '#666' 
  };
  return colors[name] || '#003870';
};

const getPassengerName = (key) => {
  const p = bookingStore.passengers.find(p => p.key === key);
  return p ? `${p.firstName} ${p.lastName.charAt(0)}.` : '';
};

// Seat hover handler
const hoverSeat = (seat) => {
  hoveredSeat.value = seat;
};

// Actions
const assignSeat = async (seat) => {
  const status = getSeatStatus(seat);
  
  // If seat is occupied by someone else, or restricted, don't allow click
  if (status === 'occupied') return;
  
  if (isClassDimmed(seat.seat_class?.name)) {
    notificationStore.warn(`You have selected ${currentFlight.value?.selected_seat_class} for this flight. You can only choose seats in that class.`);
    return;
  }

  const currentP = bookingStore.passengers[activePIndex.value];
  if (!currentP || currentP.type === 'Infant') return; // Do not allow infants to select seats
  
  const occupantKey = Object.keys(assignedSeats.value).find(k => assignedSeats.value[k]?.id === seat.id);
  
  if (occupantKey && occupantKey !== currentP.key) {
    console.warn("Seat already taken by another passenger in this booking");
    return;
  }

  // Toggle Logic - If already selected for THIS passenger, just remove it
  if (assignedSeats.value[currentP.key]?.id === seat.id) {
    const seatId = assignedSeats.value[currentP.key].id;
    bookingStore.removeSeat(currentP.key, activeFlightSegment.value);
    // Non-blocking unlock call
    seatService.unlockSeat(seatId, bookingStore.bookingSessionId);
    console.log(`❌ Removed seat ${seat.seat_code} from ${currentP.firstName} for ${activeFlightSegmentLabel.value}`);
    return;
  }

  // Handle seat change - unlock previous seat if selected
  const existingSeat = assignedSeats.value[currentP.key];
  if (existingSeat && existingSeat.id !== seat.id) {
    console.log(`🔄 Switching seat. Unlocking old seat ${existingSeat.seat_code}...`);
    seatService.unlockSeat(existingSeat.id, bookingStore.bookingSessionId);
  }

  // --- NEW LOCK LOGIC ---
  try {
    isLoading.value = true;
    const lockRes = await seatService.lockSeat(seat.id, bookingStore.bookingSessionId);
    
    if (!lockRes.success) {
      if (lockRes.status === 423 || lockRes.status === 409) {
        notificationStore.error(`Oops! Seat ${seat.seat_code} was just taken by another passenger. Please pick a different one.`);
        // Refresh local seat map to show updated availability
        await fetchSeatData();
      } else {
        notificationStore.error(lockRes.error || "Could not reserve seat. Please try again.");
      }
      return;
    }

    console.log(`🔒 Seat ${seat.seat_code} locked until:`, new Date(lockRes.locked_until).toLocaleTimeString());
    
    // Calculate seat price ONLY (not base flight fare)
    const baseFlightPrice = currentFlight.value?.price || 0;
    const seatTotalPrice = parseFloat(seat.final_price) || 0;
    
    // If Premium fare family is selected for this segment, seat is FREE
    let seatPrice = 0;
    if (bookingStore.fareFamilies[activeFlightSegment.value] === 'premium') {
      seatPrice = 0;
    } else {
      seatPrice = Math.max(0, seatTotalPrice - baseFlightPrice);
    }
    
    const seatPriceData = {
      id: seat.id,
      seat_code: seat.seat_code,
      seat_price: seatPrice,
      seat_total_price: seatTotalPrice,
      seat_class_name: seat.seat_class?.name,
      seat_class: {
        name: seat.seat_class?.name
      },
      locked_until: lockRes.locked_until
    };
    
    bookingStore.assignSeat(currentP.key, seatPriceData, activeFlightSegment.value);
    
    console.group(`💺 SEAT SELECTED & LOCKED: ${seat.seat_code}`);
    console.log(`Passenger: ${currentP.firstName} ${currentP.lastName}`);
    console.log(`Flight: ${activeFlightSegmentLabel.value}`);
    console.log(`Extra Seat Fee Only: ₱${seatPrice.toLocaleString()}`);
    console.groupEnd();

    // Auto-advance logic
    setTimeout(() => {
      const nextIdx = findNextPassengerWithoutSeat();
      if (nextIdx !== -1) activePIndex.value = nextIdx;
    }, 200);

  } catch (err) {
    console.error("Lock error:", err);
    notificationStore.error("An error occurred while reserving your seat.");
  } finally {
    isLoading.value = false;
  }
};

const findNextPassengerWithoutSeat = () => {
  let next = eligiblePassengers.value.findIndex((p, i) => 
    i > activePIndex.value && !assignedSeats.value[p.key]
  );
  
  if (next === -1) {
    next = eligiblePassengers.value.findIndex(p => !assignedSeats.value[p.key]);
  }
  
  return next;
};

const changeSeat = (key) => {
  const idx = bookingStore.passengers.findIndex(p => p.key === key);
  if (idx !== -1) activePIndex.value = idx;
};

const removeSeat = async (key) => {
  const seat = assignedSeats.value[key];
  if (seat && seat.id) {
    console.log(`🔒 Unlocking seat ${seat.seat_code} before removal...`);
    seatService.unlockSeat(seat.id, bookingStore.bookingSessionId);
  }
  bookingStore.removeSeat(key, activeFlightSegment.value);
};

const switchFlightSegment = (segment) => {
  if (segment === activeFlightSegment.value) return;
  
  activeFlightSegment.value = segment;
  activePIndex.value = 0;
  fetchSeatData();
};

const switchToReturnSegment = () => {
  if (bookingStore.isRoundTrip && activeFlightSegment.value === 'depart') {
    switchFlightSegment('return');
  }
};

const copySeatsToReturn = () => {
  if (!bookingStore.isRoundTrip) return;
  
  bookingStore.copySeatsToReturn();
  notificationStore.success('Seats copied from depart to return flight!');
  
  // Switch to return segment to show copied seats
  if (activeFlightSegment.value === 'depart') {
    switchFlightSegment('return');
  }
};

const clearSegmentSeats = async () => {
  const confirmed = await modalStore.confirm({
    title: 'Clear Seats?',
    message: `Clear all seat selections for ${activeFlightSegmentLabel.value} flight?`,
    confirmText: 'Clear All',
    cancelText: 'Cancel'
  })

  if (confirmed) {
    bookingStore.clearSeatsForSegment(activeFlightSegment.value);
    console.log(`🧹 Cleared all seats for ${activeFlightSegmentLabel.value} flight`);
  }
};

const confirmSeats = () => {
  if (!allPassengersHaveSeats.value) {
    notificationStore.warn(`Please assign seats to all passengers for the ${activeFlightSegmentLabel.value} flight.`);
    return;
  }
  
  const tripType = bookingStore.tripType;
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    const currentIdx = parseInt(activeFlightSegment.value);
    if (currentIdx < bookingStore.multiCitySegments.length - 1) {
      // Move to next segment
      switchFlightSegment((currentIdx + 1).toString());
    } else {
      // Done
      router.push({ name: 'Addons' });
    }
  } else if (bookingStore.isRoundTrip) {
    if (activeFlightSegment.value === 'depart') {
      // Move to return seat selection
      switchFlightSegment('return');
    } else {
      // Both segments are complete, go to add-ons
      router.push({ name: 'Addons' });
    }
  } else {
    // One-way trip is complete
    router.push({ name: 'Addons' });
  }
};

// Watch for active segment changes
watch(activeFlightSegment, () => {
  fetchSeatData();
});

const startPolling = () => {
  stopPolling();
  pollInterval = setInterval(async () => {
    if (document.visibilityState === 'visible' && !isLoading.value) {
      await fetchSeatData(true);
    }
  }, 5000);
};

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
};

// Initialize
onMounted(async () => {
  bookingStore.migrateAddonsToNewFormat();
  
  if (bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city') {
    activeFlightSegment.value = '0';
  } else {
    activeFlightSegment.value = 'depart';
  }
  
  await fetchSeatData();
  startPolling();
});

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
/* Core Layout */
.seat-layout-wrapper { 
  max-width: 1400px; 
  margin: 0 auto; 
  padding: 20px; 
  font-family: 'Segoe UI', sans-serif; 
}

.seat-selection-grid { 
  display: grid; 
  grid-template-columns: 250px 1fr 250px; 
  gap: 10px; 
  align-items: start;
}

/* ====== DYNAMIC SEAT MAP ====== */
.dynamic-seat-map {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  padding: 10px 0;
}

.plane-nose {
  font-size: 2rem;
  margin-bottom: 8px;
  color: #003870;
  opacity: 0.4;
  transform: rotate(-45deg);
}

.plane-tail {
  font-size: 1.2rem;
  margin-top: 12px;
  color: #003870;
  opacity: 0.3;
}

.cabin-section {
  width: 100%;
  margin-bottom: 20px;
  transition: opacity 0.3s ease;
}

.cabin-section.dimmed-class {
  opacity: 0.4;
}

.cabin-section.dimmed-class .seat-btn {
  cursor: not-allowed;
  filter: grayscale(0.5);
}


.cabin-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 10px;
  padding: 5px 16px;
  border: 2px solid;
  border-radius: 20px;
  background: white;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

.cabin-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cabin-mult {
  font-weight: 500;
  opacity: 0.7;
  font-size: 0.7rem;
}

.cabin-restricted-badge {
  background: #f0f0f0;
  color: #999;
  font-size: 0.6rem;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border: 1px solid #ddd;
}


.seat-row-wrapper {
  margin-bottom: 4px;
}

.exit-row-banner {
  text-align: center;
  font-size: 0.65rem;
  color: #e53935;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 2px 0 4px;
  text-transform: uppercase;
}

.seat-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.seat-group {
  display: flex;
  gap: 4px;
}

.row-label {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
  color: #bbb;
  background: #f8f8f8;
  border: 1px solid #eee;
  border-radius: 4px;
  flex-shrink: 0;
  user-select: none;
}

/* Seat button base */
.seat-btn {
  width: 34px;
  height: 34px;
  border-radius: 6px 6px 4px 4px;
  border: 2px solid #d0e8ff;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
  cursor: pointer;
  position: relative;
  transition: all 0.15s ease;
  padding: 0;
  gap: 1px;
}

.seat-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  background: color-mix(in srgb, var(--seat-class-color, #003870) 10%, white);
}

.seat-btn .seat-label {
  font-size: 0.65rem;
  font-weight: 800;
  color: #334;
  line-height: 1;
}

/* Status variants */
.seat-btn.available {
  background: #fff;
  cursor: pointer;
}

.seat-btn.available .seat-label { color: #225; }

.seat-btn.selected {
  background: #d11241;
  border-color: #a50d32;
  box-shadow: 0 0 0 2px rgba(209,18,65,0.3);
}

.seat-btn.selected .seat-label { color: #fff; }

.seat-btn.occupied {
  background: #e0e0e0;
  border-color: #bdbdbd;
  cursor: not-allowed;
}

.seat-btn.occupied .seat-label { color: #999; }

.seat-btn.taken-by-other {
  background: #ffe0e0;
  border-color: #ffaaaa;
  cursor: not-allowed;
}

.seat-btn.taken-by-other .seat-label { color: #c66; }

/* Feature tints */
.seat-btn.seat-exit { border-color: #f44 !important; }
.seat-btn.seat-legroom { border-color: #4c8 !important; }

/* Badges inside seat */
.seat-badge {
  font-size: 0.45rem;
  line-height: 1;
  position: absolute;
  top: 1px;
  right: 2px;
}

.seat-btn:disabled {
  opacity: 0.75;
  transform: none !important;
  box-shadow: none !important;
}


.p-seat-card.is-infant {
   opacity: 0.7;
   cursor: not-allowed;
   background: #fff8f0;
}

.p-seat-card.is-infant .p-number {
   background: #ffb347;
}

.infant-item {
   background: #fff8f0;
   border-left: 3px solid #ffb347;
}

.lap-pill {
   background: #ffb347;
   color: white;
}

/* Aircraft Layout Container */
.aircraft-layout-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #eaeaea;
  max-height: 85vh;
  overflow-y: auto;
}

.aircraft-header {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.aircraft-header h3 {
  color: #003870;
  font-size: 1.5rem;
  margin: 0 0 8px 0;
  font-weight: 700;
}

.flight-segment-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 10px;
}

.aircraft-subtitle {
  color: #FF579A;
  font-size: 1rem;
  font-weight: 600;
  background: #FFF0F7;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #FF579A;
}

.flight-number-badge {
  background: #003870;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.aircraft-capacity {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 10px;
}

.capacity-badge,
.selected-badge {
  background: #f0f7ff;
  color: #0066cc;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid #b3d9ff;
}

.selected-badge {
  background: #FFF0F7;
  color: #FF579A;
  border-color: #FFB6D9;
}

/* Flight Segment Tabs */
.flight-segment-tabs.seat-segment {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.segment-tab {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  gap: 10px;
}

.segment-tab.active {
  background: linear-gradient(135deg, #FF579A 0%, #FF4081 100%);
  border-color: #FF579A;
  color: white;
}

.segment-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
}

.segment-info {
  flex: 1;
}

.segment-label {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 3px;
}

.segment-details {
  font-size: 0.85rem;
  opacity: 0.9;
  line-height: 1.3;
}

.seat-count {
  color: #FF579A;
  font-weight: 600;
}

/* Quick Actions */
.quick-actions {
  margin-top: 25px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.quick-actions h4 {
  color: #003870;
  font-size: 1rem;
  margin-bottom: 12px;
}

.quick-action-btn {
  width: 100%;
  padding: 10px;
  background: #003870;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 8px;
  transition: 0.3s;
  text-align: center;
}

.quick-action-btn:hover:not(.disabled) {
  background: #002a54;
  transform: translateY(-1px);
}

.quick-action-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.quick-action-btn.secondary {
  background: #666;
}

.quick-action-btn.secondary:hover {
  background: #555;
}

/* Selection Progress */
.selection-progress {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.progress-label {
  font-weight: 600;
  color: #003870;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.progress-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-text {
  width: 60px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #333;
}

.progress-track {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #FF579A;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-count {
  width: 40px;
  text-align: right;
  font-size: 0.85rem;
  color: #666;
}

/* Next Segment Button */
.btn-next-segment {
  width: 100%;
  padding: 12px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
  transition: 0.3s;
  font-size: 0.95rem;
}

.btn-next-segment:hover {
  background: #218838;
  transform: translateY(-1px);
}

/* Update price summary for segments */
.price-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.price-line.total {
  font-weight: 800;
  color: #333;
  font-size: 1rem;
  padding-top: 10px;
  border-top: 1px dashed #ddd;
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 1200px) {
  .seat-selection-grid {
    grid-template-columns: 250px 1fr 280px;
  }
}

@media (max-width: 992px) {
  .seat-selection-grid {
    grid-template-columns: 1fr;
    gap: 25px;
  }
  
  .seat-main {
    padding: 15px;
  }
  
  .aircraft-layout-container {
    order: 1;
  }
  
  .seat-passenger-list {
    order: 2; 
  }
  
  .map-legend {
    order: 3;
  }
  
  .flight-segment-tabs.seat-segment {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .seat-layout-wrapper {
    padding: 10px;
  }
  
  .aircraft-layout-container {
    padding: 15px;
  }
  
  .aircraft-capacity {
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .flight-segment-info {
    flex-direction: column;
    gap: 8px;
  }
}

/* Keep existing styles for other elements (p-seat-card, legend-card, etc.) */
/* Add these to your existing styles */

.p-seat-card { 
  padding: 15px; 
  border: 1px solid #eee; 
  border-radius: 8px; 
  margin-bottom: 10px; 
  cursor: pointer; 
  background: white; 
  transition: 0.3s;
}

.p-seat-card.active { 
  border-color: #d11241; 
  box-shadow: 0 4px 12px rgba(209, 18, 65, 0.1); 
}

.p-seat-card.has-seat { 
  border-left: 4px solid #28a745; 
}

.p-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.p-number {
  background: #003870;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.p-name {
  font-weight: 600;
  color: #333;
  display: block;
}

.p-type {
  font-size: 0.75rem;
  color: #666;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  margin-top: 3px;
  display: inline-block;
}

.seat-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.p-assigned-seat {
  font-weight: 700;
  color: #003870;
  font-size: 0.95rem;
}

.change-seat-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: 0.2s;
  color: #666;
}

.change-seat-btn:hover {
  background: #e9ecef;
  border-color: #003870;
  color: #003870;
}

.seat-class-info {
  margin-top: 25px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.seat-class-info h4 {
  margin-top: 0;
  color: #003870;
  font-size: 1rem;
  margin-bottom: 12px;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 8px;
  background: white;
  border-radius: 8px;
  border: 1px solid #eee;
}

.class-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  flex-shrink: 0;
}

.class-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #333;
}

.class-price {
  font-size: 0.8rem;
  color: #666;
}

.legend-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
  border: 1px solid #eee;
}

.legend-card h4 {
  color: #003870;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.legend-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #ddd;
  flex-shrink: 0;
}

.box.available { 
  background: #fff; 
  border-color: #91d5ff;
}

.box.selected { 
  background: #d11241; 
  border-color: #a50d32;
}

.box.occupied { 
  background: #e0e0e0; 
  border-color: #bdbdbd;
}

.box.premium { 
  background: #ffd700; 
  border-color: #b8860b;
}

.selected-summary {
  margin-top: 20px;
}

.summary-divider {
  border-top: 1px solid #eee;
  margin: 15px 0;
}

.selected-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f9f9f9;
}

.selected-info {
  flex: 1;
}

.passenger-name {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
  display: block;
}

.seat-badge-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
}

.seat-mini-pill {
  background: #003870;
  color: white;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: bold;
}

.seat-class-label { 
  font-size: 0.65rem; 
  color: #666; 
}

.selected-price { 
  font-size: 0.85rem; 
  font-weight: 600; 
  color: #d11241; 
  display: flex; 
  align-items: center; 
  gap: 5px; 
}

.remove-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 6px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: 0.2s;
  color: #666;
}

.remove-btn:hover {
  background: #e9ecef;
  color: #d11241;
  border-color: #d11241;
}

.price-summary-box {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  border: 1px solid #eee;
}

.summary-note {
  font-size: 0.65rem;
  color: #999;
  margin: 5px 0 0;
  font-style: italic;
  text-align: center;
}

.btn-confirm-seats { 
  width: 100%; 
  padding: 15px; 
  background: #003870; 
  color: white; 
  border: none; 
  border-radius: 8px; 
  font-weight: bold; 
  cursor: pointer; 
  margin-top: 20px;
  transition: 0.3s;
  font-size: 1rem;
}

.btn-confirm-seats:hover:not(.disabled) {
  background: #002a54;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 56, 112, 0.2);
}

.btn-confirm-seats.disabled { 
  background: #ccc; 
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #003870;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.seat-header {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.back-link {
  background: none;
  border: none;
  color: #003870;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 10px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 0;
}

.back-link:hover {
  color: #d11241;
  text-decoration: underline;
}

.seat-header h2 {
  color: #003870;
  font-size: 1.8rem;
  margin: 0 0 8px 0;
}

.flight-info {
  color: #555;
  font-size: 1rem;
  margin: 0;
  font-weight: 500;
  line-height: 1.4;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 500px;
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin: 20px auto;
  max-width: 600px;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.7;
}

.error-state h3 {
  color: #d11241;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

.error-state p {
  color: #666;
  margin-bottom: 20px;
  max-width: 400px;
  line-height: 1.5;
}

.back-btn {
  background: #003870;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
  font-size: 1rem;
  margin-top: 10px;
}

.back-btn:hover {
  background: #002a54;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 56, 112, 0.2);
}

.aircraft-footer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  text-align: center;
}

.cabin-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #555;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  display: inline-block;
}

.legend-color.first { background-color: #8B4513; }
.legend-color.business { background-color: #4169E1; }
.legend-color.economy { background-color: #666; }
</style>
