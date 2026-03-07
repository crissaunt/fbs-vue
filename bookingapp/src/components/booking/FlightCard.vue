<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 hover:border-pink-300 hover:shadow-md transition-all duration-200">
    <div class="px-6 py-3">
      <!-- Flight Header -->
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-4 pb-4 border-b border-gray-100">
        <div class="flex items-center space-x-4 flex ">
          <div>
            <div class="font-bold text-sm text-pink-500">{{ flight.airline_name }}</div>
            <div class="text-[11px] text-green-500">{{ flight.flight_number }}</div>
          </div>
          <div v-if="flight.is_domestic !== undefined" 
            :class="['px-3 py-1 rounded-full text-[9px] font-medium',
                     flight.is_domestic ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700']">
            {{ flight.is_domestic ? 'Domestic' : 'International' }}
          </div>
          <div v-if="(flight.total_stops || 0) === 0" 
            class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-[9px] font-medium">
            Non-stop
          </div>
          <div v-else 
            class="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-[9px] font-medium">
            {{ flight.total_stops }} {{ flight.total_stops === 1 ? 'Stop' : 'Stops' }}
          </div>
        </div>
        
        <div class="text-center">
          <div class="text-xs text-gray-700">{{ formatDate(flight.departure_time) }}</div>
          <div class=" font-bold text-gray-500">{{ formatDay(flight.departure_time) }}</div>
        </div>
        
        <div class="text-right flex flex-col items-end">
          <div class="text-xl font-bold" :class="flight.ml_predicted ? 'text-pink-600' : 'text-pink-500'">
            ₱{{ Number(flight.price).toLocaleString() }}
          </div>
          <button 
            v-if="flight.ml_predicted" 
            @click="$emit('view-pricing', flight)"
            class="text-[10px] text-pink-400 hover:text-pink-600 font-medium flex items-center gap-1 mt-1 uppercase tracking-wider transition-colors"
          >
            Price Insights
            <svg class="w-3 h-3" :class="{'rotate-180': showPricingDetails && selectedPriceId === flight.price_id}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Price Insights Breakdown Overlay -->
      <div v-if="showPricingDetails && selectedPriceId === flight.price_id" 
           class="mb-4 p-4 bg-pink-50/50 rounded-lg border border-pink-100 animate-in fade-in slide-in-from-top-2 duration-300">
        <div class="flex justify-between items-center mb-2">
          <h4 class="text-xs font-bold text-pink-600 uppercase tracking-widest">Price Breakdown</h4>
          <span class="text-[10px] text-gray-400">ML ID: {{ flight.price_id }}</span>
        </div>
        
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="space-y-1">
            <div class="text-[10px] text-gray-500 uppercase">Base Prediction</div>
            <div class="text-sm font-bold text-gray-700">₱{{ Number(flight.ml_base_price).toLocaleString() }}</div>
          </div>
          
          <div v-for="(factor, key) in flight.ml_factors" :key="key" class="space-y-1">
            <div class="text-[10px] text-gray-500 uppercase">{{ getFactorLabel(key) }}</div>
            <div class="text-sm font-bold" :class="factor > 1 ? 'text-orange-500' : (factor < 1 ? 'text-green-600' : 'text-gray-600')">
              {{ factor > 1 ? '+' : '' }}{{ ((factor - 1) * 100).toFixed(0) }}%
              <span class="text-[10px] font-normal text-gray-400 ml-1">(x{{ factor.toFixed(2) }})</span>
            </div>
          </div>
        </div>
        
        <div class="mt-3 pt-3 border-t border-pink-100 flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-pink-400 animate-pulse"></div>
          <p class="text-[10px] text-pink-500 italic">This price includes real-time surge protection and local holiday adjustments.</p>
        </div>
      </div>
      
      <!-- Schedule Info - NEW VISUAL TIMELINE -->
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-4 mt-2 px-2">
        <!-- Departure -->
        <div class="text-right w-24 shrink-0">
          <div class="text-2xl font-black text-gray-900 leading-none">{{ formatTime(flight.departure_time) }}</div>
          <div class="text-sm font-bold text-gray-500 mt-1">{{ flight.origin_airport_code }}</div>
        </div>
        
        <!-- Visual Timeline -->
        <div class="flex-1 flex flex-col items-center justify-center relative min-w-[150px]">
          <div class="text-[10px] font-bold text-gray-400 mb-2 uppercase tracking-widest">
            {{ flight.flight_duration || formatDuration(flight.duration_minutes) }}
          </div>
          
          <!-- The Line -->
          <div class="w-full relative flex items-center justify-center h-2">
            <!-- connecting line -->
            <div class="absolute left-0 right-0 h-[2px] bg-gray-300"></div>
            
            <!-- Origin Dot -->
            <div class="absolute left-0 w-2 h-2 rounded-full border-2 border-pink-500 bg-white z-10"></div>
            
            <!-- Layover Dots (if any) -->
            <div v-if="(flight.total_stops || 0) > 0" class="w-3 h-3 rounded-full bg-orange-200 border-2 border-orange-500 z-10 shadow-sm relative group cursor-help">
               <!-- Tooltip for stop -->
               <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-800 text-white text-[10px] py-1 px-2 rounded whitespace-nowrap z-50">
                 {{ flight.total_stops }} Stop(s)
               </div>
            </div>
            <div v-else class="text-pink-300 z-10 bg-white px-1">
              <svg class="w-4 h-4 transform rotate-90" fill="currentColor" viewBox="0 0 20 20">
                 <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path>
              </svg>
            </div>
            
            <!-- Destination Dot -->
            <div class="absolute right-0 w-2 h-2 rounded-full border-2 border-pink-500 bg-pink-500 z-10"></div>
          </div>
        </div>
        
        <!-- Arrival -->
        <div class="text-left w-24 shrink-0">
          <div class="text-2xl font-black text-gray-900 leading-none">{{ formatTime(flight.arrival_time) }}</div>
          <div class="text-sm font-bold text-gray-500 mt-1">{{ flight.destination_airport_code }}</div>
        </div>
      </div>
      
      <!-- Footer: Amenities & Actions -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-gray-100 bg-gray-50/50 -mx-6 px-6 -mb-3 pb-3 rounded-b-lg">
        
        <!-- Amenity Icons Preview -->
        <div class="flex items-center gap-4 text-gray-500">
          <div class="flex items-center gap-1.5" title="Personal Item Included">
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
             <span class="text-[10px] font-medium hidden sm:inline">Included</span>
          </div>
          <div class="flex items-center gap-1.5" title="USB Power">
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          </div>
          <div class="flex items-center gap-1.5" title="Standard Legroom">
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path></svg>
             <span class="text-[10px] font-medium hidden sm:inline">29" Pitch</span>
          </div>
          
          <div class="flex items-center gap-1.5 ml-2">
             <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
             <span :class="['text-[10px] font-bold uppercase tracking-widest', (flight.available_seats || 0) < 10 ? 'text-orange-500 animate-pulse' : 'text-gray-500']">
                {{ flight.available_seats ?? 0 }} Seats Available
             </span>
          </div>
        </div>
        
        <div class="flex space-x-3 items-center">
          <!-- Selected Indicator Text -->
          <div v-if="isSelected" class="text-[11px] text-pink-600 font-bold uppercase tracking-wider mr-2">
            ✓ {{ selectedClassName }}
          </div>
          
          <template v-if="isSelected">
            <button class="px-5 py-2 bg-green-500 text-white rounded font-bold shadow-sm shadow-green-200 text-sm">
              ✓ {{ selectionLabel }}
            </button>
            <button @click="$emit('select-flight', flight)" 
              class="px-4 py-2 border-2 border-gray-200 text-gray-600 rounded hover:bg-gray-100 transition-colors font-bold text-sm">
              {{ isExpanded ? 'Cancel' : 'Change' }}
            </button>
          </template>
          <template v-else>
            <!-- Expanding indicator instead of direct select if not handling inline yet -->
            <button @click="$emit('select-flight', flight)" 
              class="px-6 py-2.5 bg-pink-500 cursor-pointer text-white text-sm rounded-md shadow-md shadow-pink-200 hover:bg-pink-600 hover:-translate-y-0.5 transition-all font-bold whitespace-nowrap flex items-center gap-2">
              {{ isExpanded ? 'Close' : selectButtonText }}
              <svg class="w-4 h-4 transition-transform duration-200" :class="isExpanded ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </button>
          </template>
        </div>
      </div>
      
      <!-- INLINE EXPANDED FARE FAMILIES -->
      <div v-show="isExpanded" class="mt-4 pt-4 border-t border-gray-100 animate-in slide-in-from-top-4 fade-in duration-300">
        
        <!-- Tabbed Headers -->
        <div class="flex flex-row overflow-x-auto mb-6 bg-gray-50/50 -mx-6 px-6" v-if="availableTravelClasses.length > 0">
          <button 
            v-for="tClass in availableTravelClasses" 
            :key="tClass"
            @click="selectedTravelClass = tClass"
            class="flex-1 py-3 px-4 text-left border-t-4 transition-colors min-w-[140px] border-r border-r-white"
            :class="[
              selectedTravelClass === tClass 
                ? (getTabColor(tClass) === 'blue' ? 'border-blue-500 bg-blue-100/50' : 
                   getTabColor(tClass) === 'rose' ? 'border-rose-400 bg-rose-100/50' : 
                   'border-yellow-500 bg-yellow-100/50')
                : (getTabColor(tClass) === 'blue' ? 'border-blue-200 bg-blue-50/40 text-gray-500 hover:bg-blue-100/40' : 
                   getTabColor(tClass) === 'rose' ? 'border-rose-200 bg-rose-50/40 text-gray-500 hover:bg-rose-100/40' : 
                   'border-yellow-200 bg-yellow-50/40 text-gray-500 hover:bg-yellow-100/40')
            ]"
          >
            <div class="flex justify-between items-end">
              <div>
                <div class="font-medium" :class="selectedTravelClass === tClass ? 'text-blue-900 text-sm' : 'text-gray-600 text-sm'">{{ tClass }}</div>
                <div class="text-xs mt-1" :class="selectedTravelClass === tClass ? 'text-blue-800' : 'text-gray-500'">From PHP</div>
                <div class="font-black mt-0.5" :class="selectedTravelClass === tClass ? 'text-blue-900 text-base' : 'text-gray-700 text-base'">
                  {{ Number(getLowestPrice(tClass)).toLocaleString() }}
                </div>
              </div>
              <svg class="w-4 h-4 mb-1" :class="selectedTravelClass === tClass ? 'text-blue-900' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 px-2">
          <!-- Render Seat Classes passed from parent -->
          <div v-for="seatClass in groupedClasses[selectedTravelClass]" :key="seatClass.name" 
               class="border-2 rounded-lg p-5 flex flex-col transition-all cursor-pointer relative overflow-hidden"
               :class="[
                 seatClass.fare_family === 'flex' ? 'border-yellow-500 hover:border-yellow-400 hover:-translate-y-1 shadow-sm' : 
                   (hoveredClass === seatClass.name ? 'border-pink-500 shadow-md transform -translate-y-1' : 'border-gray-200 hover:border-pink-300')
               ]"
               @mouseenter="hoveredClass = seatClass.name"
               @mouseleave="hoveredClass = null"
               @click="$emit('select-seat-class', { flight, seatClass })">
               
            <!-- Recommended Banner for Flex -->
            <div v-if="seatClass.fare_family === 'flex'" class="absolute -top-1 -right-1 bg-yellow-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-lg">
              RECOMMENDED
            </div>
            <!-- Decorative Banner for Premium (Fallback) -->
            <div v-else-if="seatClass.fare_family === 'premium'" class="absolute -top-1 -right-1 bg-pink-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-lg">
              BEST VALUE
            </div>
               
            <div class="flex justify-between items-start mb-2">
              <div>
                <h3 class="font-black text-gray-900 text-lg">{{ seatClass.name }}</h3>
                <p class="text-xs text-gray-500 mt-1 line-clamp-2 h-8">{{ seatClass.description }}</p>
              </div>
              <div class="w-10 h-10 rounded-full bg-pink-50 flex items-center justify-center shrink-0 text-pink-500">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="seatClass.icon"></path>
                </svg>
              </div>
            </div>
            
            <div class="text-2xl font-black text-pink-600 my-4">
              ₱{{ Number(seatClass.price).toLocaleString() }}
            </div>
            
            <ul class="space-y-3 mb-6 flex-1">
              <li v-for="(feature, idx) in seatClass.features" :key="idx" class="flex items-start text-sm text-gray-700">
                <svg class="w-4 h-4 text-green-500 mr-2 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="leading-tight">{{ feature }}</span>
              </li>
            </ul>
            
            <button class="w-full py-3 rounded-md font-bold text-sm transition-colors"
                    :class="hoveredClass === seatClass.name ? 'bg-pink-500 text-white shadow-md shadow-pink-200' : 'bg-pink-50 text-pink-600'">
              Select {{ seatClass.name }}
            </button>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { format } from 'date-fns';

