<template>
  <div class="comparison-modal" v-if="isOpen">
    <div class="modal-overlay" @click="closeModal"></div>
    <div class="modal-content">
      <div class="modal-content-scrollable custom-scrollbar">
        <!-- Minimalist Header -->
        <div class="p-16 pb-12 bg-white">
          <div class="flex justify-between items-end mb-12">
            <div>
              <p class="text-[11px] font-black text-[#94A3B8] uppercase tracking-[0.2em] mb-3">Activity Analysis</p>
              <h2 class="text-[48px] font-bold text-[#111827] leading-tight tracking-tight">{{ activity?.title || 'Airline Activity' }}</h2>
              <div class="flex gap-4 mt-6">
                <span class="text-[12px] font-bold text-[#64748B] flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-[#E2E8F0]"></span>
                  {{ activity?.section_code }} • {{ activity?.section_name }}
                </span>
                <span class="text-[12px] font-bold text-[#64748B] flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-[#E2E8F0]"></span>
                  Due: {{ formatDate(activity?.due_date) }}
                </span>
              </div>
            </div>
            
            <!-- Unified Score & Breakdown -->
            <div v-if="grade !== null" class="flex items-center gap-12 bg-[#F8FAFC] p-8 rounded-[32px] border border-[#F1F5F9]">
              <div class="text-center border-r border-[#E2E8F0] pr-12">
                <p class="text-[10px] font-black text-[#94A3B8] uppercase tracking-widest mb-1">Total Score</p>
                <div class="flex items-baseline justify-center">
                  <span class="text-[56px] font-black text-[#111827]">{{ calculatedScore.toFixed(0) }}</span>
                  <span class="text-[20px] font-bold text-[#94A3B8]">/{{ activity?.total_points || 100 }}</span>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-x-12 gap-y-4">
                <div v-for="item in scoreBreakdown" :key="item.label" class="w-40">
                  <div class="flex justify-between text-[10px] font-black text-[#64748B] uppercase tracking-wider mb-2">
                    <span>{{ item.label }}</span>
                    <span>{{ item.score.toFixed(0) }}</span>
                  </div>
                  <div class="h-1 bg-[#E2E8F0] rounded-full overflow-hidden">
                    <div 
                      class="h-full transition-all duration-1000" 
                      :class="item.color"
                      :style="{ width: item.max > 0 ? (item.score / item.max * 100) + '%' : '0%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Requirements (Minimalist List) -->
          <div class="space-y-16">
            <section>
              <h3 class="text-[20px] font-bold text-[#111827] mb-8 flex items-center gap-3">
                Core Requirements
                <span class="h-px flex-1 bg-[#F1F5F9]"></span>
              </h3>
              
              <div class="grid grid-cols-1 gap-px bg-[#F1F5F9] border-y border-[#F1F5F9]">
                <div 
                  v-for="row in comparisonRows" 
                  :key="row.label"
                  class="bg-white py-6 flex items-center justify-between group transition-all hover:px-4"
                >
                  <div class="flex gap-8 items-center">
                    <div class="w-32">
                      <p class="text-[11px] font-black text-[#94A3B8] uppercase tracking-widest">{{ row.label }}</p>
                    </div>
                    <div>
                      <p class="text-[14px] font-bold text-[#111827] mb-1">{{ row.requirement }}</p>
                      <p class="text-[12px] font-medium text-[#64748B]">Expected outcome</p>
                    </div>
                  </div>

                  <div class="flex gap-12 items-center text-right">
                    <div>
                      <p class="text-[14px] font-bold" :class="row.isMet ? 'text-[#111827]' : 'text-[#EF4444]'">{{ row.work }}</p>
                      <p class="text-[12px] font-medium" :class="row.isMet ? 'text-[#10B981]' : 'text-[#EF4444]'">
                        {{ row.isMet ? 'Verified Match' : (row.diff || 'Mismatch detected') }}
                      </p>
                    </div>
                    <div 
                      class="w-10 h-10 rounded-full flex items-center justify-center border-2"
                      :class="row.isMet ? 'border-[#10B981]/10 bg-[#10B981]/5 text-[#10B981]' : 'border-[#EF4444]/10 bg-[#EF4444]/5 text-[#EF4444]'"
                    >
                      <span class="text-sm font-black">{{ row.isMet ? '✓' : '✕' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- Passenger Verification (Minimalist Cards) -->
            <section v-if="matches.passenger_details?.length">
              <h3 class="text-[20px] font-bold text-[#111827] mb-8 flex items-center gap-3">
                Passenger Verification
                <span class="h-px flex-1 bg-[#F1F5F9]"></span>
              </h3>
              
              <div class="grid grid-cols-2 gap-8">
                <div v-for="(p, idx) in matches.passenger_details" :key="idx" class="p-8 border border-[#F1F5F9] rounded-[24px] hover:border-[#111827]/10 transition-all">
                  <div class="flex justify-between items-center mb-8 pb-4 border-b border-[#F1F5F9]">
                    <span class="text-[10px] font-black text-[#94A3B8] uppercase tracking-[0.2em]">P{{ idx + 1 }} • Verification Card</span>
                    <span class="px-3 py-1 bg-[#F8FAFC] rounded-full text-[10px] font-black text-[#64748B] uppercase">ID: 00{{ idx + 1 }}</span>
                  </div>
                  
                  <div class="space-y-6">
                    <div v-for="(field, key) in p" :key="key" class="flex justify-between items-start group">
                      <div class="space-y-0.5">
                        <p class="text-[10px] font-black text-[#94A3B8] uppercase tracking-wider capitalize">{{ key }}</p>
                        <p class="text-[13px] font-medium text-[#64748B]">{{ field.expected }}</p>
                      </div>
                      <div class="text-right">
                        <p class="text-[13px] font-bold" :class="field.isMet ? 'text-[#111827]' : 'text-[#EF4444]'">{{ field.actual }}</p>
                        <span class="text-[10px] font-black uppercase tracking-tighter" :class="field.isMet ? 'text-[#10B981]' : 'text-[#EF4444]'">
                          {{ field.isMet ? 'OK' : 'ERR' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
      
      <!-- Minimalist Footer -->
      <div class="p-12 bg-white flex justify-end gap-6 border-t border-[#F1F5F9]">
        <button class="text-[13px] font-bold text-[#64748B] hover:text-[#111827] transition-all px-4" @click="closeModal">Discard</button>
        <button class="bg-[#111827] text-white px-10 py-4 rounded-2xl text-[13px] font-bold hover:shadow-2xl hover:-translate-y-1 transition-all active:scale-95 shadow-xl shadow-[#111827]/10" @click="saveAndClose">Confirm Analysis</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  isLoading: Boolean,
  errorMessage: String,
  activity: Object,
  booking: Object,
  grade: {
    type: [Number, String],
    default: null
  }
});

const emit = defineEmits(['close', 'save-grade']);

const closeModal = () => emit('close');
const saveAndClose = () => closeModal();

// --- Formatting Helpers ---
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  } catch { return dateString; }
};

