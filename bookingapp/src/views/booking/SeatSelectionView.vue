<template>
  <div class="pal-bg">
    <div class="container seat-layout-wrapper">
      <main class="seat-main">
        <div class="seat-header">
          <button @click="$router.back()" class="back-link">❮ Back to Add-ons</button>
          <h2>Select Your Seats</h2>
          <p class="flight-info" v-if="bookingStore.selectedOutbound">
            {{ bookingStore.selectedOutbound.origin }} to {{ bookingStore.selectedOutbound.destination }}
          </p>
        </div>

        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading seat map...</p>
        </div>

        <div v-else class="seat-selection-grid">
          <aside class="seat-passenger-list">
            <h3>Passengers</h3>
            <div 
              v-for="(p, index) in bookingStore.passengers" 
              :key="p.key"
              :class="['p-seat-card', { 
                active: activePIndex === index,
                'has-seat': assignedSeats[p.key]
              }]"
              @click="activePIndex = index"
            >
              <div class="p-info">
                <span class="p-number">{{ index + 1 }}</span>
                <div>
                  <span class="p-name">{{ p.firstName }} {{ p.lastName }}</span>
                  <span class="p-type">{{ p.type }}</span>
                </div>
              </div>
              <div class="seat-action">
                <span class="p-assigned-seat">
                  {{ assignedSeats[p.key]?.seat_code || 'Not Selected' }}
                </span>
                <button 
                  v-if="assignedSeats[p.key]"
                  @click.stop="changeSeat(p.key)"
                  class="change-seat-btn"
                  title="Change seat"
                >
                  ↻
                </button>
              </div>
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

          <section class="map-area">
            <div class="plane-nose"></div>
            
            <div class="aisle-container">
              <div class="column-labels">
                <div class="label-left"><span>A</span><span>B</span><span>C</span></div>
                <div class="aisle-spacer"></div>
                <div class="label-right"><span>D</span><span>E</span><span>F</span></div>
              </div>

              <div 
                v-for="row in seatMapRows" 
                :key="row.number" 
                class="seat-row"
                :class="{ 'exit-row-indicator': isExitRow(row.number) }"
              >
                <div v-if="isExitRow(row.number)" class="exit-row">EXIT</div>
                <div class="row-num">{{ row.number }}</div>
                
                <div class="seat-group">
                  <div 
                    v-for="seat in getSeatsByGroup(row.seats, ['A','B','C'])" 
                    :key="seat.id" 
                    :class="['seat-unit', seatClassToStyle(seat.seat_class?.name), getSeatStatus(seat), getSeatFeatures(seat)]"
                    :aria-label="`Seat ${seat.seat_code} ${getSeatStatus(seat)}`"
                    @click="assignSeat(seat)"
                    @mouseenter="hoveredSeat = seat"
                    @mouseleave="hoveredSeat = null"
                  >
                    <span class="seat-letter">{{ seat.column }}</span>
                    <span v-if="seat.price_adjustment > 0" class="premium-badge">+</span>
                    
                    <div v-if="hoveredSeat?.id === seat.id" class="seat-tooltip">
                      <div class="tooltip-title">{{ seat.seat_code }} ({{ seat.seat_class?.name }})</div>
                      <div v-if="seat.has_extra_legroom" class="tooltip-feature">Extra Legroom</div>
                      <div class="tooltip-price" v-if="seat.price_adjustment > 0">+₱{{ seat.price_adjustment }}</div>
                    </div>
                  </div>
                </div>
                
                <div class="aisle-spacer"><div class="aisle-line"></div></div>
                
                <div class="seat-group">
                  <div 
                    v-for="seat in getSeatsByGroup(row.seats, ['D','E','F'])" 
                    :key="seat.id" 
                    :class="['seat-unit', seatClassToStyle(seat.seat_class?.name), getSeatStatus(seat), getSeatFeatures(seat)]"
                    @click="assignSeat(seat)"
                    @mouseenter="hoveredSeat = seat"
                    @mouseleave="hoveredSeat = null"
                  >
                    <span class="seat-letter">{{ seat.column }}</span>
                    <span v-if="seat.price_adjustment > 0" class="premium-badge">+</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="plane-tail"></div>
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
                <h4>Your Selection</h4>
                
                <div v-for="(seat, pKey) in assignedSeats" :key="pKey" class="selected-item">
                  <div class="selected-info">
                    <span class="passenger-name">{{ getPassengerName(pKey) }}</span>
                    <div class="seat-badge-row">
                      <span class="seat-mini-pill">{{ seat.seat_code }}</span>
                      <span class="seat-class-label">{{ seat.seat_class?.name }}</span>
                    </div>
                  </div>
                  <div class="selected-price">
                    ₱{{ seat.final_price.toLocaleString() }}
                    <button @click="removeSeat(pKey)" class="remove-btn">×</button>
                  </div>
                </div>

                <div class="price-summary-box">
                  <div class="price-line total">
                    <span>Total Seat Fees:</span>
                    <span>₱{{ seatTotal.toLocaleString() }}</span>
                  </div>
                  <p class="summary-note">*Base flight fare not included in this total</p>
                </div>
              </div>

              <button 
                class="btn-confirm-seats" 
                @click="confirmSeats"
                :disabled="!allPassengersHaveSeats"
                :class="{ disabled: !allPassengersHaveSeats }"
              >
                {{ allPassengersHaveSeats ? 'Confirm Selection' : 'Assign All Seats' }}
              </button>
            </div>
          </aside>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { seatService } from '@/services/booking/seatService';

