<template>
  <div class="p-6 poppins space-y-6">

    <!-- ─── Loading ─── -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-10 h-10 border-4 border-[#fe3787] border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else>

      <!-- ─── HEADER ─── -->
      <div class="relative overflow-hidden bg-gradient-to-br from-[#002D1E] to-[#014d33] rounded-[1px] p-8 shadow-xl">
        <div class="absolute -right-10 -top-10 w-48 h-48 bg-[#fe3787] rounded-full blur-[80px] opacity-20"></div>
        <div class="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 mb-2 poppins">Learning Management</p>
            <h1 class="text-3xl font-black text-white poppins">LMS Performance <span class="text-[#fe3787]">Overview</span></h1>
            <p class="text-sm text-white/50 mt-1">Real-time analytics across all sections and activities.</p>
          </div>
          <div class="flex gap-4">
            <div v-for="(card, i) in quickCards" :key="i"
              class="bg-white/10 backdrop-blur-sm border border-white/10 rounded-[1px] px-5 py-4 text-center min-w-[90px]">
              <p class="text-2xl font-black text-white">{{ card.value }}</p>
              <p class="text-[9px] uppercase font-bold text-white/50 tracking-widest mt-1">{{ card.label }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── ROW 1: Donut + Status Breakdown ─── -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Activity Status Donut -->
        <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
          <p class="text-[10px] uppercase font-black tracking-[0.2em] text-gray-400 mb-6">Activity Status Breakdown</p>
          <div class="flex items-center gap-8">
            <!-- SVG Donut -->
            <div class="relative flex-shrink-0">
              <svg width="160" height="160" viewBox="0 0 160 160">
                <circle cx="80" cy="80" r="60" fill="none" stroke="#f3f4f6" stroke-width="22"/>
                <circle
                  v-for="(seg, i) in donutSegments" :key="i"
                  cx="80" cy="80" r="60"
                  fill="none"
                  :stroke="seg.color"
                  stroke-width="22"
                  :stroke-dasharray="`${seg.dash} ${seg.gap}`"
                  :stroke-dashoffset="seg.offset"
                  stroke-linecap="butt"
                  style="transition: stroke-dasharray 0.8s ease"
                />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <p class="text-2xl font-black text-[#002D1E]">{{ totalBindings }}</p>
                <p class="text-[9px] uppercase font-bold text-gray-400">Total</p>
              </div>
            </div>
            <!-- Legend -->
            <div class="space-y-3 flex-1">
              <div v-for="item in statusItems" :key="item.key" class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 rounded-full flex-shrink-0" :style="{background: item.color}"></div>
                  <span class="text-sm font-medium text-gray-600 capitalize">{{ item.label }}</span>
                </div>
                <div class="flex items-center gap-3">
                  <div class="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-700" :style="{width: pct(item.count) + '%', background: item.color}"></div>
                  </div>
                  <span class="text-sm font-bold text-[#002D1E] w-8 text-right">{{ item.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Completion Rate (overall + per-status %) -->
        <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
          <p class="text-[10px] uppercase font-black tracking-[0.2em] text-gray-400 mb-6">Overall Completion Rate</p>
          <div class="flex flex-col items-center justify-center h-[calc(100%-2rem)]">
            <!-- Big radial progress ring -->
            <div class="relative">
              <svg width="140" height="140" class="-rotate-90">
                <circle cx="70" cy="70" r="56" fill="none" stroke="#f3f4f6" stroke-width="14"/>
                <circle cx="70" cy="70" r="56" fill="none" stroke="#fe3787" stroke-width="14"
                  stroke-linecap="round"
                  :stroke-dasharray="`${completionRate * 3.52} ${352 - completionRate * 3.52}`"
                  style="transition: stroke-dasharray 1s ease"/>
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center rotate-90 -scale-x-100" style="transform: rotate(0deg)">
                <p class="text-4xl font-black text-[#002D1E]">{{ completionRate }}<span class="text-xl">%</span></p>
                <p class="text-[9px] font-bold text-gray-400 uppercase">Completed</p>
              </div>
            </div>
            <div class="mt-4 grid grid-cols-2 gap-3 w-full">
              <div v-for="item in statusItems.slice(0,4)" :key="item.key"
                class="bg-gray-50 border border-gray-100 rounded-[1px] p-3 text-center">
                <p class="text-lg font-black" :style="{color: item.color}">{{ pct(item.count) }}%</p>
                <p class="text-[9px] uppercase font-bold text-gray-400 capitalize">{{ item.label }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── ROW 2: Section Bar Chart ─── -->
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <div class="flex items-center justify-between mb-6">
          <p class="text-[10px] uppercase font-black tracking-[0.2em] text-gray-400">Section Completion Rate</p>
          <div class="flex items-center gap-4 text-[10px] font-bold uppercase text-gray-400">
            <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-[1px] bg-[#fe3787] inline-block"></span>Completed %</div>
            <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-[1px] bg-[#002D1E] inline-block"></span>Avg Grade</div>
          </div>
        </div>
        <div v-if="data.section_stats.length === 0" class="py-10 text-center text-gray-400 italic text-sm">
          No section data yet. Sections with activities will appear here.
        </div>
        <div v-else class="space-y-4">
          <div v-for="sec in data.section_stats.slice(0, 8)" :key="sec.name" class="group">
            <div class="flex items-center justify-between mb-1.5">
              <div>
                <span class="text-sm font-bold text-[#002D1E]">{{ sec.name }}</span>
                <span class="ml-2 text-[10px] text-gray-400">{{ sec.enrolled }} enrolled · {{ sec.completed }}/{{ sec.total }} done</span>
              </div>
              <div class="flex items-center gap-3">
                <span v-if="sec.avg_grade" class="text-xs font-black text-[#002D1E] bg-gray-100 px-2 py-0.5 rounded-full">
                  Avg: {{ sec.avg_grade }}
                </span>
                <span class="text-sm font-black text-[#fe3787]">{{ sec.rate }}%</span>
              </div>
            </div>
            <!-- Double bar stack -->
            <div class="relative h-3 bg-gray-100 rounded-full overflow-hidden">
              <div class="absolute inset-y-0 left-0 rounded-full bg-[#fe3787]/20 transition-all duration-700"
                :style="{width: sec.rate + '%'}"></div>
              <div class="absolute inset-y-0 left-0 rounded-full bg-[#fe3787] transition-all duration-700"
                :style="{width: sec.rate + '%', opacity: 0.85}"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── ROW 3: Timeline + Leaderboard ─── -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">

        <!-- Submission Timeline (3/5) -->
        <div class="lg:col-span-3 bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
          <p class="text-[10px] uppercase font-black tracking-[0.2em] text-gray-400 mb-6">Weekly Submissions (Last 8 Weeks)</p>
          <div v-if="data.timeline.length === 0" class="py-10 text-center text-gray-400 italic text-sm">
            No submissions recorded in the past 8 weeks.
          </div>
          <div v-else class="flex items-end gap-2 h-40">
            <div v-for="(w, i) in paddedTimeline" :key="i"
              class="flex-1 flex flex-col items-center gap-1 group cursor-default">
              <span class="text-[9px] font-bold text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">{{ w.count }}</span>
              <div class="w-full rounded-t-[2px] transition-all duration-700 relative"
                :class="w.count > 0 ? 'bg-[#fe3787]' : 'bg-gray-100'"
                :style="{height: barHeight(w.count) + 'px', minHeight: '4px'}">
              </div>
              <span class="text-[8px] text-gray-400 font-bold text-center leading-tight">{{ w.week }}</span>
            </div>
          </div>
        </div>

        <!-- Top Students Leaderboard (2/5) -->
        <div class="lg:col-span-2 bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
          <p class="text-[10px] uppercase font-black tracking-[0.2em] text-gray-400 mb-4">Top Performers</p>
          <div v-if="data.top_students.length === 0" class="py-6 text-center text-gray-400 italic text-sm">
            No graded submissions yet.
          </div>
          <div v-else class="space-y-3">
            <div v-for="(s, i) in data.top_students" :key="s.student_number"
              class="flex items-center gap-3 p-3 rounded-[1px] border border-gray-100 hover:border-[#fe3787]/20 hover:bg-pink-50/30 transition-all group">
              <!-- Rank Badge -->
              <div class="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-black flex-shrink-0"
                :class="rankClass(i)">
                {{ i + 1 }}
              </div>
              <!-- Info -->
              <div class="flex-1 min-w-0">
                <p class="text-sm font-bold text-[#002D1E] truncate">{{ s.name }}</p>
                <p class="text-[10px] text-gray-400"># {{ s.student_number }} · {{ s.completed }} done</p>
              </div>
              <!-- Grade -->
              <div class="text-right">
                <p class="text-lg font-black" :style="{color: gradeColor(s.avg_grade)}">{{ s.avg_grade }}</p>
                <p class="text-[9px] uppercase font-bold text-gray-400">avg pts</p>
              </div>
            </div>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/services/admin/api';

const loading = ref(true);
const data = ref({
  totals: {},
  status_breakdown: {},
  section_stats: [],
  timeline: [],
  top_students: [],
});

// ── Fetch ──
const fetchData = async () => {
  try {
    const res = await api.get('/admin/lms-overview/');
    data.value = res.data;
  } catch (e) {
    console.error('LMS Overview fetch error:', e);
  }
  loading.value = false;
};

// ── Quick header cards ──
const quickCards = computed(() => [
  { label: 'Students',    value: data.value.totals?.students    || 0 },
  { label: 'Instructors', value: data.value.totals?.instructors || 0 },
  { label: 'Sections',    value: data.value.totals?.sections    || 0 },
  { label: 'Activities',  value: data.value.totals?.activities  || 0 },
]);

// ── Status items with colors ──
const statusConfig = {
  assigned:    { label: 'Assigned',    color: '#94a3b8' },
  in_progress: { label: 'In Progress', color: '#f59e0b' },
  submitted:   { label: 'Submitted',   color: '#3b82f6' },
  completed:   { label: 'Completed',   color: '#22c55e' },
  failed:      { label: 'Failed',      color: '#ef4444' },
};

const statusItems = computed(() =>
  Object.entries(statusConfig).map(([key, cfg]) => ({
    key,
    label: cfg.label,
    color: cfg.color,
    count: data.value.status_breakdown?.[key] || 0,
  }))
);

const totalBindings = computed(() =>
  statusItems.value.reduce((a, b) => a + b.count, 0)
);

const pct = (n) => totalBindings.value > 0 ? Math.round((n / totalBindings.value) * 100) : 0;

const completionRate = computed(() => pct(data.value.status_breakdown?.completed || 0));

// ── Donut SVG segments ──
const CIRC = 2 * Math.PI * 60; // circumference at r=60
const donutSegments = computed(() => {
  let offset = 0;
  return statusItems.value
    .filter(i => i.count > 0)
    .map((item) => {
      const fraction = totalBindings.value > 0 ? item.count / totalBindings.value : 0;
      const dash = fraction * CIRC;
      const gap = CIRC - dash;
      // SVG starts at 3 o'clock; we want 12 o'clock start → offset by -CIRC/4
      const seg = {
        color: item.color,
        dash,
        gap,
        offset: CIRC / 4 - offset,
      };
      offset += dash;
      return seg;
    });
});

// ── Timeline bar chart ──
const maxCount = computed(() =>
  Math.max(1, ...data.value.timeline.map(t => t.count))
);

// Pad timeline to always show 8 bars
const paddedTimeline = computed(() => {
  const tl = data.value.timeline;
  if (tl.length >= 8) return tl.slice(-8);
  const pad = Array(8 - tl.length).fill({ week: '', count: 0 });
  return [...pad, ...tl];
});

const barHeight = (count) => {
  return Math.round((count / maxCount.value) * 120);
};

// ── Rank badge colors ──
const rankClass = (i) => {
  if (i === 0) return 'bg-yellow-400 text-white';
  if (i === 1) return 'bg-gray-300 text-gray-700';
  if (i === 2) return 'bg-orange-400 text-white';
  return 'bg-gray-100 text-gray-500';
};

const gradeColor = (g) => {
  if (g >= 90) return '#22c55e';
  if (g >= 75) return '#f59e0b';
  return '#ef4444';
};

onMounted(fetchData);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
.poppins { font-family: 'Poppins', sans-serif; }
</style>