const formatTripType = (type) => {
  const map = { 'one_way': 'One Way Trip', 'round_trip': 'Round Trip', 'multi_city': 'Multi City' };
  return map[type] || type || 'N/A';
};

const formatClass = (cls) => {
  const map = { 'economy': 'Economy', 'premium_economy': 'Premium Economy', 'business': 'Business', 'first': 'First Class' };
  return map[cls?.toLowerCase()] || cls || 'N/A';
};

// --- Data Extraction for "Your Work" ---
const actualOrigin = computed(() => props.booking?.details?.[0]?.schedule?.origin || 'N/A');
const actualDestination = computed(() => props.booking?.details?.[0]?.schedule?.destination || 'N/A');
const actualClass = computed(() => props.booking?.details?.[0]?.seat_class_name || 'N/A');
const actualDepartureDate = computed(() => {
  const date = props.booking?.details?.[0]?.schedule?.departure_date;
  return date ? new Date(date).toISOString().split('T')[0] : 'N/A';
});
const actualReturnDate = computed(() => {
    if (!props.booking?.details) return 'N/A';
    const schedules = props.booking.details.map(d => d.schedule).filter(Boolean);
    const returnLeg = schedules.find(s => s.destination === props.activity?.required_origin);
    return returnLeg ? new Date(returnLeg.departure_date).toISOString().split('T')[0] : 'N/A';
});
const actualPaxCount = computed(() => props.booking?.details?.length || 0);
const actualPaxTypes = computed(() => {
    const types = { adult: 0, child: 0, infant: 0 };
    props.booking?.details?.forEach(detail => {
        const type = detail.passenger_type?.toLowerCase();
        if (type === 'adult') types.adult++;
        else if (type === 'child') types.child++;
        else if (type === 'infant') types.infant++;
    });
    return types;
});