const router = useRouter();
const bookingStore = useBookingStore();

const activePIndex = ref(0);
const hoveredSeat = ref(null);
const rawSeats = ref([]);
const isLoading = ref(true);

onMounted(async () => {
  const scheduleId = bookingStore.selectedOutbound?.id;
  if (!scheduleId) { router.push('/'); return; }

  try {
    rawSeats.value = await seatService.getSeatsBySchedule(scheduleId);
  } catch (err) {
    console.error("Failed to load seat map", err);
  } finally {
    isLoading.value = false;
  }
});

// Layout Logic
const seatMapRows = computed(() => {
  const rows = {};
  rawSeats.value.forEach(s => {
    if (!rows[s.row]) rows[s.row] = { number: s.row, seats: [] };
    rows[s.row].seats.push(s);
  });
  return Object.values(rows).sort((a, b) => a.number - b.number);
});

const assignedSeats = computed(() => bookingStore.addons.seats || {});
const seatClasses = computed(() => {
  const unique = [];
  rawSeats.value.forEach(s => {
    if (s.seat_class && !unique.find(c => c.id === s.seat_class.id)) unique.push(s.seat_class);
  });
  return unique;
});

const exitRows = computed(() => [...new Set(rawSeats.value.filter(s => s.is_exit_row).map(s => s.row))]);
const hasSelections = computed(() => Object.keys(assignedSeats.value).length > 0);
const allPassengersHaveSeats = computed(() => 
  bookingStore.passengers.every(p => assignedSeats.value[p.key])
);

// CRITICAL FIX: Calculate seat total correctly
const seatTotal = computed(() => {
  const selections = Object.values(bookingStore.addons.seats || {});
  const flightPrice = bookingStore.selectedOutbound?.price || 0;
  
  return selections.reduce((total, seat) => {
    const seatPrice = parseFloat(seat.final_price) || 0;
    // Calculate extra fee (price above base fare)
    const extraFee = Math.max(0, seatPrice - flightPrice);
    return total + extraFee;
  }, 0);
});

// Helpers
const getSeatsByGroup = (seats, letters) => seats.filter(s => letters.includes(s.column)).sort((a,b) => a.column.localeCompare(b.column));
const isExitRow = (num) => exitRows.value.includes(num);

const getSeatStatus = (seat) => {
  const currentPKey = bookingStore.passengers[activePIndex.value]?.key;
  if (assignedSeats.value[currentPKey]?.id === seat.id) return 'selected';
  if (!seat.is_available) return 'occupied';
  const isTaken = Object.values(assignedSeats.value).some(s => s.id === seat.id);
  return isTaken ? 'taken-by-other' : 'available';
};