const props = defineProps({
  flight: Object,
  isRoundTrip: Boolean,
  isMultiCity: Boolean,
  selectionPhase: String,
  selectedOutbound: Object,
  selectedReturn: Object,
  selectedSegmentFlight: Object,
  selectButtonText: String,
  mlPricingEnabled: Boolean,
  showPricingDetails: Boolean,
  selectedPriceId: String,
  parsedSeatClasses: Array // New Array passed down from parent view
});

const emit = defineEmits(['select-flight', 'view-pricing', 'select-seat-class', 'expand']);

const isExpanded = computed(() => {
  return props.parsedSeatClasses && props.parsedSeatClasses.length > 0;
});
const hoveredClass = ref(null);

// NEW: Group seat classes by travel class and logic for tabs
const groupedClasses = computed(() => {
  if (!props.parsedSeatClasses) return {};
  return props.parsedSeatClasses.reduce((acc, sc) => {
    let tClass = sc.travel_class;
    // Fallback if travel_class is missing, parse from name
    if (!tClass) {
      if (sc.name.toLowerCase().includes('economy')) tClass = 'Economy';
      else if (sc.name.toLowerCase().includes('business')) tClass = 'Business';
      else if (sc.name.toLowerCase().includes('first')) tClass = 'First Class';
      else tClass = 'Economy';
    }
    
    // Capitalize properly
    tClass = tClass.charAt(0).toUpperCase() + tClass.slice(1);
    
    if (!acc[tClass]) acc[tClass] = [];
    acc[tClass].push(sc);
    return acc;
  }, {});
});