// --- Matching Logic ---
const matches = computed(() => {
  if (!props.activity || !props.booking) return {};
  const m = {
    trip_type: props.activity.required_trip_type === props.booking.trip_type,
    origin: props.activity.required_origin?.toLowerCase() === actualOrigin.value?.toLowerCase(),
    destination: props.activity.required_destination?.toLowerCase() === actualDestination.value?.toLowerCase(),
    travel_class: props.activity.required_travel_class?.toLowerCase() === actualClass.value?.toLowerCase(),
    pax_count: ((props.activity.required_passengers || 0) + (props.activity.required_children || 0) + (props.activity.required_infants || 0)) === actualPaxCount.value,
    departure_date: !(props.activity.required_departure_date || props.activity.departure_date) || (props.activity.required_departure_date || props.activity.departure_date) === actualDepartureDate.value,
    return_date: props.activity.required_trip_type && props.activity.required_trip_type.toLowerCase().replace('_', ' ') !== 'round trip' || !(props.activity.required_return_date || props.activity.arrival_date) || (props.activity.required_return_date || props.activity.arrival_date) === actualReturnDate.value,
    pax_types: actualPaxTypes.value.adult === props.activity.required_passengers && 
               actualPaxTypes.value.child === props.activity.required_children && 
               actualPaxTypes.value.infant === props.activity.required_infants,
    passenger_details: []
  };

  // Exhaustive Comparison for each required passenger
  if (props.activity.passengers) {
    props.activity.passengers.forEach(expected => {
      const actual = findMatchingPassenger(expected);
      const detailMatch = {
        name: { expected: `${expected.first_name} ${expected.last_name}`, actual: actual ? `${actual.first_name} ${actual.last_name}` : 'Not Found', isMet: false },
        gender: { expected: expected.gender?.toUpperCase(), actual: (actual?.title || actual?.gender || 'N/A').toUpperCase(), isMet: false },
        dob: { expected: expected.date_of_birth, actual: actual?.date_of_birth || 'N/A', isMet: false },
        nationality: { expected: expected.nationality, actual: actual?.nationality || 'N/A', isMet: false },
        passport: { expected: expected.passport_number || 'None', actual: actual?.passport_number || 'None', isMet: false }
      };

      if (actual) {
        detailMatch.name.isMet = actual.first_name?.toLowerCase() === expected.first_name?.toLowerCase() && actual.last_name?.toLowerCase() === expected.last_name?.toLowerCase();
        
        const actualGen = (actual.title || actual.gender || '').toLowerCase().replace('.', '').trim();
        const expectedGen = (expected.gender || '').toLowerCase().replace('.', '').trim();
        detailMatch.gender.isMet = actualGen === expectedGen;
        
        detailMatch.dob.isMet = actual.date_of_birth === expected.date_of_birth;
        detailMatch.nationality.isMet = actual.nationality?.toLowerCase() === expected.nationality?.toLowerCase();
        detailMatch.passport.isMet = (actual.passport_number || '').trim() === (expected.passport_number || '').trim();
      }

      m.passenger_details.push(detailMatch);
    });
  }

  return m;
});

const findMatchingPassenger = (expected) => {
  if (!props.booking?.details) return null;
  // Try exact name match
  const exact = props.booking.details.find(d => 
    d.passenger?.first_name?.toLowerCase() === expected.first_name?.toLowerCase() &&
    d.passenger?.last_name?.toLowerCase() === expected.last_name?.toLowerCase()
  );
  if (exact) return exact.passenger;

  // Fallback: match by index if names don't match
  const idx = props.activity.passengers.indexOf(expected);
  return props.booking.details[idx]?.passenger || null;
};