const seatClassToStyle = (name) => {
  const map = { 
    'First Class': 'first-class-seat', 
    'Business': 'business-seat', 
    'Premium Economy': 'premium-economy-seat', 
    'Economy': 'economy-seat' 
  };
  return map[name] || '';
};

const getSeatFeatures = (seat) => {
  return [
    seat.is_window && 'window-seat',
    seat.is_aisle && 'aisle-seat',
    seat.has_extra_legroom && 'extra-legroom'
  ].filter(Boolean).join(' ');
};

const getClassColor = (name) => {
  const colors = { 
    'First Class': '#8B4513', 
    'Business': '#4169E1', 
    'Premium Economy': '#228B22', 
    'Economy': '#666' 
  };
  return colors[name] || '#666';
};

const getPassengerName = (key) => {
  const p = bookingStore.passengers.find(p => p.key === key);
  return p ? `${p.firstName} ${p.lastName.charAt(0)}.` : '';
};

// Actions
const assignSeat = (seat) => {
  if (!seat.is_available) return;
  const currentP = bookingStore.passengers[activePIndex.value];

  // Prevent stealing seats within the group
  const occupantKey = Object.keys(assignedSeats.value).find(k => assignedSeats.value[k]?.id === seat.id);
  if (occupantKey && occupantKey !== currentP.key) {
      console.warn("Seat already taken by another passenger in this booking");
      return;
  }

  // Toggle Logic
  if (assignedSeats.value[currentP.key]?.id === seat.id) {
    bookingStore.removeSeat(currentP.key);
    console.log(`❌ Removed seat ${seat.seat_code} from ${currentP.firstName}`);
  } else {
    // IMPORTANT: Store the seat data exactly as it comes from the API
    // The final_price already includes the base fare + seat class multiplier + adjustments
    const seatData = {
      id: seat.id,
      seat_number: seat.seat_number || seat.seat_code,
      seat_code: seat.seat_code,
      final_price: parseFloat(seat.final_price) || 0,
      seat_class_name: seat.seat_class?.name,
      seat_class: {
        name: seat.seat_class?.name
      }
    };
    
    bookingStore.assignSeat(currentP.key, seatData);
    
    // --- DEBUG LOG START ---
    console.group(`💺 SEAT SELECTED: ${seat.seat_code}`);
    console.log(`Passenger: ${currentP.firstName} ${currentP.lastName}`);
    console.log(`Class: ${seat.seat_class?.name}`);
    console.log(`Total Seat Price: ₱${parseFloat(seat.final_price).toLocaleString()}`);
    
    // Calculate breakdown
    const flightPrice = bookingStore.selectedOutbound?.price || 0;
    const seatPrice = parseFloat(seat.final_price) || 0;
    const extraFee = Math.max(0, seatPrice - flightPrice);
    
    console.log(`Flight Base Price: ₱${flightPrice.toLocaleString()}`);
    console.log(`Extra Seat Fee: ₱${extraFee.toLocaleString()}`);
    console.log("Updated Seat Add-ons in Store:", JSON.parse(JSON.stringify(bookingStore.addons.seats)));
    console.groupEnd();
    // --- DEBUG LOG END ---
  }

  // Auto-advance logic
  setTimeout(() => {
    const nextIdx = findNextPassengerWithoutSeat();
    if (nextIdx !== -1) activePIndex.value = nextIdx;
  }, 200);
};

const findNextPassengerWithoutSeat = () => {
  // Look forward
  let next = bookingStore.passengers.findIndex((p, i) => i > activePIndex.value && !assignedSeats.value[p.key]);
  // Look from start (wrap-around)
  if (next === -1) next = bookingStore.passengers.findIndex(p => !assignedSeats.value[p.key]);
  return next;
};

const changeSeat = (key) => {
  const idx = bookingStore.passengers.findIndex(p => p.key === key);
  if (idx !== -1) activePIndex.value = idx;
};

const removeSeat = (key) => bookingStore.removeSeat(key);
const confirmSeats = () => {
  if (allPassengersHaveSeats.value) router.back();
};
</script>

