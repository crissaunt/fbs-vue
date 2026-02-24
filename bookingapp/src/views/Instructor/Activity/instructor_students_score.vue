<template>
  <div class="min-h-screen bg-[#F3F4F6] font-sans text-gray-900 p-8">
    <!-- Navigation Back Link -->
    <div class="max-w-7xl mx-auto mb-6">
      <button @click="goBack" class="text-sm font-semibold text-gray-500 hover:text-black transition-all flex items-center gap-2">
        ← Back to Submissions
      </button>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="w-12 h-1 bg-gray-200 rounded-full overflow-hidden mb-4">
        <div class="h-full bg-blue-500 w-1/3 animate-[loading_1s_infinite_linear]"></div>
      </div>
      <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Generating Analysis</p>
    </div>

    <main v-else class="max-w-7xl mx-auto space-y-8">
      
      <!-- Top Card: Activity Summary & Score -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-10 flex flex-col lg:flex-row gap-12">
        <!-- Left: Activity Info & Score -->
        <div class="flex-1 space-y-8">
          <div>
            <h1 class="text-4xl font-bold mb-2 tracking-tight">{{ activity?.title || 'Title of Activity' }}</h1>
            <p class="text-gray-500 font-medium text-lg">{{ activity?.course_code || 'CS-101' }} - {{ activity?.block || 'Block A' }}</p>
            <p class="text-gray-400 text-sm mt-1">Due: {{ formatDueDate(activity?.due_date) }}</p>
            
            <div class="flex gap-2 mt-4">
              <span class="px-3 py-1 bg-blue-100 text-blue-600 text-[10px] font-bold rounded-full uppercase tracking-tighter">Flight Booking</span>
              <span class="px-3 py-1 bg-green-100 text-green-600 text-[10px] font-bold rounded-full uppercase tracking-tighter">Active</span>
              <span class="px-3 py-1 bg-yellow-100 text-yellow-600 text-[10px] font-bold rounded-full uppercase tracking-tighter">Submitted</span>
            </div>
          </div>

          <div class="space-y-4">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Student Score:</p>
            <div class="bg-[#D1FAE5] rounded-lg p-10 flex items-center justify-center border border-[#A7F3D0]">
              <span class="text-6xl font-bold tracking-tighter">
                {{ calculatedScore.toFixed(0) }}/{{ activity?.total_points || 100 }}
              </span>
            </div>
          </div>
        </div>

        <!-- Right: Score Breakdown Bars -->
        <div class="w-full lg:w-1/2 bg-[#F9FAFB] rounded-xl border border-gray-100 p-8">
          <h2 class="text-lg font-bold mb-8">Score Breakdown</h2>
          <div class="space-y-8">
            <div v-for="item in scoreBreakdown" :key="item.label" class="space-y-3">
              <div class="flex justify-between items-end">
                <p class="text-sm font-bold text-gray-700">{{ item.label }}: {{ item.score.toFixed(1) }} / {{ item.max.toFixed(1) }} pts</p>
              </div>
              <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full transition-all duration-1000" 
                  :class="getBarColor(item.score, item.max)"
                  :style="{ width: (item.score / item.max * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Card: Comparison Table -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-10 space-y-8">
        <h2 class="text-2xl font-bold flex items-center">
          Requirements <span class="text-gray-400 font-normal px-2 text-sm italic">vs</span> Student Work
        </h2>

        <div class="overflow-hidden border border-gray-200 rounded-lg">
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-gray-50 text-gray-700 text-sm font-bold">
                <th class="border border-gray-200 p-4 text-left">Category</th>
                <th class="border border-gray-200 p-4 text-left">Activity Requirement</th>
                <th class="border border-gray-200 p-4 text-left">Student Work</th>
                <th class="border border-gray-200 p-4 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in comparisonRows" :key="row.label" 
                class="transition-colors text-sm"
                :class="row.isMet ? 'bg-[#DCFCE7]' : 'bg-[#FEE2E2]'"
              >
                <td class="border border-gray-200 p-4">
                  <p class="font-bold text-gray-900">{{ row.label }}</p>
                  <p class="text-[11px] text-gray-400">({{ row.priority }} priority)</p>
                </td>
                <td class="border border-gray-200 p-4 font-medium">{{ row.requirement }}</td>
                <td class="border border-gray-200 p-4 font-medium" :class="!row.isMet && 'text-red-600'">{{ row.work }}</td>
                <td class="border border-gray-200 p-4">
                  <div class="flex items-center gap-2 font-bold" :class="row.isMet ? 'text-green-700' : 'text-red-700'">
                    <span>{{ row.isMet ? '✓' : '✕' }}</span>
                    <span>{{ row.isMet ? 'Met' : 'Not Met' }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Passenger Verification: Explicit Comparison -->
      <div v-if="matches.passenger_details?.length" class="mb-20">
        <h2 class="text-2xl font-bold mb-8 flex items-center gap-3">
          Passenger Information <span class="text-gray-400 font-normal px-2 text-sm italic">vs</span> Submission Data
        </h2>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div v-for="(p, idx) in matches.passenger_details" :key="idx" 
            class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <!-- Traveler Card Header -->
            <div class="bg-gray-50 border-b border-gray-200 p-6 flex justify-between items-center">
              <div>
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-none mb-1">Dossier Identity</p>
                <h3 class="text-lg font-bold">Passenger 0{{ idx + 1 }}</h3>
              </div>
              <div 
                class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border"
                :class="isPassengerPerfect(p) ? 'bg-green-100 text-green-700 border-green-200' : 'bg-red-100 text-red-700 border-red-200'"
              >
                {{ isPassengerPerfect(p) ? 'Fully Verified' : 'Discrepancy Found' }}
              </div>
            </div>

            <!-- Traveler Comparison Body -->
            <div class="p-0">
              <div class="grid grid-cols-4 bg-gray-50/50 text-[10px] font-black uppercase tracking-widest text-gray-500 border-b border-gray-100">
                <div class="p-4 border-r border-gray-100">Field</div>
                <div class="p-4 border-r border-gray-100">Activity Req.</div>
                <div class="p-4 border-r border-gray-100">Student Work</div>
                <div class="p-4 text-center">Status</div>
              </div>
              <div v-for="(field, key) in p" :key="key" 
                class="grid grid-cols-4 text-xs font-bold border-b border-gray-100 last:border-0 transition-colors"
                :class="field.isMet ? 'bg-green-50/20' : 'bg-red-50/20'"
              >
                <div class="p-4 border-r border-gray-100 text-gray-400 uppercase tracking-tighter">{{ key }}</div>
                <div class="p-4 border-r border-gray-100 truncate text-gray-500">{{ field.expected }}</div>
                <div class="p-4 border-r border-gray-100 truncate" :class="!field.isMet && 'text-red-600'">{{ field.actual }}</div>
                <div class="p-4 flex items-center justify-center">
                  <span v-if="field.isMet" class="text-green-600">✓</span>
                  <span v-else class="text-red-600">✕</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions Footer removed for Automated Grading -->
      <div class="flex justify-start items-center gap-4 pb-20">
        <button @click="goBack" class="px-8 py-4 border-2 border-gray-200 rounded-xl text-sm font-bold hover:bg-white transition-all uppercase tracking-widest text-[#FFC145]">← Back to Student Submissions</button>
      </div>
    </main>

    <!-- Success Overlay removed for Automated Grading -->

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { activityDetailsService } from '@/services/instructor/activityDetailsService';
import { bookingService } from '@/services/booking/bookingService';
import { useNotificationStore } from '@/stores/notification';

const route = useRoute();
const router = useRouter();
const notificationStore = useNotificationStore();

const activityId = route.params.activityId;
const studentId = route.params.studentId;

const loading = ref(true);
const error = ref(null);
const activity = ref(null);
const booking = ref(null);
const student = ref(null);

const fetchData = async () => {
    loading.value = true;
    error.value = null;
    try {
        const actData = await activityDetailsService.getActivity(activityId);
        activity.value = actData;

        const subData = await activityDetailsService.getSubmissions(activityId);
        const submission = subData.submissions.find(s => s.student_id == studentId);
        
        if (!submission) throw new Error("Submission not found.");
        
        student.value = { first_name: submission.first_name, last_name: submission.last_name, student_number: submission.student_number };

        if (!submission.booking) throw new Error("No student work data.");

        const bookingRes = await bookingService.getBookingDetails(submission.booking.id);
        if (bookingRes.success) {
            booking.value = bookingRes.booking;
        } else {
            throw new Error("Failed to load booking details.");
        }
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
};

const scoreBreakdown = computed(() => {
    if (!activity.value || !booking.value) return [];
    
    const m = matches.value;
    const totalPoints = parseFloat(activity.value.total_points || 100);
    
    // 1. Compliance (40% base)
    let compPenalty = 0;
    if (!m.origin) compPenalty += 40;
    if (!m.destination) compPenalty += 40;
    if (!m.trip_type) compPenalty += 20;
    if (!m.travel_class) compPenalty += 10;
    
    const compScore = Math.max(0, (totalPoints * 0.4) - (compPenalty / 100 * totalPoints));
    
    // 2. Passengers (30% base)
    let paxPenalty = 0;
    const paxTypes = actualPaxTypes.value;
    if (paxTypes.adult !== activity.value.required_passengers) paxPenalty += 10;
    if (paxTypes.child !== activity.value.required_children) paxPenalty += 5;
    if (paxTypes.infant !== activity.value.required_infants) paxPenalty += 5;

    m.passenger_details?.forEach(p => {
        if (p.name.actual === 'Not Found') {
            paxPenalty += 25;
        } else {
            if (!p.gender.isMet) paxPenalty += 2;
            if (!p.dob.isMet) paxPenalty += 5;
            if (!p.nationality.isMet) paxPenalty += 3;
            if (!p.passport.isMet) paxPenalty += 10;
        }
    });
    
    const paxScore = Math.max(0, (totalPoints * 0.3) - (paxPenalty / 100 * totalPoints));

    // 3. Completion (30% base)
    let datePenalty = 0;
    const reqTripType = (activity.value.required_trip_type || '').toLowerCase().replace('_', ' ');
    if (!m.departure_date) datePenalty += 15;
    if (reqTripType === 'round trip' && !m.return_date) datePenalty += 15;
    
    const completionScore = Math.max(0, (totalPoints * 0.3) - (datePenalty / 100 * totalPoints));

    return [
        { label: 'Completion', score: completionScore, max: totalPoints * 0.3 },
        { label: 'Passengers', score: paxScore, max: totalPoints * 0.3 },
        { label: 'Compliance', score: compScore, max: totalPoints * 0.4 }
    ];
});

const calculatedScore = computed(() => {
    return scoreBreakdown.value.reduce((acc, c) => acc + c.score, 0);
});

onMounted(fetchData);

const goBack = () => router.push(`/instructor/activity/${activityId}`);

const formatDueDate = (date) => {
    if (!date) return 'TBA';
    return new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
};

const isPassengerPerfect = (p) => {
    return Object.values(p).every(field => field.isMet);
};

const getBarColor = (score, max) => {
    const ratio = score / max;
    if (ratio >= 0.8) return 'bg-[#10B981]'; // Green
    if (ratio >= 0.5) return 'bg-[#F59E0B]'; // Orange/Yellow
    return 'bg-[#EF4444]'; // Red
};

const formatTripType = (type) => {
    const map = { 'one_way': 'One_Way Trip', 'round_trip': 'Round_Trip', 'multi_city': 'Multi_City' };
    return map[type] || type || '-';
};

const formatClass = (cls) => {
    const map = { 'economy': 'Economy Class', 'premium_economy': 'Premium Economy', 'business': 'Business Class', 'first': 'First Class' };
    return map[cls?.toLowerCase()] || cls || '-';
};

const actualOrigin = computed(() => booking.value?.details?.[0]?.schedule?.origin || '-');
const actualDestination = computed(() => booking.value?.details?.[0]?.schedule?.destination || '-');
const actualClass = computed(() => booking.value?.details?.[0]?.seat_class_name || '-');
const actualDepartureDate = computed(() => {
    const date = booking.value?.details?.find(d => d.schedule?.origin?.toLowerCase() === activity.value?.required_origin?.toLowerCase())?.schedule?.departure_date;
    return date ? new Date(date).toISOString().split('T')[0] : '-';
});

const actualReturnDate = computed(() => {
    const reqTripType = (activity.value?.required_trip_type || '').toLowerCase().replace('_', ' ');
    if (reqTripType !== 'round trip') return null;
    const date = booking.value?.details?.find(d => d.schedule?.destination?.toLowerCase() === activity.value?.required_origin?.toLowerCase())?.schedule?.departure_date;
    return date ? new Date(date).toISOString().split('T')[0] : '-';
});

const actualPaxTypes = computed(() => {
    const types = { adult: 0, child: 0, infant: 0 };
    const seenPassengers = new Set();
    
    booking.value?.details?.forEach(detail => {
        const pId = detail.passenger?.id || `${detail.passenger?.first_name}_${detail.passenger?.last_name}_${detail.passenger?.date_of_birth}`;
        if (seenPassengers.has(pId)) return;
        seenPassengers.add(pId);

        const type = (detail.passenger_type || detail.passenger?.type || 'adult').toLowerCase();
        if (type === 'adult') types.adult++;
        else if (type === 'child') types.child++;
        else if (type === 'infant') types.infant++;
    });
    return types;
});

const matches = computed(() => {
    if (!activity.value || !booking.value) return {};
    
    // Normalize properties
    const reqTripType = (activity.value.required_trip_type || '').toLowerCase().replace('_', ' ');
    const actTripType = (booking.value.trip_type || '').toLowerCase().replace('_', ' ');

    const m = {
        trip_type: reqTripType === actTripType,
        origin: activity.value.required_origin?.toLowerCase() === actualOrigin.value?.toLowerCase(),
        destination: activity.value.required_destination?.toLowerCase() === actualDestination.value?.toLowerCase(),
        travel_class: activity.value.required_travel_class?.toLowerCase() === actualClass.value?.toLowerCase(),
        departure_date: !activity.value.required_departure_date || activity.value.required_departure_date === actualDepartureDate.value,
        return_date: reqTripType !== 'round trip' || !activity.value.required_return_date || activity.value.required_return_date === actualReturnDate.value,
        pax_types: actualPaxTypes.value.adult === activity.value.required_passengers && 
                   actualPaxTypes.value.child === activity.value.required_children && 
                   actualPaxTypes.value.infant === activity.value.required_infants,
        passenger_details: []
    };

    if (activity.value.passengers) {
        activity.value.passengers.forEach(expected => {
            const actual = findMatchingPassenger(expected);
            const detailMatch = {
                name: { expected: `${expected.first_name} ${expected.last_name}`, actual: actual ? `${actual.first_name} ${actual.last_name}` : 'Not Found', isMet: false },
                gender: { expected: expected.gender?.toUpperCase(), actual: (actual?.title || actual?.gender || '-').toUpperCase(), isMet: false },
                dob: { expected: expected.date_of_birth, actual: actual?.date_of_birth || '-', isMet: false },
                nationality: { expected: expected.nationality, actual: actual?.nationality || '-', isMet: false },
                passport: { expected: expected.passport_number || 'NONE', actual: actual?.passport_number || 'NONE', isMet: false }
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
    if (!booking.value?.details) return null;
    
    // 1. Try exact name match
    const exact = booking.value.details.find(d => 
        d.passenger?.first_name?.toLowerCase() === expected.first_name?.toLowerCase() &&
        d.passenger?.last_name?.toLowerCase() === expected.last_name?.toLowerCase()
    );
    if (exact) return exact.passenger;

    // 2. Collect unique passengers from booking
    const uniquePassengers = [];
    const seenIds = new Set();
    booking.value.details.forEach(d => {
        if (!d.passenger) return;
        const id = d.passenger.id || `${d.passenger.first_name}_${d.passenger.last_name}`;
        if (!seenIds.has(id)) {
            seenIds.add(id);
            uniquePassengers.push(d.passenger);
        }
    });

    // 3. Fallback to index-based match from unique list
    const idx = activity.value.passengers.indexOf(expected);
    return uniquePassengers[idx] || null;
};

const comparisonRows = computed(() => {
    if (!activity.value || !booking.value) return [];
    const m = matches.value;
    const rows = [
        { label: 'Trip Type', priority: 'High', requirement: formatTripType(activity.value.required_trip_type), work: formatTripType(booking.value.trip_type), isMet: m.trip_type },
        { label: 'Passengers', priority: 'High', requirement: `${activity.value.required_passengers} Adult(s)`, work: `${actualPaxTypes.value.adult} Adult(s)`, isMet: m.pax_types },
        { label: 'Travel Class', priority: 'High', requirement: formatClass(activity.value.required_travel_class), work: formatClass(actualClass.value), isMet: m.travel_class },
        { label: 'Flight Route', priority: 'Medium', requirement: `Depart from ${activity.value.required_origin}`, work: `Depart from ${actualOrigin.value}`, isMet: m.origin },
        { label: 'Flight Route', priority: 'Medium', requirement: `Arrive at ${activity.value.required_destination}`, work: `Arrive at ${actualDestination.value}`, isMet: m.destination },
        { label: 'Flight Details', priority: 'Medium', requirement: `Depart: ${activity.value.required_departure_date || 'Any'}`, work: actualDepartureDate.value, isMet: m.departure_date }
    ];

    if (activity.value.required_trip_type === 'round_trip') {
        rows.push({ label: 'Flight Details', priority: 'Medium', requirement: `Return: ${activity.value.required_return_date || 'Any'}`, work: actualReturnDate.value || '-', isMet: m.return_date });
    }

    return rows;
});


</script>

<style scoped>
@keyframes loading {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(300%); }
}
</style>
