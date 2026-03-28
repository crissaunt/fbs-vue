<template class="">
  <div class="p-8 min-w-7xl mx-auto">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
      <div>
        <h1 class="text-4xl font-black text-gray-900 tracking-tight">Tasks & Activities</h1>
        <p class="text-gray-500 mt-1 font-medium italic">Manage and track your flight booking assignments.</p>
      </div>

      <!-- Filters -->
      <div class="flex bg-gray-100 p-1.5 rounded-2xl shadow-inner">
        <button 
          v-for="f in filters" 
          :key="f.id"
          @click="activeFilter = f.id"
          :class="[
            'px-6 py-2.5 rounded-xl text-xs font-black transition-all uppercase tracking-widest',
            activeFilter === f.id 
              ? 'bg-white text-pink-600 shadow-sm scale-105' 
              : 'text-gray-500 hover:text-gray-800'
          ]"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- Activity List -->
    <div v-if="filteredActivities.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
      <div 
        v-for="activity in filteredActivities" 
        :key="activity.id"
        class="bg-white rounded-3xl border border-gray-100 shadow-sm hover:shadow-xl transition-all group overflow-hidden flex flex-col"
      >
        <!-- Card Header -->
        <div :class="[
          'p-6 text-white relative',
          activity.is_active ? 'bg-gradient-to-br from-pink-500 to-rose-600' : 'bg-gray-400'
        ]">
          <div class="absolute -right-6 -top-6 w-24 h-24 bg-white/10 rounded-full blur-xl group-hover:scale-150 transition-transform"></div>
          
          <div class="relative z-10">
            <div class="flex justify-between items-start mb-4">
              <span class="px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-[10px] font-black uppercase tracking-tighter">
                {{ activity.status || 'Assigned' }}
              </span>
              <span v-if="activity.grade !== null" class="text-2xl font-black">
                {{ activity.grade }}<span class="text-xs opacity-60">/{{ activity.total_points }}</span>
              </span>
              <span v-else-if="activity.status === 'graded' || activity.status === 'submitted'" class="px-2 py-1 bg-yellow-400/20 text-yellow-100 border border-yellow-400/30 rounded text-[10px] font-black uppercase tracking-widest flex items-center shadow-inner">
                Pending Release
              </span>
            </div>
            <h3 class="text-xl font-bold leading-tight line-clamp-2">{{ activity.title }}</h3>
          </div>
        </div>

        <!-- Card Body -->
        <div class="p-6 flex-1 flex flex-col">
          <div class="space-y-4 mb-8">
            <div class="flex items-center gap-3 text-sm font-medium text-gray-600">
              <span class="w-8 h-8 bg-gray-50 rounded-lg flex items-center justify-center text-lg">📅</span>
              <div>
                <p class="text-[10px] text-gray-400 font-bold uppercase leading-none mb-1">Due Date</p>
                <p class="text-gray-800">{{ formatDate(activity.due_date) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3 text-sm font-medium text-gray-600">
              <span class="w-8 h-8 bg-gray-50 rounded-lg flex items-center justify-center text-lg">✈️</span>
              <div>
                <p class="text-[10px] text-gray-400 font-bold uppercase leading-none mb-1">Route</p>
                <p class="text-gray-800">{{ activity.required_origin }} ➔ {{ activity.required_destination }}</p>
              </div>
            </div>
          </div>

          <router-link 
            :to="`/student/activity/${activity.id}`"
            class="mt-auto w-full py-4 rounded-2xl bg-gray-50 border border-gray-100 text-center font-bold text-gray-800 group-hover:bg-pink-600 group-hover:text-white group-hover:border-pink-500 transition-all shadow-sm"
          >
            START ACTIVITY
          </router-link>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-24 bg-gray-50 rounded-[40px] border-2 border-dashed border-gray-200">
      <div class="text-6xl mb-6 grayscale opacity-30">📋</div>
      <h3 class="text-xl font-bold text-gray-400">No tasks found for this category.</h3>
      <p class="text-gray-400 mt-1 font-medium">Keep up the great work!</p>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'StudentTasks',
  props: {
    activities: Array
  },
  setup(props) {
    const activeFilter = ref('all')
    const filters = [
      { id: 'all', label: 'All' },
      { id: 'active', label: 'Active' },
      { id: 'submitted', label: 'Done' }
    ]

    const filteredActivities = computed(() => {
      let list = props.activities || []
      if (activeFilter.value === 'active') {
        return list.filter(a => a.is_active && !['submitted', 'graded'].includes(a.status))
      }
      if (activeFilter.value === 'submitted') {
        return list.filter(a => ['submitted', 'graded'].includes(a.status))
      }
      return list
    })

    const formatDate = (d) => {
      if (!d) return 'N/A'
      return new Date(d).toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      })
    }

    return {
      activeFilter,
      filters,
      filteredActivities,
      formatDate
    }
  }
}
</script>
