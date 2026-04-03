<template>
  <div class="flex-1 flex flex-col bg-gray-200">
    <!-- <div class="bg-white mx-3 sm:mx-6 mt-4 sm:mt-5 px-5 sm:px-8 py-8 sm:py-12 rounded-lg shadow-sm relative overflow-hidden">
 
      <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
      <div class="absolute -left-10 -bottom-10 w-32 h-32 bg-pink-400/20 rounded-full blur-xl"></div>
      
      <div class="relative z-10">
        <h1 class="text-[#FF579A] text-xl sm:text-3xl font-light tracking-wide drop-shadow-sm">
          {{ sectionDisplayName }}
        </h1>
        <div class="flex flex-wrap items-center gap-4 mt-3">
          <p class="text-[#FF579A] text-sm font-medium flex items-center gap-1.5 bg-white/10 px-3 py-1 rounded-full border border-white/10 backdrop-blur-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {{ filteredActivities.length }} {{ filteredActivities.length === 1 ? 'activity' : 'activities' }}
          </p>
          
       
          <div v-if="section" class="flex flex-wrap gap-2">
            <template v-if="parsedSchedules.length > 0">
              <div v-for="(s, i) in parsedSchedules" :key="i" class="text-white/90 text-[11px] font-bold flex items-center gap-1.5 bg-pink-600/30 px-3 py-1 rounded-full border border-white/10 backdrop-blur-sm">
                <span class="opacity-70 uppercase">{{ s.day.substring(0, 3) }}</span>
                <span>{{ formatTimeOnly(s.start_time) }} - {{ formatTimeOnly(s.end_time) }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div> -->

    <!-- TABS - Only show if section exists -->
    <div v-if="section" class="mx-3 sm:mx-6 mt-4 sm:mt-5 flex items-center justify-between border-b border-slate-200">
      <div class="flex overflow-x-auto no-scrollbar">
        <button 
          v-for="tab in tabs" 
          :key="tab.name"
          :class="[
            'px-5 py-2 text-[10px] font-black transition-all uppercase tracking-widest border-b-2 flex-shrink-0',
            activeTab === tab.name 
              ? 'text-[#FF579A] border-[#FF579A] cursor-pointer' 
              : 'text-slate-400 border-transparent hover:text-[#FF579A] cursor-pointer hover:bg-pink-50/50'
          ]"
          @click="activeTab = tab.name"
        >
          {{ tab.label }}
          <span class="ml-1.5 px-1.5 py-0.5 bg-[#FF579A] text-white rounded-sm text-[8px]">
            {{ getTabCount(tab.name) }}
          </span>
        </button>
      </div>
      
      <!-- Desktop Section Display -->
      <div class="hidden md:flex items-center gap-2 px-4 py-2 border border-b-0 border-slate-100 bg-white rounded-t-sm ml-4 shadow-sm">
        <div class="w-1.5 h-1.5 rounded-full bg-[#FF579A] animate-pulse"></div>
        <span class="text-[10px] font-black text-[#FF579A] uppercase tracking-widest">{{ sectionDisplayName }}</span>
      </div>
    </div>

    <!-- CONTENT AREA -->
    <div :class="[
      'px-4 sm:px-6 py-4 sm:py-6 mx-3 sm:mx-6 mb-4 sm:mb-6',
      section ? 'bg-transparent' : 'bg-transparent'
    ]">
      <!-- Performance Hub (Desktop) -->
      <PerformanceAnalytics v-if="section && activeTab === 'all'" class="hidden lg:grid" :activities="activities" />

      <!-- Content when section exists -->
      <div v-if="section" class="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-8">
        <!-- Dashboard Toolbar for Mobile -->
        <div class="lg:hidden grid grid-cols-2 gap-3 mb-6">
          <button 
            @click="showSimulationModal = true"
            class="w-full bg-gray-900 text-white py-5 px-6 rounded-sm shadow-xl font-bold flex flex-col items-center justify-center group active:scale-[0.98] transition-all relative overflow-hidden border border-white/10"
          >
            <div class="absolute right-0 top-0 w-16 h-16 bg-white/5 rounded-full -mr-8 -mt-8 blur-xl"></div>
            <div class="w-10 h-10 bg-white/10 rounded-sm flex items-center justify-center mb-3">
              <i class="ph ph-terminal-window text-xl"></i>
            </div>
            <span class="text-[10px] font-black uppercase tracking-widest text-center">Training Hub</span>
          </button>

          <button 
            @click="showPerformanceModal = true"
            class="w-full bg-white text-slate-900 py-5 px-6 rounded-sm shadow-xl font-bold flex flex-col items-center justify-center group active:scale-[0.98] transition-all relative overflow-hidden border border-slate-100"
          >
             <div class="w-10 h-10 bg-pink-50 text-[#FF579A] rounded-sm flex items-center justify-center mb-3 border border-pink-100">
              <i class="ph ph-chart-line-up text-xl"></i>
            </div>
            <span class="text-[10px] font-black uppercase tracking-widest text-center">Performance</span>
          </button>
        </div>

        <!-- LEFT PANEL -->
        <div class="flex flex-col gap-4">
          <UpcomingDeadlines 
            :deadlines="upcomingDeadlines" 
            @view="viewActivityDetails" 
          />

          <!-- Consolidated Simulation Console Button -->
          <div class="hidden lg:block bg-gray-900 rounded-sm p-6 text-white shadow-lg transition-all relative overflow-hidden group cursor-pointer border border-white/10" @click="showSimulationModal = true">
            <div class="absolute -right-6 -top-6 w-32 h-32 bg-white/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
            
            <div class="relative z-10">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-12 h-12 bg-white/10 rounded-sm flex items-center justify-center backdrop-blur-md shadow-inner border border-white/10">
                  <i class="ph ph-terminal-window text-2xl"></i>
                </div>
                <div>
                  <h3 class="text-xs font-black uppercase tracking-widest poppins leading-none mb-1 text-white">Training Hub</h3>
                  <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Flight Simulation Console</p>
                </div>
              </div>
              


              <button 
                class="w-full bg-white text-gray-900 py-4 rounded-sm text-[10px] font-black cursor-pointer uppercase tracking-[0.2em] hover:bg-slate-50 transition-all active:scale-[0.97] shadow-xl flex items-center justify-center gap-3 group/btn border border-transparent"
              >
                Access Portal
                <i class="ph ph-arrow-square-out text-lg transition-transform group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5"></i>
              </button>
            </div>
          </div>

        </div>

        <!-- RIGHT PANEL - Activities -->
        <div class="flex flex-col gap-5">
          <TransitionGroup name="list" tag="div" class="space-y-4">
            <ActivityCard 
              v-if="filteredActivities.length > 0"
              v-for="activity in filteredActivities" 
              :key="activity.id"
              :activity="activity"
              @view="viewActivityDetails"
              @compare="openComparisonModal"
            />
          </TransitionGroup>
          <div v-if="filteredActivities.length === 0" class="bg-white border-2 border-dashed border-slate-200 rounded-sm p-12 text-center shadow-sm">
            <div class="w-16 h-16 bg-slate-50 rounded-sm flex items-center justify-center mx-auto mb-4 border border-slate-100 text-slate-300 text-2xl">
              <i class="ph ph-clipboard-text"></i>
            </div>
            <p class="text-slate-500 font-black text-[10px] uppercase tracking-widest">No activities found in this category</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Modal -->
    <ComparisonModal
      :is-open="showComparison"
      :is-loading="isLoadingBooking"
      :error-message="comparisonError"
      :activity="comparisonActivity"
      :booking="comparisonBooking"
      @close="showComparison = false"
    />

    <!-- Simulation Console Modal (Mobile Only) -->
    <Transition name="fade">
      <div v-if="showSimulationModal" class="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="showSimulationModal = false"></div>
        
        <Transition name="slide-up">
          <div v-if="showSimulationModal" class="relative w-full max-w-md bg-white rounded-t-xl sm:rounded-sm shadow-2xl overflow-hidden">
            <!-- Modal Header -->
            <div class="px-6 py-6 border-b border-white/10 flex items-center justify-between bg-gray-900 relative overflow-hidden">
              <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 blur-3xl"></div>
              <div class="relative z-10">
                <h3 class="text-lg font-black text-white poppins uppercase tracking-tight">Simulation Console</h3>
                <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Unified Training Environment</p>
              </div>
              <button @click="showSimulationModal = false" class="relative z-10 w-10 h-10 rounded-sm bg-white/5 flex items-center justify-center text-slate-300 hover:text-white transition-all border border-white/10">
                <i class="ph ph-x text-xl"></i>
              </button>
            </div>

            <!-- Modal Content -->
            <div class="p-6 space-y-5 max-h-[70vh] overflow-y-auto no-scrollbar">
              <!-- Primary Actions Section -->
              <div>
                <p class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-4 px-1">Simulation Modules</p>
                  <div class="grid grid-cols-1 gap-3">
                     <button 
                        @click="startPracticeBooking(); showSimulationModal = false"
                        class="flex items-center gap-4 p-5 bg-gray-50 rounded-sm border border-slate-200 text-left hover:bg-slate-100 transition-all group relative overflow-hidden"
                     >
                        <div class="w-12 h-12 bg-gray-900 rounded-sm flex items-center justify-center text-white shadow-lg group-hover:scale-105 transition-transform">
                          <i class="ph ph-airplane text-2xl"></i>
                        </div>
                        <div class="relative z-10">
                          <span class="block text-xs font-black text-slate-900 uppercase tracking-tight">Practice Booking</span>
                          <span class="block text-[9px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Global Reservation Training</span>
                        </div>
                     </button>
  
                     <button 
                        @click="$router.push('/dcs/dashboard'); showSimulationModal = false"
                        class="flex items-center gap-4 p-5 bg-gray-50 rounded-sm border border-slate-200 text-left hover:bg-slate-100 transition-all group relative overflow-hidden"
                     >
                        <div class="w-12 h-12 bg-gray-900 rounded-sm flex items-center justify-center text-white shadow-lg group-hover:scale-105 transition-transform">
                          <i class="ph ph-monitor text-2xl"></i>
                        </div>
                        <div class="relative z-10">
                          <span class="block text-xs font-black text-slate-900 uppercase tracking-tight">DCS Operations</span>
                          <span class="block text-[9px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Control & Check-in Console</span>
                        </div>
                     </button>
                  </div>
              </div>

              <!-- Logs & Registry Section -->
              <div>
                <p class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-4 px-1">Registry Access</p>
                  <div class="grid grid-cols-2 gap-3">
                    <div @click="$router.push('/student/booking-registry'); showSimulationModal = false" class="p-5 bg-white border border-slate-100 rounded-sm hover:border-gray-900 hover:bg-slate-50 transition-all cursor-pointer group shadow-sm">
                      <div class="w-10 h-10 bg-slate-50 text-slate-400 rounded-sm flex items-center justify-center mb-4 group-hover:bg-gray-900 group-hover:text-white transition-all border border-slate-100">
                        <i class="ph ph-scroll text-xl"></i>
                      </div>
                      <span class="block text-[10px] font-black text-slate-900 uppercase tracking-tighter leading-tight">Booking<br/>Registry</span>
                    </div>
                    
                    <div @click="$router.push('/student/checkin-registry'); showSimulationModal = false" class="p-5 bg-white border border-slate-100 rounded-sm hover:border-gray-900 hover:bg-slate-50 transition-all cursor-pointer group shadow-sm">
                      <div class="w-10 h-10 bg-slate-50 text-slate-400 rounded-sm flex items-center justify-center mb-4 group-hover:bg-gray-900 group-hover:text-white transition-all border border-slate-100">
                        <i class="ph ph-users-four text-xl"></i>
                      </div>
                      <span class="block text-[10px] font-black text-slate-900 uppercase tracking-tighter leading-tight">DCS<br/>Registry</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Modal Footer -->
              <div class="p-4 bg-gray-50 flex justify-center border-t border-gray-100 shrink-0">
                <p class="text-[9px] text-gray-400 font-medium uppercase tracking-widest">Aviation Training System v2.0</p>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>

    <!-- Performance Modal (Mobile Only) -->
    <Transition name="fade">
      <div v-if="showPerformanceModal" class="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 lg:hidden">
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="showPerformanceModal = false"></div>
        
        <Transition name="slide-up">
          <div v-if="showPerformanceModal" class="relative w-full max-w-2xl bg-white rounded-t-xl sm:rounded-sm shadow-2xl overflow-hidden h-[90vh] flex flex-col">
            <!-- Modal Header -->
            <div class="px-6 py-6 border-b border-slate-100 flex items-center justify-between bg-white shrink-0">
              <div>
                <h3 class="text-lg font-black text-slate-900 uppercase tracking-tight">Academic Analytics</h3>
                <p class="text-[9px] text-[#FF579A] font-bold uppercase tracking-widest">Performance Insights</p>
              </div>
              <button @click="showPerformanceModal = false" class="w-10 h-10 rounded-sm bg-slate-50 flex items-center justify-center text-slate-400 hover:text-slate-900 transition-all border border-slate-100">
                <i class="ph ph-x text-xl"></i>
              </button>
            </div>

            <!-- Modal Content -->
            <div class="p-4 overflow-y-auto no-scrollbar flex-1">
               <PerformanceAnalytics :activities="activities" />
            </div>
            
            <div class="p-4 bg-slate-50 border-t border-slate-100 shrink-0 text-center">
               <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Global Academic Tracker</p>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>

  </div>
