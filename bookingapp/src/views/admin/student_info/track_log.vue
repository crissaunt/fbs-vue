<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <button 
          @click="exportLogs" 
          class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px]"
        >
          <i class="ph ph-export"></i> Export
        </button>
        <button 
          @click="refreshLogs" 
          class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px]"
        >
          <i class="ph ph-arrows-clockwise"></i> Refresh
        </button>
        <button 
          @click="clearAllLogs" 
          class="bg-red-500 text-white px-4 py-2 flex items-center gap-2 hover:bg-red-600 font-semibold poppins text-[14px] rounded-[1px]"
        >
          <i class="ph ph-trash"></i> Clear All
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Total Logs</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ stats.total }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <i class="ph ph-list-dashes text-blue-600 text-xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Today's Activity</p>
            <p class="text-2xl font-bold text-green-600 poppins">{{ stats.today }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
            <i class="ph ph-calendar-check text-green-600 text-xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Unique Users</p>
            <p class="text-2xl font-bold text-purple-600 poppins">{{ stats.uniqueUsers }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
            <i class="ph ph-users text-purple-600 text-xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">This Week</p>
            <p class="text-2xl font-bold text-orange-600 poppins">{{ stats.thisWeek }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center">
            <i class="ph ph-chart-line-up text-orange-600 text-xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6 text-[14px]">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="relative flex-1">
          <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by user, action, or keyword..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedUser" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="fetchLogs"
        >
          <option value="">All Users</option>
          <option v-for="user in uniqueUsersList" :key="user.id" :value="user.id">
            {{ user.username }}
          </option>
        </select>

        <input 
          v-model="dateFrom" 
          type="date" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px]"
          @change="fetchLogs"
        />
        
        <input 
          v-model="dateTo" 
          type="date" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px]"
          @change="fetchLogs"
        />

        <button 
          @click="clearFilters" 
          class="text-white px-4 py-2 border bg-[#fe3787] rounded-[1px] hover:bg-[#fb1873] font-medium poppins text-[14px]"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Activity Timeline -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-[#002D1E] poppins">Activity Timeline</h3>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500 poppins">Auto-refresh:</span>
          <button 
            @click="toggleAutoRefresh" 
            :class="[
              'px-3 py-1 rounded-[1px] text-sm font-medium poppins transition-colors',
              autoRefresh ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
            ]"
          >
            {{ autoRefresh ? 'ON' : 'OFF' }}
          </button>
        </div>
      </div>

      <div class="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
        <div 
          v-for="(log, index) in paginatedLogs" 
          :key="log.id" 
          class="p-4 hover:bg-gray-50/50 transition-colors"
        >
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <div :class="[
                'w-10 h-10 rounded-full flex items-center justify-center',
                getActionColor(log.action)
              ]">
                <i :class="getActionIcon(log.action)" class="text-white text-lg"></i>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <p class="text-sm font-semibold text-[#002D1E] poppins">
                  {{ log.user?.username || 'Unknown User' }}
                </p>
                <span class="text-xs text-gray-400 poppins">
                  {{ formatDateTime(log.timestamp) }}
                </span>
              </div>
              <p class="text-sm text-gray-600 poppins break-words">
                {{ log.action }}
              </p>
              <div class="flex items-center gap-4 mt-2">
                <span class="text-xs text-gray-400 poppins flex items-center gap-1">
                  <i class="ph ph-clock"></i>
                  {{ timeAgo(log.timestamp) }}
                </span>
                <span class="text-xs text-gray-400 poppins flex items-center gap-1">
                  <i class="ph ph-hash"></i>
                  Log #{{ log.id }}
                </span>
              </div>
            </div>
            <div class="flex-shrink-0">
              <button 
                @click="deleteLog(log.id)" 
                class="text-gray-400 hover:text-red-500 transition-colors p-1"
                title="Delete Log"
              >
                <i class="ph ph-trash text-lg"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="logs.length === 0 && !loading" class="p-12 text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <i class="ph ph-clipboard-text text-2xl text-gray-400"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No activity logs found</h3>
          <p class="text-gray-500 poppins">User actions will be recorded here</p>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="p-12 text-center">
          <i class="ph ph-spinner animate-spin text-4xl text-[#fe3787]"></i>
          <p class="mt-2 text-gray-500 poppins">Loading activity logs...</p>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="filteredLogs.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredLogs.length }} logs
          </div>
          <div class="flex gap-1">
            <button 
              @click="prevPage" 
              :disabled="currentPage === 1"
              class="px-3 py-1 border border-gray-300 rounded-[1px] text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed poppins"
            >
              Prev
            </button>
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="goToPage(page)"
              :disabled="page === '...'"
              :class="[
                'px-3 py-1 border rounded-[1px] text-sm poppins',
                page === '...' ? 'border-gray-300 cursor-default' : '',
                currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
              class="px-3 py-1 border border-gray-300 rounded-[1px] text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed poppins"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Summary Chart -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <!-- Top Users -->
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-lg font-semibold text-[#002D1E] poppins mb-4">Most Active Users</h3>
        <div class="space-y-3">
          <div 
            v-for="(user, index) in topUsers" 
            :key="user.user__id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-[1px]"
          >
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-[#fe3787] text-white flex items-center justify-center text-sm font-bold">
                {{ index + 1 }}
              </div>
              <span class="font-medium text-[#002D1E] poppins">{{ user.user__username }}</span>
            </div>
            <span class="text-sm font-semibold text-[#fe3787] poppins">{{ user.count }} actions</span>
          </div>
          <div v-if="topUsers.length === 0" class="text-center text-gray-500 py-4">
            No activity data available
          </div>
        </div>
      </div>

      <!-- Recent Actions Breakdown -->
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-lg font-semibold text-[#002D1E] poppins mb-4">Action Types</h3>
        <div class="space-y-3">
          <div 
            v-for="(action, index) in actionBreakdown" 
            :key="index"
            class="flex items-center justify-between"
          >
            <div class="flex items-center gap-3 flex-1">
              <div :class="[
                'w-3 h-3 rounded-full',
                getActionColor(action.action)
              ]"></div>
              <span class="text-sm text-gray-600 poppins truncate">{{ truncateAction(action.action) }}</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-[#fe3787] h-2 rounded-full transition-all duration-300"
                  :style="{ width: (action.count / stats.total * 100) + '%' }"
                ></div>
              </div>
              <span class="text-sm font-semibold text-[#002D1E] poppins w-8 text-right">{{ action.count }}</span>
            </div>
          </div>
          <div v-if="actionBreakdown.length === 0" class="text-center text-gray-500 py-4">
            No action data available
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import api from '@/services/admin/api'

// Reactive state
const logs = ref([])
const loading = ref(false)
const autoRefresh = ref(false)
let refreshInterval = null

// Filters
const searchQuery = ref('')
const selectedUser = ref('')
const dateFrom = ref('')
const dateTo = ref('')

// Pagination
const currentPage = ref(1)
const itemsPerPage = 20

// Stats
const stats = ref({
  total: 0,
  today: 0,
  uniqueUsers: 0,
  thisWeek: 0
})

const uniqueUsersList = ref([])
const topUsers = ref([])
const actionBreakdown = ref([])

// Computed
const filteredLogs = computed(() => {
  let filtered = logs.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(log => 
      log.action?.toLowerCase().includes(query) ||
      log.user?.username?.toLowerCase().includes(query)
    )
  }
  
  if (selectedUser.value) {
    filtered = filtered.filter(log => log.user?.id === parseInt(selectedUser.value))
  }
  
  if (dateFrom.value) {
    const fromDate = new Date(dateFrom.value)
    filtered = filtered.filter(log => new Date(log.timestamp) >= fromDate)
  }
  
  if (dateTo.value) {
    const toDate = new Date(dateTo.value)
    toDate.setHours(23, 59, 59)
    filtered = filtered.filter(log => new Date(log.timestamp) <= toDate)
  }
  
  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const totalPages = computed(() => Math.ceil(filteredLogs.value.length / itemsPerPage))

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredLogs.value.slice(start, end)
})

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredLogs.value.length))

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 5) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 2) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 3; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      pages.push(current - 1)
      pages.push(current)
      pages.push(current + 1)
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