<style scoped>
/* Core Layout */
.seat-layout-wrapper { max-width: 1200px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', sans-serif; }
.seat-selection-grid { display: grid; grid-template-columns: 280px 1fr 280px; gap: 20px; align-items: start; }

/* Airplane Visuals */
.map-area { 
  background: #fff; border: 2px solid #ccc; border-radius: 100px 100px 30px 30px; 
  padding: 80px 40px; position: relative; max-height: 85vh; overflow-y: auto;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.05);
}
.plane-nose { 
  position: absolute; top: 0; left: 50%; transform: translateX(-50%); 
  width: 120px; height: 40px; background: #e0e0e0; border-radius: 60px 60px 0 0; 
}

/* Row & Seat Styling */
.seat-row { display: flex; align-items: center; justify-content: center; margin-bottom: 10px; position: relative; }
.row-num { width: 30px; text-align: center; font-size: 0.75rem; color: #999; font-weight: bold; }
.seat-group { display: flex; gap: 8px; }
.aisle-spacer { width: 40px; display: flex; justify-content: center; }
.aisle-line { width: 2px; height: 40px; background: #f0f0f0; }

.seat-unit { 
  width: 36px; height: 40px; border-radius: 6px; border: 1px solid #ccc;
  display: flex; align-items: center; justify-content: center; font-size: 0.7rem;
  cursor: pointer; transition: 0.2s; position: relative; background: #f9f9f9;
}
.seat-unit.available:hover { transform: scale(1.1); border-color: #003870; z-index: 2; }
.seat-unit.selected { background: #d11241 !important; color: white; border-color: #a00d31; }
.seat-unit.occupied { background: #e0e0e0; color: #bbb; cursor: not-allowed; border-color: #ddd; }
.seat-unit.taken-by-other { background: #003870; color: white; opacity: 0.5; cursor: not-allowed; }

/* Indicators */
.premium-badge { 
  position: absolute; top: -5px; right: -5px; background: #ffd700; 
  font-size: 0.6rem; width: 14px; height: 14px; border-radius: 50%; 
  display: flex; align-items: center; justify-content: center; border: 1px solid #b8860b;
}
.exit-row { 
  position: absolute; width: 100%; text-align: center; top: -15px;
  font-size: 0.6rem; font-weight: bold; color: #d11241; letter-spacing: 2px;
}

/* Sidebar Styling */
.p-seat-card { 
  padding: 15px; border: 1px solid #eee; border-radius: 10px; margin-bottom: 10px; 
  cursor: pointer; background: white; transition: 0.3s;
}
.p-seat-card.active { border-color: #d11241; box-shadow: 0 4px 12px rgba(209, 18, 65, 0.1); }
.p-seat-card.has-seat { border-left: 4px solid #28a745; }

.btn-confirm-seats { 
  width: 100%; padding: 15px; background: #003870; color: white; 
  border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 20px;
}
.btn-confirm-seats.disabled { background: #ccc; cursor: not-allowed; }

/* Tooltip */
.seat-tooltip {
  position: absolute; bottom: 120%; left: 50%; transform: translateX(-50%);
  background: #333; color: white; padding: 10px; border-radius: 5px;
  z-index: 100; min-width: 100px; text-align: center; pointer-events: none;
}
.selected-summary { margin-top: 20px; }
.summary-divider { border-top: 1px solid #eee; margin: 15px 0; }

.selected-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f9f9f9;
}

.seat-mini-pill {
  background: #003870;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: bold;
}

.seat-class-label { font-size: 0.65rem; color: #666; margin-left: 5px; }

.selected-price { 
  font-size: 0.85rem; 
  font-weight: 600; 
  color: #d11241; 
  display: flex; 
  align-items: center; 
  gap: 5px; 
}

.price-summary-box {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  border: 1px solid #eee;
}

.price-line.total {
  display: flex;
  justify-content: space-between;
  font-weight: 800;
  color: #333;
}

.summary-note {
  font-size: 0.65rem;
  color: #999;
  margin: 5px 0 0;
  font-style: italic;
}
</style>