</template>

<script>
import ComparisonModal from '@/components/common/ComparisonModal.vue';
import UpcomingDeadlines from '@/components/Student/UpcomingDeadlines.vue';
import ActivityCard from '@/components/Student/ActivityCard.vue';
import PerformanceAnalytics from '@/components/Student/PerformanceAnalytics.vue';
import { comparisonService } from '@/services/Student/comparisonService';
import { useUserStore } from '@/stores/user'
import { useModalStore } from '@/stores/modal'
import { useNotificationStore } from '@/stores/notification'
import { useBookingStore } from '@/stores/booking'

export default {
  name: 'StudentDashboard',
  props: {
    section: Object,
    activities: {
      type: Array,
      default: () => []
    }
  },
  setup() {
    const userStore = useUserStore()
    const modalStore = useModalStore()
    const notificationStore = useNotificationStore()
    const bookingStore = useBookingStore()
    return { userStore, modalStore, notificationStore, bookingStore }
  },
  components: {
    ComparisonModal,
    UpcomingDeadlines,
    ActivityCard,
    PerformanceAnalytics
  },
  data() {
    return {
      activeTab: 'all',
      tabs: [
        { name: 'all', label: 'All Activities' },
        { name: 'active', label: 'Active' },
        { name: 'missing', label: 'Missing' },
        { name: 'submitted', label: 'Submitted' },
        { name: 'graded', label: 'Graded' }
      ],
      showComparison: false,
      showSimulationModal: false,
      showPerformanceModal: false,
      comparisonActivity: null,
      comparisonBooking: null,
      isLoadingBooking: false,
      comparisonError: null
    }
  },
  computed: {
    sectionDisplayName() {
      if (!this.section) return 'No section enrolled';
      return `${this.section.section_code} - ${this.section.section_name}`;
    },
    filteredActivities() {
      let filtered = this.activities;
      if (this.activeTab === 'active') {
        filtered = filtered.filter(a => a.is_active && !['submitted', 'graded'].includes(a.status));
      } else if (this.activeTab === 'missing') {
        filtered = filtered.filter(a => this.checkIsOverdue(a));
      } else if (this.activeTab === 'submitted') {
        filtered = filtered.filter(a => a.status === 'submitted');
      } else if (this.activeTab === 'graded') {
        filtered = filtered.filter(a => a.status === 'graded');
      }
      return filtered;
    },
    upcomingDeadlines() {
      return this.activities
        .filter(a => a.due_date && a.is_active && !a.completed && !['submitted', 'graded'].includes(a.status))
        .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
        .slice(0, 5);
    },
    parsedSchedules() {
      if (!this.section?.schedule) return []
      try {
        const schedules = typeof this.section.schedule === 'string' ? JSON.parse(this.section.schedule) : this.section.schedule
        if (Array.isArray(schedules)) return schedules
      } catch (e) {}
      return []
    }
  },
  methods: {
    viewActivityDetails(activityId) {
      this.$router.push(`/student/activity/${activityId}`);
    },
    async startPracticeBooking() {
      const confirmed = await this.modalStore.confirm({
        title: 'Start Practice Booking?',
        message: 'This will start a simulation where you can practice the booking flow.',
        confirmText: 'Start Simulation',
        cancelText: 'Maybe Later'
      });
      if (!confirmed) return;
      this.bookingStore.resetBooking();
      this.bookingStore.setPracticeMode();
      this.notificationStore.success('Practice mode enabled. Happy booking!');
      this.$router.push('/');
    },
    async openComparisonModal(activity) {
      this.showComparison = true;
      this.comparisonActivity = activity;
      this.comparisonBooking = null;
      this.isLoadingBooking = true;
      this.comparisonError = null;

      try {
        const data = await comparisonService.getComparisonData(activity.id, activity.confirmed_booking_id);
        if (data.success) {
          if (data.activity) this.comparisonActivity = data.activity;
          this.comparisonBooking = data.booking;
        } else {
          this.comparisonError = data.error || "Could not find booking data.";
        }
      } catch (error) {
        this.comparisonError = "Failed to connect to the server.";
      } finally {
        this.isLoadingBooking = false;
      }
    },
    getTabCount(tabName) {
      if (tabName === 'active') return this.activities.filter(a => a.is_active && !['submitted', 'graded'].includes(a.status)).length;
      if (tabName === 'missing') return this.activities.filter(a => this.checkIsOverdue(a)).length;
      if (tabName === 'submitted') return this.activities.filter(a => a.status === 'submitted').length;
      if (tabName === 'graded') return this.activities.filter(a => a.status === 'graded').length;
      return this.activities.length;
    },
    checkIsOverdue(activity) {
      if (!activity.due_date) return false;
      const now = new Date();
      const dueDate = new Date(activity.due_date);
      if (typeof activity.due_date === 'string' && activity.due_date.length <= 10) {
        dueDate.setHours(23, 59, 59, 999);
      }
      return now > dueDate && !activity.completed && activity.status !== 'submitted' && activity.status !== 'graded';
    },
    formatTimeOnly(t) {
      if (!t) return ''
      const [h, m] = t.split(':')
      const hour = parseInt(h)
      const ampm = hour >= 12 ? 'PM' : 'AM'
      const h12 = hour % 12 || 12
      return `${h12}:${m} ${ampm}`
    }
  }
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

@keyframes slide-up {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-slide-up {
  animation: slide-up 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

/* Vue Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
@media (min-width: 640px) {
  .slide-up-enter-from, .slide-up-leave-to {
    transform: scale(0.95);
    opacity: 0;
  }
}

/* List Transitions */
.list-enter-active, .list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from, .list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
.list-move {
  transition: transform 0.4s ease;
}
</style>