const availableTravelClasses = computed(() => Object.keys(groupedClasses.value));
const selectedTravelClass = ref('');

// Switch to first tab safely
watch(() => isExpanded.value, (newVal) => {
  if (newVal && availableTravelClasses.value.length > 0 && !selectedTravelClass.value) {
    selectedTravelClass.value = availableTravelClasses.value[0];
  }
});

const getTabColor = (tClass) => {
  const c = tClass.toLowerCase();
  if (c.includes('premium')) return 'rose';
  if (c.includes('business') || c.includes('first')) return 'yellow';
  return 'blue';
};

const getLowestPrice = (tClass) => {
  const classes = groupedClasses.value[tClass] || [];
  if (classes.length === 0) return 0;
  return Math.min(...classes.map(c => Number(c.price)));
};

const isFlightMatch = (flightA, flightB) => {
  if (!flightA || !flightB) return false;
  // Use ID if available, otherwise fallback to flight_number + departure_time combination
  if (flightA.id && flightB.id) {
    return flightA.id === flightB.id;
  }
  return flightA.flight_number === flightB.flight_number && 
         flightA.departure_time === flightB.departure_time;
};

const isSelected = computed(() => {
  if (props.isMultiCity) {
    return isFlightMatch(props.selectedSegmentFlight, props.flight);
  }
  if (props.isRoundTrip) {
    if (props.selectionPhase === 'outbound') {
      return isFlightMatch(props.selectedOutbound, props.flight);
    } else {
      return isFlightMatch(props.selectedReturn, props.flight);
    }
  }
  return isFlightMatch(props.selectedOutbound, props.flight);
});