// Methods
const fetchLogs = async () => {
  loading.value = true
  try {
    const params = {}
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    
    const response = await api.get('/tracklogs/', { params })
    logs.value = response.data
    
    calculateStats()
    extractUniqueUsers()
    calculateTopUsers()
    calculateActionBreakdown()
  } catch (err) {
    console.error('Fetch error:', err)
    // Fallback: if API doesn't exist, show empty state
    logs.value = []
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
  
  stats.value.total = logs.value.length
  stats.value.today = logs.value.filter(log => new Date(log.timestamp) >= today).length
  stats.value.thisWeek = logs.value.filter(log => new Date(log.timestamp) >= weekAgo).length
  
  const uniqueUserIds = new Set(logs.value.map(log => log.user?.id).filter(Boolean))
  stats.value.uniqueUsers = uniqueUserIds.size
}

const extractUniqueUsers = () => {
  const usersMap = new Map()
  logs.value.forEach(log => {
    if (log.user && !usersMap.has(log.user.id)) {
      usersMap.set(log.user.id, log.user)
    }
  })
  uniqueUsersList.value = Array.from(usersMap.values())
}

const calculateTopUsers = () => {
  const userCounts = {}
  logs.value.forEach(log => {
    const userId = log.user?.id
    const username = log.user?.username
    if (userId) {
      if (!userCounts[userId]) {
        userCounts[userId] = { user__id: userId, user__username: username, count: 0 }
      }
      userCounts[userId].count++
    }
  })
  
  topUsers.value = Object.values(userCounts)
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
}

const calculateActionBreakdown = () => {
  const actionCounts = {}
  logs.value.forEach(log => {
    const action = log.action
    if (!actionCounts[action]) {
      actionCounts[action] = { action, count: 0 }
    }
    actionCounts[action].count++
  })
  
  actionBreakdown.value = Object.values(actionCounts)
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
}

const getActionIcon = (action) => {
  const actionLower = action?.toLowerCase() || ''
  if (actionLower.includes('login')) return 'ph-sign-in'
  if (actionLower.includes('logout')) return 'ph-sign-out'
  if (actionLower.includes('create') || actionLower.includes('add')) return 'ph-plus-circle'
  if (actionLower.includes('update') || actionLower.includes('edit')) return 'ph-pencil-simple'
  if (actionLower.includes('delete')) return 'ph-trash'
  if (actionLower.includes('book')) return 'ph-ticket'
  if (actionLower.includes('pay')) return 'ph-credit-card'
  if (actionLower.includes('check')) return 'ph-check-circle'
  if (actionLower.includes('export')) return 'ph-export'
  if (actionLower.includes('import')) return 'ph-import'
  return 'ph-activity'
}

const getActionColor = (action) => {
  const actionLower = action?.toLowerCase() || ''
  if (actionLower.includes('login')) return 'bg-green-500'
  if (actionLower.includes('logout')) return 'bg-gray-500'
  if (actionLower.includes('create') || actionLower.includes('add')) return 'bg-blue-500'
  if (actionLower.includes('update') || actionLower.includes('edit')) return 'bg-yellow-500'
  if (actionLower.includes('delete')) return 'bg-red-500'
  if (actionLower.includes('book')) return 'bg-purple-500'
  if (actionLower.includes('pay')) return 'bg-pink-500'
  if (actionLower.includes('check')) return 'bg-teal-500'
  return 'bg-[#fe3787]'
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const timeAgo = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)
  
  let interval = seconds / 31536000
  if (interval > 1) return Math.floor(interval) + ' years ago'
  
  interval = seconds / 2592000
  if (interval > 1) return Math.floor(interval) + ' months ago'
  
  interval = seconds / 86400
  if (interval > 1) return Math.floor(interval) + ' days ago'
  
  interval = seconds / 3600
  if (interval > 1) return Math.floor(interval) + ' hours ago'
  
  interval = seconds / 60
  if (interval > 1) return Math.floor(interval) + ' minutes ago'
  
  return 'Just now'
}