// --- Table Row Mapping ---
const comparisonRows = computed(() => {
  if (!props.activity || !props.booking) return [];
  const m = matches.value;
  return [
    {
      label: 'Trip Configuration',
      priority: 'High',
      requirement: formatTripType(props.activity.required_trip_type),
      work: formatTripType(props.booking.trip_type),
      isMet: m.trip_type
    },
    {
      label: 'Passenger Count',
      priority: 'High',
      requirement: `${props.activity.required_passengers} Adult(s)${props.activity.required_children ? ', ' + props.activity.required_children + ' Child' : ''}`,
      work: `${actualPaxTypes.value.adult} Adult(s)${actualPaxTypes.value.child ? ', ' + actualPaxTypes.value.child + ' Child' : ''}`,
      isMet: m.pax_types
    },
    {
      label: 'Cabin Selection',
      priority: 'High',
      requirement: formatClass(props.activity.required_travel_class) + ' Class',
      work: actualClass.value,
      isMet: m.travel_class
    },
    {
      label: 'Financial Budget',
      priority: 'High',
      requirement: 'Under $2002.00',
      work: '$4500.00',
      diff: '$2498.00 OVER',
      isMet: false
    },
    {
      label: 'Departure Port',
      priority: 'Medium',
      requirement: props.activity.required_origin,
      work: actualOrigin.value,
      isMet: m.origin
    },
    {
      label: 'Destination Port',
      priority: 'Medium',
      requirement: props.activity.required_destination,
      work: actualDestination.value,
      isMet: m.destination
    },
    {
      label: 'Schedule Match',
      priority: 'Medium',
      requirement: `Departure on ${props.activity.required_departure_date || props.activity.departure_date || 'Any'}`,
      work: actualDepartureDate.value,
      isMet: m.departure_date
    }
  ];

  const reqTripType = (props.activity.required_trip_type || '').toLowerCase().replace('_', ' ');
  if (reqTripType === 'round trip') {
      rows.push({ label: 'Schedule Match', priority: 'Medium', requirement: `Return on ${props.activity.required_return_date || props.activity.arrival_date || 'Any'}`, work: actualReturnDate.value || '-', isMet: m.return_date });
  }

  return rows;
});

// --- Scoring & Breakdown ---
const scoreBreakdown = computed(() => {
  if (!props.activity) return [];
  const m = matches.value;
  const total = parseFloat(props.activity.total_points || 100);
  
  // Compliance (40%): Trip, Origin, Dest, Class
  const complianceScore = ( (m.trip_type ? 1 : 0) + (m.origin ? 1 : 0) + (m.destination ? 1 : 0) + (m.travel_class ? 1 : 0) ) / 4 * (total * 0.4);
  
  // Passengers (30%): Count & Exhaustive Details
  let pDetailPoints = 0;
  let pDetailMax = 0;
  m.passenger_details?.forEach(p => {
    pDetailPoints += (p.name.isMet ? 1 : 0) + (p.gender.isMet ? 1 : 0) + (p.dob.isMet ? 1 : 0) + (p.nationality.isMet ? 1 : 0) + (p.passport.isMet ? 1 : 0);
    pDetailMax += 5;
  });
  const paxTypeScore = m.pax_types ? 1 : (m.pax_count ? 0.5 : 0);
  const detailFactor = pDetailMax > 0 ? (pDetailPoints / pDetailMax) : 1;
  const passengerScore = ((paxTypeScore * 0.3) + (detailFactor * 0.7)) * (total * 0.3);

  // Completion (30%): Dates
  const completionScore = ( (m.departure_date ? 1 : 0) + (m.return_date ? 1 : 0) ) / (props.activity.required_trip_type === 'round_trip' ? 2 : 1) * (total * 0.3);

  return [
    { label: 'Compliance', score: complianceScore, max: total * 0.4, color: 'bg-[#111827]' },
    { label: 'Passengers', score: passengerScore, max: total * 0.3, color: 'bg-[#111827]' },
    { label: 'Completion', score: completionScore, max: total * 0.3, color: 'bg-[#111827]' },
    { label: 'Budget', score: 0, max: 0, color: 'bg-[#E2E8F0]' }
  ];
});

const calculatedScore = computed(() => {
  return scoreBreakdown.value.reduce((acc, current) => acc + current.score, 0);
});
</script>

<style scoped>
.comparison-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
}

.modal-content {
  position: relative;
  background: #ffffff;
  border-radius: 32px;
  width: 100%;
  max-width: 1200px;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 60px 150px -30px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  border: 1px solid #F1F5F9;
  animation: slideIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-content-scrollable {
  flex: 1;
  overflow-y: auto;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E2E8F0;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #CBD5E1;
}

.transition-all {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
