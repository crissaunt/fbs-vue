<template>
  <div class="pal-bg">
    <div class="container seat-layout-wrapper">
      <main class="seat-main">
        <div class="seat-header">
          <button @click="$router.back()" class="back-link">❮ Back to Add-ons</button>
          <h2>Select Your Seats</h2>
          <p class="flight-info" v-if="bookingStore.selectedOutbound">
            {{ bookingStore.selectedOutbound.origin }} to {{ bookingStore.selectedOutbound.destination }}
            <span v-if="bookingStore.selectedReturn" style="font-weight: normal; color: #666;">
              (Round Trip - Selecting for Outbound Flight)
            </span>
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

          <section class="airbus-layout-container">
            <div class="aircraft-header">
              <h3>Airbus A321</h3>
              <span class="aircraft-subtitle">Cabin Layout</span>
            </div>
            
            <!-- Import and use the Airbus layout component -->
            <AirbusA321Layout
              :seats="rawSeats"
              :selectedSeats="assignedSeats"
              :activePassenger="activePassenger"
              :onSeatSelect="assignSeat"
              :onSeatHover="hoverSeat"
            />
            
            <div class="aircraft-footer">
              <div class="cabin-legend">
                <span class="legend-item">
                  <span class="legend-color first"></span>
                  <span>First Class</span>
                </span>
                <span class="legend-item">
                  <span class="legend-color business"></span>
                  <span>Business</span>
                </span>
                <span class="legend-item">
                  <span class="legend-color economy"></span>
                  <span>Economy</span>
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
                    <!-- Show ONLY seat price (not total price) -->
                    ₱{{ (seat.seat_price || 0).toLocaleString() }}
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
import AirbusA321Layout from '@/components/seatmaps/AirbusA321Layout.vue';

const router = useRouter();
const bookingStore = useBookingStore();

const activePIndex = ref(0);
const hoveredSeat = ref(null);
const rawSeats = ref([]);
const isLoading = ref(true);
const baseFlightPrice = ref(0);

// Fetch seat data
onMounted(async () => {
  const scheduleId = bookingStore.selectedOutbound?.id;
  if (!scheduleId) { 
    router.push('/'); 
    return; 
  }

  try {
    isLoading.value = true;
    
    console.log('🚀 Starting seat data fetch for schedule:', scheduleId);
    
    // Get seat data using the service
    const response = await seatService.getSeatsBySchedule(scheduleId);
    
    if (response.success) {
      rawSeats.value = response.seats || [];
      baseFlightPrice.value = response.schedule_price || 0;
      
      console.log('✅ Seat data loaded successfully:', {
        scheduleId: scheduleId,
        schedulePrice: baseFlightPrice.value,
        seatsCount: rawSeats.value.length,
        availableSeats: response.available_seats,
        sampleSeat: rawSeats.value[0] ? {
          seat_code: rawSeats.value[0].seat_code,
          final_price: rawSeats.value[0].final_price,
          seat_class: rawSeats.value[0].seat_class?.name,
          features: rawSeats.value[0].features || []
        } : null
      });
      
      // If no seats, show error
      if (rawSeats.value.length === 0) {
        console.error('❌ No seats found for schedule', scheduleId);
        alert('No seats available for this flight. Please try another flight.');
        router.back();
      }
    } else {
      console.error('❌ Failed to load seat data:', response.error);
      alert('Failed to load seat map. Please try again.');
      router.back();
    }
    
  } catch (err) {
    console.error("❌ Failed to load seat map", err);
    alert('Error loading seat selection. Please try again.');
    router.back();
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

// CRITICAL FIX: Calculate seat total correctly - ONLY seat prices
const seatTotal = computed(() => {
  const selections = Object.values(bookingStore.addons.seats || {});
  
  return selections.reduce((total, seat) => {
    // Use seat_price which is already calculated as (final_price - base_flight_price)
    const seatPrice = parseFloat(seat.seat_price) || 0;
    return total + seatPrice;
  }, 0);
});

// Get active passenger
const activePassenger = computed(() => {
  return bookingStore.passengers[activePIndex.value] || bookingStore.passengers[0];
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

// Seat hover handler for Airbus component
const hoverSeat = (seat) => {
  hoveredSeat.value = seat;
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
    // CRITICAL: Calculate seat price ONLY (not base flight fare)
    const baseFlightPrice = bookingStore.selectedOutbound?.price || 0;
    const seatTotalPrice = parseFloat(seat.final_price) || 0;
    
    // Seat price is the DIFFERENCE between final price and base fare
    const seatPrice = Math.max(0, seatTotalPrice - baseFlightPrice);
    
    // Store only seat price data
    const seatPriceData = {
      id: seat.id,
      seat_code: seat.seat_code,
      seat_price: seatPrice,  // Store only the seat price
      seat_total_price: seatTotalPrice,  // Optional: store for reference
      seat_class_name: seat.seat_class?.name,
      seat_class: {
        name: seat.seat_class?.name
      }
    };
    
    bookingStore.assignSeat(currentP.key, seatPriceData);
    
    // Debug logging
    console.group(`💺 SEAT SELECTED: ${seat.seat_code}`);
    console.log(`Passenger: ${currentP.firstName} ${currentP.lastName}`);
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
.seat-layout-wrapper { max-width: 1400px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', sans-serif; }
.seat-selection-grid { 
  display: grid; 
  grid-template-columns: 280px 1fr 320px; 
  gap: 20px; 
  align-items: start;
}

/* Airbus Layout Container */
.airbus-layout-container {
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
  margin: 0;
  font-weight: 700;
}

.aircraft-subtitle {
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
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

/* Sidebar Styling */
.p-seat-card { 
  padding: 15px; border: 1px solid #eee; border-radius: 10px; margin-bottom: 10px; 
  cursor: pointer; background: white; transition: 0.3s;
}
.p-seat-card.active { border-color: #d11241; box-shadow: 0 4px 12px rgba(209, 18, 65, 0.1); }
.p-seat-card.has-seat { border-left: 4px solid #28a745; }

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
}

.change-seat-btn:hover {
  background: #e9ecef;
  border-color: #003870;
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
}

.class-price {
  font-size: 0.8rem;
  color: #666;
}

/* Legend Card */
.legend-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
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

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #555;
}

.box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #ddd;
  flex-shrink: 0;
}

.box.available { background: #fff; }
.box.selected { background: #d11241; }
.box.occupied { background: #e0e0e0; }
.box.premium { 
  background: #ffd700; 
  border-color: #b8860b;
}

/* Selected Summary */
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

.price-line.total {
  display: flex;
  justify-content: space-between;
  font-weight: 800;
  color: #333;
  font-size: 1.1rem;
}

.summary-note {
  font-size: 0.65rem;
  color: #999;
  margin: 5px 0 0;
  font-style: italic;
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
  
  .airbus-layout-container {
    order: 1;
  }
  
  .seat-passenger-list {
    order: 2;
  }
  
  .map-legend {
    order: 3;
  }
}
</style>