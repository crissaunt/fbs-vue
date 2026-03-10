<template>
  <div class="flex-1 flex flex-col bg-gray-50 overflow-y-auto">
    <div class="bg-pink-500 mx-6 mt-5 px-8 py-12 rounded-lg shadow-lg relative overflow-hidden">
      <!-- Background decoration -->
      <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
      <div class="absolute -left-10 -bottom-10 w-32 h-32 bg-pink-400/20 rounded-full blur-xl"></div>
      
      <div class="relative z-10">
        <h1 class="text-white text-3xl font-light tracking-wide drop-shadow-sm">
          {{ sectionDisplayName }}
        </h1>
        <div class="flex flex-wrap items-center gap-4 mt-3">
          <p class="text-white/90 text-sm font-medium flex items-center gap-1.5 bg-white/10 px-3 py-1 rounded-full border border-white/10 backdrop-blur-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {{ filteredActivities.length }} {{ filteredActivities.length === 1 ? 'activity' : 'activities' }}
          </p>
          
          <!-- New Schedule Display -->
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
    </div>

    <!-- TABS - Only show if section exists -->
    <div v-if="section" class="bg-white mx-6 mt-5 flex gap-0 border-b border-gray-200 rounded-t-lg">
      <button 
        v-for="tab in tabs" 
        :key="tab.name"
        :class="[
          'px-5 py-3 text-xs font-semibold transition-all uppercase tracking-wide border-b-[3px]',
          activeTab === tab.name 
            ? 'text-pink-600 border-pink-600 bg-pink-50/50' 
            : 'text-gray-600 border-transparent hover:text-pink-600 hover:bg-pink-50/30'
        ]"
        @click="activeTab = tab.name"
      >
        {{ tab.label }}
        <span class="ml-1.5 px-1.5 py-0.5 bg-gray-200 text-gray-700 rounded-full text-[9px]">
          {{ getTabCount(tab.name) }}
        </span>
      </button>
    </div>

    <!-- CONTENT AREA -->
    <div :class="[
      'px-6 py-6 mx-6 mb-6',
      section ? 'bg-white rounded-b-lg shadow-sm' : 'bg-transparent'
    ]">
      <!-- Content when section exists -->
      <div v-if="section" class="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
        <!-- LEFT PANEL -->
        <div class="flex flex-col gap-4">
          <UpcomingDeadlines 
            :deadlines="upcomingDeadlines" 
            @view="viewActivityDetails" 
          />

          <!-- Practice Booking Button -->
          <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-5 text-white shadow-lg hover:shadow-xl transition-all">
            <h3 class="text-sm font-bold mb-1">Practice Booking</h3>
            <p class="text-[10px] opacity-80 mb-3">Try the booking system without affecting your grade.</p>
            <button 
              @click="startPracticeBooking"
              class="w-full bg-white text-blue-600 px-4 py-2 rounded-lg text-xs font-bold hover:bg-blue-50 transition-colors"
            >
              Start Simulation
            </button>
          </div>

          <StudentSectionInfo 
            :section="section" 
            :total-activities="activities.length" 
            :active-activities="activeActivitiesCount" 
          />
        </div>

        <!-- RIGHT PANEL - Activities -->
        <div class="flex flex-col gap-5">
          <ActivityCard 
            v-if="filteredActivities.length > 0"
            v-for="activity in filteredActivities" 
            :key="activity.id"
            :activity="activity"
            @view="viewActivityDetails"
            @compare="openComparisonModal"
          />
          <div v-else class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-10 text-center">
            <p class="text-gray-600 font-semibold text-sm">No activities found</p>
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
  </div>
</template>

<script>
import ComparisonModal from '@/components/common/ComparisonModal.vue';
import UpcomingDeadlines from '@/components/Student/UpcomingDeadlines.vue';
import StudentSectionInfo from '@/components/Student/StudentSectionInfo.vue';
import ActivityCard from '@/components/Student/ActivityCard.vue';
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
    StudentSectionInfo,
    ActivityCard
  },
  data() {
    return {
      activeTab: 'all',
      tabs: [
        { name: 'all', label: 'All Activities' },
        { name: 'active', label: 'Active' },
        { name: 'assigned', label: 'Assigned' },
        { name: 'submitted', label: 'Submitted' }
      ],
      showComparison: false,
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
        filtered = filtered.filter(a => a.is_active === true);
      } else if (this.activeTab === 'assigned') {
        filtered = filtered.filter(a => a.status === 'assigned');
      } else if (this.activeTab === 'submitted') {
        filtered = filtered.filter(a => ['submitted', 'graded'].includes(a.status));
      }
      return filtered;
    },
    activeActivitiesCount() {
      return this.activities.filter(a => a.is_active === true).length;
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
      if (tabName === 'active') return this.activeActivitiesCount;
      if (tabName === 'assigned') return this.activities.filter(a => a.status === 'assigned').length;
      if (tabName === 'submitted') return this.activities.filter(a => ['submitted', 'graded'].includes(a.status)).length;
      return this.activities.length;
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