const selectedClassName = computed(() => {
  let selected = props.selectedOutbound;
  if (props.isMultiCity) selected = props.selectedSegmentFlight;
  else if (props.isRoundTrip && props.selectionPhase === 'return') selected = props.selectedReturn;
  
  return selected?.selected_seat_class || selected?.seat_class || 'Not selected';
});

const selectionLabel = computed(() => {
  if (props.isMultiCity) return 'Flight Selected';
  if (!props.isRoundTrip) return 'Flight Selected';
  return props.selectionPhase === 'outbound' ? 'Outbound Selected' : 'Return Selected';
});

// Helpers
const formatTime = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit', hour12: true });
};

const formatDate = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' });
};

const formatDay = (dateTimeString) => {
  if (!dateTimeString) return '';
  return format(new Date(dateTimeString), 'EEEE');
};

const formatDuration = (minutes) => {
  if (!minutes) return '';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const formatSeatClasses = (seatClasses) => {
  if (!seatClasses || !Array.isArray(seatClasses)) return '';
  return seatClasses.map(sc => {
    if (typeof sc === 'string') return sc;
    if (sc && typeof sc === 'object') return sc.name || sc.class_name || sc.value || 'Unknown';
    return 'Unknown';
  }).join(', ');
};
const getFactorLabel = (key) => {
  const labels = {
    'user_factor': 'Loyalty',
    'session_factor': 'Session',
    'demand_factor': 'Urgency',
    'time_factor': 'Peak Time',
    'inventory_factor': 'Occupancy',
    'randomization': 'Disturbance',
    'festival_factor': 'Fiesta'
  };
  return labels[key] || key.replace('_', ' ');
};
</script>
