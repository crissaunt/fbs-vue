<template>
  <div class="seat-selection-view pb-20 lg:pb-0">
    <BookingStatusHeader />
    <div class="container container-layout">
      <main class="seat-main">
        <div class="seat-header">
          <button @click="$router.back()" class="back-link">❮ Back to Add-ons</button>
          <h2>Select Your Seats</h2>
          
          <!-- Flight Segment Tabs -->
          <div v-if="bookingStore.isRoundTrip || bookingStore.tripType.includes('multi')" class="flight-segment-tabs seat-segment">
            <div 
              v-for="segment in flightSegments" 
              :key="segment.key"
              @click="switchFlightSegment(segment.key)"
              :class="['segment-tab', { active: activeFlightSegment === segment.key }]"
            >
              <div class="segment-icon">
                <span v-if="segment.key === 'depart'">✈️</span>
                <span v-else-if="segment.key === 'return'">🔄</span>
                <span v-else>📍</span>
              </div>
              <div class="segment-info">
                <div class="segment-label">{{ segment.label }}</div>
                <div class="segment-details">
                  {{ segment.flight }} • {{ segment.route }}
                  <span v-if="getSeatsForSegment(segment.key).length > 0" class="seat-count">
                    ({{ getSeatsForSegment(segment.key).length }}/{{ eligiblePassengers.length }} selected)
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <p v-else class="flight-info">
            {{ bookingStore.selectedOutbound?.origin }} to {{ bookingStore.selectedOutbound?.destination }}
          </p>
        </div>

        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading seat map for {{ activeFlightSegmentLabel }}...</p>
        </div>

        <div v-else-if="rawSeats.length > 0" class="seat-selection-grid">
          <aside class="seat-passenger-list">
            <h3>Passengers</h3>
            <div 
              v-for="(p, index) in eligiblePassengers" 
              :key="p.key"
              :class="['p-seat-card', { 
                active: activePIndex === index && p.type !== 'Infant',
                'has-seat': assignedSeats[p.key] || (p.type === 'Infant' && getInfantSeat(p.key)),
                'is-infant': p.type === 'Infant'
              }]"
              @click="p.type !== 'Infant' ? activePIndex = index : null"
            >
              <div class="p-info">
                <span class="p-number">{{ index + 1 }}</span>
                <div>
                  <span class="p-name">{{ p.firstName }} {{ p.lastName }}</span>
                  <span class="p-type">{{ p.type }}</span>
                </div>
              </div>
              <div class="seat-action">
                <span v-if="p.type === 'Infant'" class="p-assigned-seat text-xs text-orange-600">
                  {{ getInfantSeat(p.key) ? `Lap: ${getInfantSeat(p.key).seat_code}` : 'Awaiting Adult' }}
                </span>
                <span v-else class="p-assigned-seat">
                  {{ assignedSeats[p.key]?.seat_code || 'Not Selected' }}
                </span>
                <button 
                  v-if="assignedSeats[p.key] && p.type !== 'Infant'"
                  @click.stop="changeSeat(p.key)"
                  class="change-seat-btn"
                  title="Change seat"
                >
                  ↻
                </button>
              </div>
            </div>

            <!-- Quick Actions for Round Trips -->
            <div v-if="bookingStore.isRoundTrip" class="quick-actions">
              <h4>Quick Actions</h4>
              <button 
                @click="copySeatsToReturn"
                class="quick-action-btn"
                :disabled="!hasDepartSeats"
                :class="{ disabled: !hasDepartSeats }"
              >
                📋 Copy Depart Seats to Return
              </button>
              <button 
                @click="clearSegmentSeats"
                class="quick-action-btn secondary"
              >
                🗑️ Clear {{ activeFlightSegmentLabel }} Seats
              </button>
            </div>

            <div class="seat-class-info">
              <h4>Seat Classes</h4>
              <div v-for="sc in seatClasses" :key="sc.id" class="class-item">
                <span class="class-color" :style="{ backgroundColor: getClassColor(sc.name) }"></span>
                <div>
                  <div class="class-name">{{ sc.name }}</div>
                  <div class="class-price">Multiplier: {{ sc.price_multiplier }}x</div>
                </div>
              </div>
            </div>
          </aside>

          <section class="aircraft-layout-container">
            <div class="aircraft-header">
              <h3>{{ aircraftModel }}</h3>
              <div class="flight-segment-info">
                <span class="aircraft-subtitle">{{ activeFlightSegmentLabel }} Flight</span>
                <span class="flight-number-badge">{{ currentFlight?.flight_number || 'N/A' }}</span>
              </div>
              <div class="aircraft-capacity">
                <span class="capacity-badge">Capacity: {{ aircraftCapacity }} seats</span>
                <span class="selected-badge">Selected: {{ Object.keys(assignedSeats).length }}/{{ eligiblePassengers.length }}</span>
              </div>
            </div>
            
            <!-- Dynamic seat map rendered from API data -->
            <div class="dynamic-seat-map">
              <!-- Aircraft body shape -->
              <div class="plane-nose">✈</div>

              <!-- Group by seat class -->
              <div v-for="seatClass in seatClasses" :key="seatClass.id" 
                   :class="['cabin-section', { 'dimmed-class': isClassDimmed(seatClass.name) }]">
                <!-- Cabin class header -->
                <div class="cabin-header" :style="{ borderColor: getClassColor(seatClass.name), color: getClassColor(seatClass.name) }">
                  <span class="cabin-dot" :style="{ background: getClassColor(seatClass.name) }"></span>
                  <span class="cabin-label">{{ seatClass.name }}</span>
                  <span class="cabin-mult">×{{ seatClass.price_multiplier }}</span>
                  <span v-if="isClassDimmed(seatClass.name)" class="cabin-restricted-badge">Restricted</span>
                </div>

                <!-- Rows for this class -->
                <div v-for="rowGroup in getRowGroupsByClass(seatClass.id)" :key="rowGroup.row" class="seat-row-wrapper">
                  <!-- Exit row banner -->
                  <div v-if="rowGroup.isExitRow" class="exit-row-banner">🚪 Emergency Exit</div>

                  <div class="seat-row">
                    <!-- Left side seats (first half of columns) -->
                    <div class="seat-group">
                      <button
                        v-for="seat in rowGroup.leftSeats"
                        :key="seat.id"
                        @click="assignSeat(seat)"
                        :class="['seat-btn', getSeatStatus(seat), { 'seat-exit': seat.is_exit_row, 'seat-legroom': seat.has_extra_legroom }]"
                        :style="seat.is_available && getSeatStatus(seat) === 'available' ? { borderColor: getClassColor(seatClass.name), '--seat-class-color': getClassColor(seatClass.name) } : {}"
                        :title="getSeatTooltip(seat)"
                        :disabled="!seat.is_available || getSeatStatus(seat) === 'taken-by-other' || isClassDimmed(seat.seat_class?.name)"
                      >
                        <span class="seat-label">{{ seat.column }}</span>
                        <span v-if="seat.is_exit_row" class="seat-badge exit-badge">🚪</span>
                        <span v-else-if="seat.has_extra_legroom" class="seat-badge leg-badge">↕</span>
                        <span v-else-if="seat.is_wheelchair_accessible" class="seat-badge wheel-badge">♿</span>
                      </button>
                    </div>

                    <!-- Aisle / Row number -->
                    <div class="row-label">{{ rowGroup.globalRow }}</div>

                    <!-- Right side seats (second half of columns) -->
                    <div class="seat-group">
                      <button
                        v-for="seat in rowGroup.rightSeats"
                        :key="seat.id"
                        @click="assignSeat(seat)"
                        :class="['seat-btn', getSeatStatus(seat), { 'seat-exit': seat.is_exit_row, 'seat-legroom': seat.has_extra_legroom }]"
                        :style="seat.is_available && getSeatStatus(seat) === 'available' ? { borderColor: getClassColor(seatClass.name), '--seat-class-color': getClassColor(seatClass.name) } : {}"
                        :title="getSeatTooltip(seat)"
                        :disabled="!seat.is_available || getSeatStatus(seat) === 'taken-by-other' || isClassDimmed(seat.seat_class?.name)"
                      >
                        <span class="seat-label">{{ seat.column }}</span>
                        <span v-if="seat.is_exit_row" class="seat-badge exit-badge">🚪</span>
                        <span v-else-if="seat.has_extra_legroom" class="seat-badge leg-badge">↕</span>
                        <span v-else-if="seat.is_wheelchair_accessible" class="seat-badge wheel-badge">♿</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="plane-tail">▼</div>
            </div>
            
            <div class="aircraft-footer">
              <div class="cabin-legend">
                <span v-for="sc in seatClasses" :key="sc.id" class="legend-item">
                  <span class="legend-color" :style="{ background: getClassColor(sc.name) }"></span>
                  <span>{{ sc.name }}</span>
                </span>
              </div>
            </div>
          </section>

          <aside class="map-legend">
            <div class="legend-card">
              <h4>Legend</h4>
              <div class="legend-grid">
                <div class="legend-item"><span class="box available"></span><span>Available</span></div>
                <div class="legend-item"><span class="box selected"></span><span>Selected</span></div>
                <div class="legend-item"><span class="box occupied"></span><span>Occupied</span></div>
                <div class="legend-item"><span class="box premium"></span><span>Extra Space</span></div>
              </div>

              <div v-if="hasSelections" class="selected-summary">
                <div class="summary-divider"></div>
                <h4>Your Selection ({{ activeFlightSegmentLabel }})</h4>
                
                <div v-for="(seat, pKey) in assignedSeats" :key="pKey" class="selected-item">
                  <div class="selected-info">
                    <span class="passenger-name">{{ getPassengerName(pKey) }}</span>
                    <div class="seat-badge-row">
                      <span class="seat-mini-pill">{{ seat.seat_code }}</span>
                      <span class="seat-class-label">{{ seat.seat_class?.name }}</span>
                    </div>
                  </div>
                  <div class="selected-price">
                    ₱{{ (seat.seat_price || 0).toLocaleString() }}
                    <button @click="removeSeat(pKey)" class="remove-btn">×</button>
                  </div>
                </div>
                
                <!-- Display mapped infants -->
                <div v-for="infant in mappedInfants" :key="infant.key" class="selected-item infant-item">
                  <div class="selected-info">
                    <span class="passenger-name">{{ infant.firstName }} {{ infant.lastName }} (Infant)</span>
                    <div class="seat-badge-row">
                      <span class="seat-mini-pill lap-pill">Lap of {{ infant.adultName }}</span>
                      <span class="seat-class-label">{{ infant.seatCode }}</span>
                    </div>
                  </div>
                  <div class="selected-price">
                    Included
                  </div>
                </div>

                <div class="price-summary-box">
                  <div class="price-line">
                    <span>Seat Fees ({{ activeFlightSegmentLabel }}):</span>
                    <span>₱{{ segmentSeatTotal.toLocaleString() }}</span>
                  </div>
                  
                  <!-- Show total for both segments if round trip -->
                  <div v-if="bookingStore.isRoundTrip" class="price-line total">
                    <span>Total Seat Fees (Both Flights):</span>
                    <span>₱{{ totalSeats.toLocaleString() }}</span>
                  </div>
                  
                  <p class="summary-note">*Base flight fare not included in this total</p>
                </div>
              </div>

              <div class="selection-progress" v-if="bookingStore.isRoundTrip || bookingStore.tripType.includes('multi')">
                <div class="progress-label">Selection Progress</div>
                <div class="progress-bars">
                  <div v-for="seg in segmentProgress" :key="seg.key" class="progress-bar">
                    <div class="progress-text">{{ seg.label }}</div>
                    <div class="progress-track">
                      <div class="progress-fill" :style="{ width: seg.percent + '%' }"></div>
                    </div>
                  <div class="progress-count">{{ seg.count }}/{{ bookingStore.passengers.length }}</div>
                  </div>
                </div>
              </div>

              <div v-if="hasNextSegment" class="next-segment-nav">
                <button class="next-segment-btn" @click="goToNextSegment">
                  Next Flight: {{ getNextSegmentLabel }} ❯
                </button>
              </div>

              <button class="confirm-btn flex-1 hidden lg:block" :disabled="!allPassengersHaveSeats" @click="confirmSeats">
                {{ confirmButtonText }}
              </button>
            </div>
          </aside>
        </div>
      </main>

      <MobileBookingFooter 
        :button-text="confirmButtonText" 
        :disabled="!allPassengersHaveSeats"
        @next="confirmSeats" 
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
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
const fetchSeatData = async () => {
  const scheduleId = currentFlight.value?.id;
  if (!scheduleId) { 
    console.error('No schedule ID for', activeFlightSegment.value);
    return;
  }

  try {
    isLoading.value = true;
    
    console.log(`🚀 Fetching seat data for ${activeFlightSegmentLabel.value} flight:`, scheduleId);
    
    const response = await seatService.getSeatsBySchedule(scheduleId);
    
    if (response.success) {
      // Handle paginated response (response.seats.results) or flat array (response.seats)
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
  if (assignedSeats.value[currentPKey]?.id === seat.id) return 'selected';
  if (!seat.is_available) return 'occupied';
  const isTaken = Object.values(assignedSeats.value).some(s => s.id === seat.id);
  if (isTaken) return 'taken-by-other';
  
  // If seat class doesn't match selected class, mark it as disabled/unavailable for selection
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
const assignSeat = (seat) => {
  if (!seat.is_available) return;

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

  // Toggle Logic
  if (assignedSeats.value[currentP.key]?.id === seat.id) {
    bookingStore.removeSeat(currentP.key, activeFlightSegment.value);
    console.log(`❌ Removed seat ${seat.seat_code} from ${currentP.firstName} for ${activeFlightSegmentLabel.value}`);
  } else {
    // Calculate seat price ONLY (not base flight fare)
    const baseFlightPrice = currentFlight.value?.price || 0;
    const seatTotalPrice = parseFloat(seat.final_price) || 0;
    const seatPrice = Math.max(0, seatTotalPrice - baseFlightPrice);
    
    const seatPriceData = {
      id: seat.id,
      seat_code: seat.seat_code,
      seat_price: seatPrice,
      seat_total_price: seatTotalPrice,
      seat_class_name: seat.seat_class?.name,
      seat_class: {
        name: seat.seat_class?.name
      }
    };
    
    bookingStore.assignSeat(currentP.key, seatPriceData, activeFlightSegment.value);
    
    console.group(`💺 SEAT SELECTED: ${seat.seat_code}`);
    console.log(`Passenger: ${currentP.firstName} ${currentP.lastName}`);
    console.log(`Flight: ${activeFlightSegmentLabel.value}`);
    console.log(`Class: ${seat.seat_class?.name}`);
    console.log(`Base Flight Price: ₱${baseFlightPrice.toLocaleString()}`);
    console.log(`Total Seat Price (inc. flight): ₱${seatTotalPrice.toLocaleString()}`);
    console.log(`Extra Seat Fee Only: ₱${seatPrice.toLocaleString()}`);
    console.groupEnd();
  }

  // Auto-advance logic
  setTimeout(() => {
    const nextIdx = findNextPassengerWithoutSeat();
    if (nextIdx !== -1) activePIndex.value = nextIdx;
  }, 200);
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

const removeSeat = (key) => {
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
      router.back();
    }
  } else if (bookingStore.isRoundTrip) {
    if (activeFlightSegment.value === 'depart') {
      // Move to return seat selection
      switchFlightSegment('return');
    } else {
      // Both segments are complete, go back to add-ons
      router.back();
    }
  } else {
    // One-way trip is complete
    router.back();
  }
};

// Watch for active segment changes
watch(activeFlightSegment, () => {
  fetchSeatData();
});

// Initialize
onMounted(async () => {
  // First, migrate store to new format
  bookingStore.migrateAddonsToNewFormat();
  
  // Initialize active segment
  if (bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city') {
    activeFlightSegment.value = '0';
  } else {
    activeFlightSegment.value = 'depart';
  }
  
  // Fetch seat data for initial segment
  await fetchSeatData();
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
  border-radius: 10px; 
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
  border-radius: 10px;
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
  border-radius: 4px;
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
  border-radius: 6px;
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
  border-radius: 5px;
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
  border-radius: 4px;
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
  border-radius: 4px;
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
