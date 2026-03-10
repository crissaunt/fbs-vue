<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900 p-8">
    <!-- Navigation Back Link -->
    <div class="max-w-7xl mx-auto mb-6 flex justify-between items-center">
      <button @click="goBack" class="text-sm font-semibold text-gray-500 hover:text-black transition-all flex items-center gap-2">
        ← Back to Activity Details
      </button>
      <div v-if="storedGrade !== null" class="px-4 py-2 bg-emerald-100 text-emerald-700 rounded-lg text-xs font-black uppercase tracking-widest border border-emerald-200">
        Assessment Finalized
      </div>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="w-12 h-1 bg-gray-200 rounded-full overflow-hidden mb-4">
        <div class="h-full bg-blue-500 w-1/3 animate-[loading_1s_infinite_linear]"></div>
      </div>
      <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Generating Your Assessment Analysis...</p>
    </div>

    <!-- Results not released notification -->
    <div v-if="!loading && !error && activity && activity.grade === null" class="max-w-xl mx-auto py-20 text-center px-4">
      <div class="inline-flex items-center justify-center w-20 h-20 bg-amber-50 text-amber-500 rounded-full mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h2 class="text-3xl font-black text-gray-900 mb-4 tracking-tight">Results Not Released Yet</h2>
      <p class="text-gray-500 mb-8 font-medium">Your instructor hasn't released the assessment results for this activity. Please check back later.</p>
      <button @click="goBack" class="px-8 py-3 bg-gray-900 text-white rounded-xl font-bold hover:bg-black transition-all shadow-lg uppercase tracking-widest text-xs">Back to Activity</button>
    </div>

    <main v-else-if="!loading && !error && activity" class="max-w-5xl mx-auto space-y-6 pb-20 px-4">
      
      <!-- Clean Header & Points Summary -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 space-y-6">
        <div class="flex justify-between items-start">
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-[10px] font-black rounded uppercase">Graded</span>
              <span class="text-xs text-gray-400 font-bold uppercase tracking-widest">{{ activity.section_code }}</span>
            </div>
            <h1 class="text-3xl font-bold text-gray-900 mb-1 tracking-tight">{{ activity?.title }}</h1>
            <p class="text-gray-500 font-medium text-sm">Results for {{ student?.first_name }} {{ student?.last_name }}</p>
          </div>
          <div class="text-right">
            <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Final Assessment Score</p>
            <div class="text-4xl font-black text-emerald-600 tracking-tighter">
              {{ Math.round((calculatedScore / (activity?.total_points || 100)) * 100) }}%
            </div>
          </div>
        </div>

        <div class="grid grid-cols-4 gap-4 border-t border-gray-100 pt-6">
          <div v-for="item in scoreBreakdown" :key="item.label" class="p-5 bg-gray-50 rounded-xl text-center border border-gray-100 relative overflow-hidden group hover:border-emerald-200 transition-colors">
            <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">{{ item.label }} Weight</p>
            <p class="text-2xl font-black text-gray-900">
              {{ Math.round((item.score / item.max) * 100) }}%
            </p>
            <div class="absolute bottom-0 left-0 h-1 bg-emerald-500" :style="{ width: (item.score / item.max * 100) + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- Compliance Comparison Table -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="px-8 py-5 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <h2 class="text-xs font-black text-gray-900 uppercase tracking-widest">Compliance Verification</h2>
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Weights: 40% of grade</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full border-collapse text-left">
            <thead>
              <tr class="bg-white text-gray-400 text-[10px] font-black uppercase tracking-widest border-b border-gray-100">
                <th class="p-4 pl-8">Requirement</th>
                <th class="p-4">Expected Detail</th>
                <th class="p-4">Your Submitted Work</th>
                <th class="p-4 text-center pr-8">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="row in comparisonRows" :key="row.label" 
                class="hover:bg-gray-50/50 transition-colors group"
                :class="!row.isMet && 'bg-red-50/30'"
              >
                <td class="p-4 pl-8">
                  <span class="text-xs font-bold text-gray-700 block">{{ row.label }}</span>
                  <span :class="['text-[9px] font-black uppercase px-1.5 py-0.5 rounded', row.priority === 'High' ? 'bg-red-50 text-red-500' : 'bg-gray-100 text-gray-500']">
                    {{ row.priority }}
                  </span>
                </td>
                <td class="p-4 text-xs text-gray-600 font-medium">{{ row.requirement }}</td>
                <td class="p-4 text-xs font-bold" :class="row.isMet ? 'text-gray-900' : 'text-red-700'">{{ row.work }}</td>
                <td class="p-4 text-center pr-8">
                  <div v-if="row.isMet" class="flex flex-col items-center">
                    <span class="w-6 h-6 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center text-[10px] mb-0.5">✓</span>
                    <span class="text-[8px] font-black text-emerald-600 uppercase">Correct</span>
                  </div>
                  <div v-else class="flex flex-col items-center">
                    <span class="w-6 h-6 bg-red-100 text-red-700 rounded-full flex items-center justify-center text-[10px] mb-0.5">✕</span>
                    <span class="text-[8px] font-black text-red-600 uppercase">Mismatch</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Add-ons Verification Table (Compliance Style) -->
      <div v-if="matches.addons?.length" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
        <div class="px-8 py-5 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <h2 class="text-xs font-black text-gray-900 uppercase tracking-widest">Add-on & Service Compliance (10%)</h2>
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Baggage, Meals, Insurance & Others</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full border-collapse text-left">
            <thead>
              <tr class="bg-white text-gray-400 text-[10px] font-black uppercase tracking-widest border-b border-gray-100">
                <th class="p-4 pl-8">Passenger</th>
                <th class="p-4">Requirement</th>
                <th class="p-4">Your Selection</th>
                <th class="p-4 text-center pr-8">Result</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="(addon, aIdx) in matches.addons" :key="aIdx" 
                class="hover:bg-gray-50/50 transition-colors group"
                :class="!addon.isMet && 'bg-red-50/30'"
              >
                <td class="p-4 pl-8 font-bold text-gray-700 text-xs">{{ addon.passengerName }}</td>
                <td class="p-4 text-xs text-gray-600 font-medium">{{ addon.requirement }}</td>
                <td class="p-4 text-xs font-bold" :class="addon.isMet ? 'text-gray-900' : 'text-red-700'">{{ addon.actual || 'None' }}</td>
                <td class="p-4 text-center pr-8">
                  <div class="flex flex-col items-center">
                    <span v-if="addon.isMet" class="w-6 h-6 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center text-[10px] mb-0.5">✓</span>
                    <span v-else class="w-6 h-6 bg-red-100 text-red-700 rounded-full flex items-center justify-center text-[10px] mb-0.5">✕</span>
                    <span :class="['text-[8px] font-black uppercase', addon.isMet ? 'text-emerald-600' : 'text-red-600']">
                      {{ addon.isMet ? 'Correct' : 'Wrong' }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Passenger Comparison Tables -->
      <div v-if="matches.passenger_details?.length" class="space-y-4">
        <div class="flex items-center justify-between px-2">
          <h2 class="text-xs font-black text-gray-900 uppercase tracking-widest">Passenger Identity Verification (25%)</h2>
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest px-2 py-1 bg-gray-100 rounded-full">{{ matches.passenger_details.length }} Records Analyzed</span>
        </div>

        <div class="grid grid-cols-1 gap-6">
          <div v-for="(p, idx) in matches.passenger_details" :key="idx" 
            class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-white border border-gray-200 rounded-lg flex items-center justify-center text-xs font-black text-gray-400">
                  {{ idx + 1 }}
                </div>
                <h3 class="text-sm font-bold text-gray-700">
                  Passenger: <span class="text-emerald-600">{{ p.name.expected }}</span>
                </h3>
              </div>
              <span 
                class="px-2.5 py-1 rounded text-[10px] font-black uppercase tracking-widest border shadow-sm"
                :class="isPassengerPerfect(p) ? 'bg-emerald-500 text-white border-emerald-600' : 'bg-red-500 text-white border-red-600'"
              >
                {{ isPassengerPerfect(p) ? 'IDENTITY VERIFIED' : 'IDENTITY FAILED' }}
              </span>
            </div>

            <table class="w-full border-collapse text-left">
              <thead>
                <tr class="bg-white text-gray-400 text-[9px] font-black uppercase tracking-widest border-b border-gray-100">
                  <th class="px-6 py-3 pl-10">Verification Field</th>
                  <th class="px-6 py-3">Assigned Requirement</th>
                  <th class="px-6 py-3">Student Entry</th>
                  <th class="px-6 py-3 text-center pr-10">Result</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="(field, key) in p" :key="key" 
                  class="text-xs transition-colors hover:bg-gray-50/50"
                  :class="!field.isMet && 'bg-red-50/30'"
                >
                  <td class="px-6 py-3 pl-10">
                    <span class="text-[10px] font-black text-gray-400 uppercase tracking-tighter">{{ key === 'dob' ? 'Date of Birth' : key }}</span>
                  </td>
                  <td class="px-6 py-3 font-medium text-gray-700">{{ field.expected }}</td>
                  <td class="px-6 py-3 font-black" :class="field.isMet ? 'text-gray-900' : 'text-red-700'">{{ field.actual }}</td>
                  <td class="px-6 py-3 text-center pr-10">
                    <span v-if="field.isMet" class="text-emerald-500 font-bold block">✓ Matches</span>
                    <span v-else class="text-red-500 font-bold block">✕ Error</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Footer/Return Button -->
      <div class="pt-8 flex flex-col items-center gap-4">
        <button @click="goBack" class="px-12 py-4 bg-gray-900 text-white rounded-xl text-xs font-black hover:bg-black transition-all uppercase tracking-widest shadow-xl border-t-4 border-gray-700">
          Return to Activity Details
        </button>
        <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest italic">Assessment ID: #{{ activityId }}-{{ student?.id }}</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { studentActivityDetailsService } from '@/services/Student/studentActivityDetailsService';
import { bookingService } from '@/services/booking/bookingService';
import { useNotificationStore } from '@/stores/notification';

const route = useRoute();
const router = useRouter();
const notificationStore = useNotificationStore();

const activityId = route.params.activityId;

const loading = ref(true);
const error = ref(null);
const activity = ref(null);
const booking = ref(null);
const student = ref(null);
const storedGrade = ref(null);

const fetchData = async () => {
    loading.value = true;
    error.value = null;
    try {
        const response = await studentActivityDetailsService.getActivityDetails(activityId);
        const data = response.data;
        
        if (data && data.activity) {
            activity.value = data.activity;
            student.value = data.student;
            storedGrade.value = data.activity.grade;

            if (data.activity.confirmed_booking_id) {
                const bookingRes = await bookingService.getBookingDetails(data.activity.confirmed_booking_id);
                if (bookingRes.success) {
                    booking.value = bookingRes.booking;
                }
            }
        } else {
            error.value = "We couldn't find the assessment details for this activity.";
        }
    } catch (err) {
        console.error('Failed to fetch assessment analysis:', err);
        error.value = err.response?.data?.error || "An error occurred while loading your assessment details. Please try again later.";
        notificationStore.error('Could not load analysis details.');
    } finally {
        loading.value = false;
    }
};

const scoreBreakdown = computed(() => {
    if (!activity.value || !booking.value) return [];

    const m = matches.value;
    const totalPoints = parseFloat(activity.value.total_points || 100);

    // --- PRIMARY: Use backend-computed analysis ---
    if (activity.value?.analysis?.breakdown) {
        const b = activity.value.analysis.breakdown;
        return [
            { label: 'Compliance', score: parseFloat(b.compliance), max: totalPoints * 0.4 },
            { label: 'Passenger', score: parseFloat(b.passengers), max: totalPoints * 0.25 },
            { label: 'Completion', score: parseFloat(b.completion), max: totalPoints * 0.25 },
            { label: 'Add-ons', score: parseFloat(b.addons || 0), max: totalPoints * 0.1 }
        ];
    }

    // --- FALLBACK: Client-side calculation ---
    const compMax = totalPoints * 0.4;
    let compPenalty = 0;
    if (!m.trip_type) compPenalty += 20;
    if (!m.origin) compPenalty += 40;
    if (!m.destination) compPenalty += 40;
    if (!m.travel_class) compPenalty += 10;
    const compScore = Math.max(0, compMax * (1 - compPenalty / 100.0));

    const paxMax = totalPoints * 0.25;
    let paxPenalty = 0;
    const paxTypes = actualPaxTypes.value;
    if (paxTypes.adult !== activity.value.required_passengers) paxPenalty += 10;
    if (paxTypes.child !== (activity.value.required_children || 0)) paxPenalty += 10;
    if (paxTypes.infant !== (activity.value.required_infants || 0)) paxPenalty += 10;

    m.passenger_details.forEach(p => {
        if (!p.name.isMet) paxPenalty += 25;
        if (!p.gender.isMet) paxPenalty += 2;
        if (!p.dob.isMet) paxPenalty += 5;
        if (!p.nationality.isMet) paxPenalty += 3;
        if (!p.passport.isMet) paxPenalty += 10;
    });
    const paxScore = Math.max(0, paxMax * (1 - paxPenalty / 100.0));

    const completionMax = totalPoints * 0.25;
    let datePenalty = 0;
    if (!m.departure_date) datePenalty += 15;
    if (!m.return_date) datePenalty += 15;
    const completionScore = Math.max(0, completionMax * (1 - datePenalty / 100.0));

    const addonMax = totalPoints * 0.1;
    let addonScore = addonMax;
    if (m.addons?.length) {
        const correctCount = m.addons.filter(a => a.isMet).length;
        addonScore = addonMax * (correctCount / m.addons.length);
    }

    return [
        { label: 'Compliance', score: Math.round(compScore), max: compMax },
        { label: 'Passenger', score: Math.round(paxScore), max: paxMax },
        { label: 'Completion', score: Math.round(completionScore), max: completionMax },
        { label: 'Add-ons', score: Math.round(addonScore), max: addonMax }
    ];
});

const calculatedScore = computed(() => {
    // Use backend-stored grade for the total (matches what instructor sees)
    if (activity.value?.grade !== null && activity.value?.grade !== undefined) {
        return parseFloat(activity.value.grade);
    }
    return scoreBreakdown.value.reduce((acc, c) => acc + c.score, 0);
});


onMounted(fetchData);

const goBack = () => router.push(`/student/activity/${activityId}`);

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

const actualRoute = computed(() => {
    if (!booking.value || !booking.value.details || booking.value.details.length === 0) return null;
    const segments = booking.value.details;
    if (segments.length === 1) {
        return `${segments[0].schedule.origin} → ${segments[0].schedule.destination}`;
    }
    const cities = [segments[0].schedule.origin];
    segments.forEach(seg => {
        if (cities[cities.length - 1] !== seg.schedule.destination) {
            cities.push(seg.schedule.destination);
        }
    });
    return cities.join(' → ');
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
        pax_types: (actualPaxTypes.value.adult || 0) === (activity.value.required_passengers || 0) && 
                   (actualPaxTypes.value.child || 0) === (activity.value.required_children || 0) && 
                   (actualPaxTypes.value.infant || 0) === (activity.value.required_infants || 0),
        passenger_details: [],
        addons: []
    };

    // 1. Passenger Identities
    const bookedPassengers = [];
    const seenPId = new Set();
    booking.value.details.forEach(d => {
        if (!d.passenger) return;
        const pId = d.passenger.id || `${d.passenger.first_name}_${d.passenger.last_name}`;
        if (!seenPId.has(pId)) {
            seenPId.add(pId);
            bookedPassengers.push(d.passenger);
        }
    });

    const usedIndices = new Set();
    if (activity.value.passengers) {
        activity.value.passengers.forEach(expected => {
            // Find match among unused booked passengers
            let actualIdx = bookedPassengers.findIndex((p, idx) => 
                !usedIndices.has(idx) && 
                p.first_name?.toLowerCase() === expected.first_name?.toLowerCase() && 
                p.last_name?.toLowerCase() === expected.last_name?.toLowerCase()
            );

            let actual = null;
            if (actualIdx !== -1) {
                actual = bookedPassengers[actualIdx];
                usedIndices.add(actualIdx);
            }

            const detailMatch = {
                name: { 
                    expected: `${expected.first_name} ${expected.last_name}`, 
                    actual: actual ? `${actual.first_name} ${actual.last_name}` : 'NONE / MISSING', 
                    isMet: !!actual 
                },
                gender: { 
                    expected: (expected.gender || '').toUpperCase(), 
                    actual: (actual?.title || actual?.gender || '-').toUpperCase(), 
                    isMet: false 
                },
                dob: { 
                    expected: expected.date_of_birth, 
                    actual: actual?.date_of_birth || '-', 
                    isMet: false 
                },
                nationality: { 
                    expected: expected.nationality, 
                    actual: actual?.nationality || '-', 
                    isMet: false 
                },
                passport: { 
                    expected: activity.value.require_passport ? (expected.passport_number || 'REQUIRED') : 'NO PASSPORT REQ.', 
                    actual: actual?.passport_number || 'NONE', 
                    isMet: !activity.value.require_passport // Always met if not required
                }
            };

            if (actual) {
                const actualGen = (actual.title || actual.gender || '').toLowerCase().replace('.', '').trim();
                const expectedGen = (expected.gender || '').toLowerCase().replace('.', '').trim();
                detailMatch.gender.isMet = actualGen === expectedGen;
                detailMatch.dob.isMet = actual.date_of_birth === expected.date_of_birth;
                detailMatch.nationality.isMet = actual.nationality?.toLowerCase() === expected.nationality?.toLowerCase();
                
                if (activity.value.require_passport) {
                    detailMatch.passport.isMet = (actual.passport_number || '').trim() === (expected.passport_number || '').trim();
                }
            }
            m.passenger_details.push(detailMatch);
        });
    }

    // 2. Add-ons
    if (activity.value.activity_addons?.length) {
        activity.value.activity_addons.forEach(req => {
            const detail = booking.value.details.find(d => 
                d.passenger?.first_name?.toLowerCase() === req.passenger.first_name?.toLowerCase() &&
                d.passenger?.last_name?.toLowerCase() === req.passenger.last_name?.toLowerCase()
            );

            const isMet = detail?.addons?.some(a => a.id === req.addon_id) || false;
            m.addons.push({
                passengerName: `${req.passenger.first_name} ${req.passenger.last_name}`,
                requirement: req.addon_name || req.addon?.name || 'Required Add-on',
                actual: detail?.addons?.map(a => a.name).join(', ') || 'None',
                isMet: isMet
            });
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
        { 
            label: 'Passengers', 
            priority: 'High', 
            requirement: [
                `${activity.value.required_passengers || 0} Adult(s)`,
                activity.value.required_children ? `${activity.value.required_children} Child(ren)` : '',
                activity.value.required_infants ? `${activity.value.required_infants} Infant(s)` : ''
            ].filter(Boolean).join(', '),
            work: [
                `${actualPaxTypes.value.adult || 0} Adult(s)`,
                actualPaxTypes.value.child ? `${actualPaxTypes.value.child} Child(ren)` : '',
                actualPaxTypes.value.infant ? `${actualPaxTypes.value.infant} Infant(s)` : ''
            ].filter(Boolean).join(', '),
            isMet: m.pax_types 
        },
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