const truncateAction = (action) => {
  if (!action) return ''
  return action.length > 50 ? action.substring(0, 50) + '...' : action
}

const deleteLog = async (id) => {
  if (!confirm('Are you sure you want to delete this log entry?')) return
  
  try {
    await api.delete(`/tracklogs/${id}/`)
    logs.value = logs.value.filter(log => log.id !== id)
    calculateStats()
    calculateTopUsers()
    calculateActionBreakdown()
  } catch (err) {
    console.error('Delete error:', err)
    alert('Failed to delete log entry')
  }
}

const clearAllLogs = async () => {
  if (!confirm('WARNING: This will permanently delete ALL log entries. Are you sure?')) return
  
  try {
    await api.delete('/tracklogs/clear-all/')
    logs.value = []
    calculateStats()
    topUsers.value = []
    actionBreakdown.value = []
    alert('All logs cleared successfully')
  } catch (err) {
    console.error('Clear error:', err)
    alert('Failed to clear logs')
  }
}

const exportLogs = async () => {
  try {
    const response = await api.get('/tracklogs/export/', {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `activity_logs_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error('Export error:', err)
    alert('Failed to export logs')
  }
}

const refreshLogs = () => {
  fetchLogs()
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    refreshInterval = setInterval(fetchLogs, 30000) // Refresh every 30 seconds
  } else {
    clearInterval(refreshInterval)
  }
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedUser.value = ''
  dateFrom.value = ''
  dateTo.value = ''
  currentPage.value = 1
  fetchLogs()
}

// Debounce search
let searchTimeout = null
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
  }, 500)
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const goToPage = (page) => {
  if (page !== '...') currentPage.value = page
}

// Watch
watch([searchQuery], () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(() => {
  fetchLogs()
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style scoped>
.poppins {
  font-family: 'Poppins', sans-serif;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Custom scrollbar for timeline */
.max-h-\[600px\]::-webkit-scrollbar {
  width: 6px;
}
.max-h-\[600px\]::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.max-h-\[600px\]::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}
.max-h-\[600px\]::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>