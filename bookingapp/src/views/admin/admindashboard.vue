<template>
  <div class="p-6 space-y-6 bg-gray-100 min-h-screen">
    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 border-4 border-[#fe3787] border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-600 poppins">Loading dashboard...</p>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div class="text-right">
        <p class="text-sm text-gray-500 poppins">{{ currentDate }}</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Passengers Card -->
      <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Passengers Today</p>
            <p class="text-3xl font-bold text-[#002D1E] poppins mt-2">{{ stats.passengersToday }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center">
            <i class="ph ph-users text-blue-600 text-2xl"></i>
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <i class="ph" :class="stats.passengerGrowth >= 0 ? 'ph-trend-up text-green-500' : 'ph-trend-down text-red-500'"></i>
          <span :class="stats.passengerGrowth >= 0 ? 'text-green-600' : 'text-red-600'" class="font-medium ml-1">
            {{ stats.passengerGrowth >= 0 ? '+' : '' }}{{ stats.passengerGrowth }}%
          </span>
          <span class="text-gray-400 ml-2">vs yesterday</span>
        </div>
      </div>

      <!-- Revenue Card -->
      <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Total Revenue</p>
            <p class="text-3xl font-bold text-[#fe3787] poppins mt-2">₱{{ formatNumber(stats.totalRevenue) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-pink-100 flex items-center justify-center">
            <i class="ph ph-currency-circle-dollar text-[#fe3787] text-2xl"></i>
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <i class="ph" :class="stats.revenueGrowth >= 0 ? 'ph-trend-up text-green-500' : 'ph-trend-down text-red-500'"></i>
          <span :class="stats.revenueGrowth >= 0 ? 'text-green-600' : 'text-red-600'" class="font-medium ml-1">
            {{ stats.revenueGrowth >= 0 ? '+' : '' }}{{ stats.revenueGrowth }}%
          </span>
          <span class="text-gray-400 ml-2">vs last month</span>
        </div>
      </div>

      <!-- Bookings Card -->
      <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Total Bookings</p>
            <p class="text-3xl font-bold text-[#002D1E] poppins mt-2">{{ stats.totalBookings }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center">
            <i class="ph ph-check-circle text-green-600 text-2xl"></i>
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <span class="text-yellow-600 font-medium">{{ stats.pendingBookings }}</span>
          <span class="text-gray-400 ml-2">pending confirmation</span>
        </div>
      </div>

      <!-- Flights Card -->
      <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Active Flights</p>
            <p class="text-3xl font-bold text-[#002D1E] poppins mt-2">{{ stats.activeFlights }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-purple-100 flex items-center justify-center">
            <i class="ph ph-airplane-tilt text-purple-600 text-2xl"></i>
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <span class="text-purple-600 font-medium">{{ stats.scheduledFlights }}</span>
          <span class="text-gray-400 ml-2">scheduled today</span>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Ticket Sales Chart -->
      <div class="lg:col-span-2 bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-[#002D1E] poppins">Ticket Sales Overview</h3>
          <select 
            v-model="chartPeriod" 
            @change="fetchTicketSales"
            class="border border-gray-300 rounded-[1px] px-3 py-1 text-sm poppins focus:outline-none focus:ring-2 focus:ring-[#fe3787]"
          >
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="90">Last 3 Months</option>
          </select>
        </div>
        <div class="h-80 relative">
          <canvas ref="ticketChartRef"></canvas>
          <div v-if="!hasTicketData" class="absolute inset-0 flex items-center justify-center bg-white/80">
            <p class="text-gray-400 text-sm">No ticket sales data available</p>
          </div>
        </div>
      </div>

      <!-- Revenue Breakdown -->
      <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm">
        <h3 class="text-lg font-bold text-[#002D1E] poppins mb-6">Revenue Breakdown</h3>
        <div class="h-64 relative">
          <canvas ref="revenueChartRef"></canvas>
          <div v-if="revenueTotal === 0" class="absolute inset-0 flex items-center justify-center">
            <p class="text-gray-400 text-sm">No revenue data</p>
          </div>
        </div>
        <div class="mt-6 space-y-3">
          <div v-for="(item, index) in revenueBreakdown" :key="index" class="flex items-center justify-between p-2 hover:bg-gray-50 rounded transition-colors">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: item.color }"></div>
              <span class="text-sm text-gray-600 poppins">{{ item.label }}</span>
            </div>
            <div class="text-right">
              <span class="text-sm font-semibold text-[#002D1E] poppins block">₱{{ formatNumber(item.value) }}</span>
              <span v-if="revenueTotal > 0" class="text-xs text-gray-400">{{ ((item.value / revenueTotal) * 100).toFixed(1) }}%</span>
            </div>
          </div>
          <div class="border-t border-gray-200 pt-3 mt-3">
            <div class="flex items-center justify-between font-semibold">
              <span class="text-[#002D1E] poppins">Total</span>
              <span class="text-[#fe3787] poppins">₱{{ formatNumber(revenueTotal) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Bookings & Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent Bookings -->
      <div class="lg:col-span-2 bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#002D1E] poppins">Recent Bookings</h3>
          <router-link to="/admin/booking/list" class="text-[#fe3787] hover:text-[#fb1873] text-sm font-medium poppins flex items-center gap-1 transition-colors">
            View All <i class="ph ph-arrow-right"></i>
          </router-link>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full text-left" v-if="recentBookings.length > 0">
            <thead class="bg-gray-50 text-gray-600 text-[12px] uppercase font-semibold">
              <tr>
                <th class="px-6 py-4 poppins">Booking ID</th>
                <th class="px-6 py-4 poppins">Passenger</th>
                <th class="px-6 py-4 poppins">Flight</th>
                <th class="px-6 py-4 poppins">Date</th>
                <th class="px-6 py-4 poppins">Amount</th>
                <th class="px-6 py-4 poppins">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="booking in recentBookings" :key="booking.id" class="hover:bg-gray-50/50 transition-colors">
                <td class="px-6 py-4">
                  <span class="font-mono text-sm font-semibold text-[#002D1E]">#{{ booking.id }}</span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#fe3787] to-[#002D1E] flex items-center justify-center text-white font-semibold text-xs">
                      {{ getInitials(booking.passenger) }}
                    </div>
                    <span class="font-medium text-[#002D1E] poppins text-sm">{{ booking.passenger }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span class="text-sm text-gray-600 poppins font-mono">{{ booking.flight }}</span>
                </td>
                <td class="px-6 py-4">
                  <span class="text-sm text-gray-600 poppins">{{ formatDate(booking.date) }}</span>
                </td>
                <td class="px-6 py-4">
                  <span class="text-sm font-semibold text-[#fe3787] poppins">₱{{ formatNumber(booking.amount) }}</span>
                </td>
                <td class="px-6 py-4">
                  <span :class="statusClass(booking.status)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                    {{ booking.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="recentBookings.length === 0" class="p-12 text-center">
          <i class="ph ph-ticket text-4xl text-gray-300 mb-4"></i>
          <p class="text-gray-500 poppins">No recent bookings found</p>
        </div>
      </div>

      <!-- Quick Actions & Alerts -->
      <div class="space-y-6">
        <!-- Quick Actions -->
        <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm">
          <h3 class="text-lg font-bold text-[#002D1E] poppins mb-4">Quick Actions</h3>
          <div class="space-y-3">
            <router-link to="/admin/manage-flight/schedules" class="flex items-center gap-3 p-3 rounded-[1px] hover:bg-gray-50 transition-colors group border border-transparent hover:border-gray-200">
              <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                <i class="ph ph-calendar-plus text-blue-600"></i>
              </div>
              <div>
                <p class="font-medium text-[#002D1E] poppins text-sm">Add Schedule</p>
                <p class="text-xs text-gray-500 poppins">Create new flight schedule</p>
              </div>
            </router-link>
            
            <router-link to="/admin/passenger/list" class="flex items-center gap-3 p-3 rounded-[1px] hover:bg-gray-50 transition-colors group border border-transparent hover:border-gray-200">
              <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center group-hover:bg-green-200 transition-colors">
                <i class="ph ph-user-plus text-green-600"></i>
              </div>
              <div>
                <p class="font-medium text-[#002D1E] poppins text-sm">Add Passenger</p>
                <p class="text-xs text-gray-500 poppins">Register new passenger</p>
              </div>
            </router-link>
            
            <router-link to="/admin/booking/list" class="flex items-center gap-3 p-3 rounded-[1px] hover:bg-gray-50 transition-colors group border border-transparent hover:border-gray-200">
              <div class="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center group-hover:bg-pink-200 transition-colors">
                <i class="ph ph-receipt text-[#fe3787]"></i>
              </div>
              <div>
                <p class="font-medium text-[#002D1E] poppins text-sm">View Bookings</p>
                <p class="text-xs text-gray-500 poppins">Check all reservations</p>
              </div>
            </router-link>
          </div>
        </div>

        <!-- System Alerts -->
        <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm">
          <h3 class="text-lg font-bold text-[#002D1E] poppins mb-4">System Alerts</h3>
          <div class="space-y-3">
            <div v-if="alerts.length === 0" class="text-center py-8 bg-gray-50 rounded-[1px]">
              <i class="ph ph-check-circle text-3xl text-green-500 mb-2"></i>
              <p class="text-sm text-gray-500 poppins">All systems operational</p>
            </div>
            <div v-for="alert in alerts" :key="alert.id" :class="['p-4 rounded-[1px] border-l-4 shadow-sm', alertTypeClass(alert.type)]">
              <div class="flex items-start gap-3">
                <i :class="alertIconClass(alert.type)" class="text-lg mt-0.5"></i>
                <div>
                  <p class="text-sm font-medium poppins">{{ alert.message }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ formatTime(alert.time) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '@/services/admin/api'

Chart.register(...registerables)

// State
const loading = ref(false)
const error = ref(null)
const chartPeriod = ref('7')
const ticketChartRef = ref(null)
const revenueChartRef = ref(null)

// Stats
const stats = ref({
  passengersToday: 0,
  passengerGrowth: 0,
  totalRevenue: 0,
  revenueGrowth: 0,
  totalBookings: 0,
  pendingBookings: 0,
  activeFlights: 0,
  scheduledFlights: 0
})

const recentBookings = ref([])
const alerts = ref([])
const ticketSalesData = ref({
  labels: [],
  data: []
})

const revenueBreakdown = ref([
  { label: 'Ticket Sales', value: 0, color: '#fe3787' },
  { label: 'Add-ons', value: 0, color: '#3b82f6' },
  { label: 'Taxes & Fees', value: 0, color: '#10b981' }
])

// Chart instances
let ticketChartInstance = null
let revenueChartInstance = null

// Computed
const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-PH', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const revenueTotal = computed(() => {
  return revenueBreakdown.value.reduce((sum, item) => sum + item.value, 0)
})

const hasTicketData = computed(() => {
  return ticketSalesData.value.data.some(val => val > 0)
})

// Methods
const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Fetch all dashboard data in parallel with proper error handling
    const responses = await Promise.allSettled([
      api.get('/dashboard/stats/').catch(err => ({ error: err, data: null })),
      api.get('/dashboard/revenue_breakdown/').catch(err => ({ error: err, data: null })),
      api.get('/dashboard/recent_bookings/').catch(err => ({ error: err, data: null })),
      api.get('/dashboard/alerts/').catch(err => ({ error: err, data: null })),
      api.get(`/dashboard/ticket_sales/?days=${chartPeriod.value}`).catch(err => ({ error: err, data: null }))
    ])

    // Handle stats response
    const statsRes = responses[0]
    if (statsRes.value && !statsRes.value.error && statsRes.value.data) {
      const data = statsRes.value.data
      stats.value = {
        passengersToday: data.passengersToday || 0,
        passengerGrowth: data.passengerGrowth || 0,
        totalRevenue: data.totalRevenue || 0,
        revenueGrowth: data.revenueGrowth || 0,
        totalBookings: data.totalBookings || 0,
        pendingBookings: data.pendingBookings || 0,
        activeFlights: data.activeFlights || 0,
        scheduledFlights: data.scheduledFlights || 0
      }
    } else if (statsRes.value?.error) {
      console.error('Stats API error:', statsRes.value.error)
    }

    // Handle revenue breakdown
    const revenueRes = responses[1]
    if (revenueRes.value && !revenueRes.value.error && revenueRes.value.data?.breakdown) {
      const breakdown = revenueRes.value.data.breakdown
      revenueBreakdown.value = [
        { label: 'Ticket Sales', value: breakdown.tickets || 0, color: '#fe3787' },
        { label: 'Add-ons', value: breakdown.addons || 0, color: '#3b82f6' },
        { label: 'Taxes & Fees', value: breakdown.taxes || 0, color: '#10b981' }
      ]
    }

    // Handle recent bookings
    const bookingsRes = responses[2]
    if (bookingsRes.value && !bookingsRes.value.error) {
      recentBookings.value = bookingsRes.value.data || []
    }

    // Handle alerts
    const alertsRes = responses[3]
    if (alertsRes.value && !alertsRes.value.error) {
      alerts.value = alertsRes.value.data || []
    }

    // Handle ticket sales
    const ticketSalesRes = responses[4]
    if (ticketSalesRes.value && !ticketSalesRes.value.error && ticketSalesRes.value.data) {
      ticketSalesData.value = {
        labels: ticketSalesRes.value.data.labels || [],
        data: ticketSalesRes.value.data.data || []
      }
    }

    // Wait for DOM to update then initialize charts
    await nextTick()
    initCharts()
    
  } catch (err) {
    console.error('Dashboard fetch error:', err)
    error.value = 'Failed to load dashboard data. Please try again.'
  } finally {
    loading.value = false
  }
}

const fetchTicketSales = async () => {
  try {
    const res = await api.get(`/dashboard/ticket_sales/?days=${chartPeriod.value}`)
    if (res.data) {
      ticketSalesData.value = {
        labels: res.data.labels || [],
        data: res.data.data || []
      }
      await nextTick()
      updateTicketChart()
    }
  } catch (err) {
    console.error('Ticket sales fetch error:', err)
  }
}

const initCharts = () => {
  // Delay slightly to ensure canvas elements are rendered
  setTimeout(() => {
    initTicketChart()
    initRevenueChart()
  }, 100)
}

const initTicketChart = () => {
  if (!ticketChartRef.value) {
    console.warn('Ticket chart canvas not found')
    return
  }
  
  if (ticketChartInstance) {
    ticketChartInstance.destroy()
    ticketChartInstance = null
  }

  const ctx = ticketChartRef.value.getContext('2d')
  if (!ctx) {
    console.warn('Could not get 2d context for ticket chart')
    return
  }

  const gradient = ctx.createLinearGradient(0, 0, 0, 400)
  gradient.addColorStop(0, 'rgba(254, 55, 135, 0.2)')
  gradient.addColorStop(1, 'rgba(254, 55, 135, 0)')

  const labels = ticketSalesData.value.labels.length > 0 ? ticketSalesData.value.labels : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const data = ticketSalesData.value.data.length > 0 ? ticketSalesData.value.data : [0, 0, 0, 0, 0, 0, 0]

  ticketChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Tickets Sold',
        data: data,
        borderColor: '#fe3787',
        backgroundColor: gradient,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#fe3787',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#002D1E',
          titleColor: '#fff',
          bodyColor: '#fff',
          padding: 12,
          cornerRadius: 4,
          displayColors: false,
          callbacks: {
            label: function(context) {
              return `${context.parsed.y} tickets sold`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#f3f4f6' },
          ticks: {
            stepSize: 1,
            color: '#6b7280'
          }
        },
        x: {
          grid: { display: false },
          ticks: {
            color: '#6b7280'
          }
        }
      }
    }
  })
}

const updateTicketChart = () => {
  if (!ticketChartInstance) {
    initTicketChart()
    return
  }
  
  ticketChartInstance.data.labels = ticketSalesData.value.labels
  ticketChartInstance.data.datasets[0].data = ticketSalesData.value.data
  ticketChartInstance.update('active')
}

const initRevenueChart = () => {
  if (!revenueChartRef.value) {
    console.warn('Revenue chart canvas not found')
    return
  }
  
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
    revenueChartInstance = null
  }

  const ctx = revenueChartRef.value.getContext('2d')
  if (!ctx) {
    console.warn('Could not get 2d context for revenue chart')
    return
  }

  const data = revenueBreakdown.value.map(item => item.value)
  const hasData = data.some(val => val > 0)

  revenueChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: revenueBreakdown.value.map(i => i.label),
      datasets: [{
        data: hasData ? data : [1, 1, 1],
        backgroundColor: hasData ? revenueBreakdown.value.map(i => i.color) : ['#e5e7eb', '#e5e7eb', '#e5e7eb'],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: hasData,
          backgroundColor: '#002D1E',
          bodyColor: '#fff',
          padding: 12,
          cornerRadius: 4,
          callbacks: {
            label: function(context) {
              const value = context.parsed
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((value / total) * 100).toFixed(1)
              return `₱${value.toLocaleString()} (${percentage}%)`
            }
          }
        }
      }
    }
  })
}

// Watch for revenue changes to update chart
watch(revenueBreakdown, () => {
  if (revenueChartInstance) {
    const data = revenueBreakdown.value.map(item => item.value)
    const hasData = data.some(val => val > 0)
    
    revenueChartInstance.data.datasets[0].data = hasData ? data : [1, 1, 1]
    revenueChartInstance.data.datasets[0].backgroundColor = hasData 
      ? revenueBreakdown.value.map(i => i.color) 
      : ['#e5e7eb', '#e5e7eb', '#e5e7eb']
    revenueChartInstance.update()
  }
}, { deep: true })

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return parseFloat(num).toLocaleString('en-PH', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleDateString('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleTimeString('en-PH', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const statusClass = (status) => {
  const classes = {
    'Confirmed': 'bg-green-100 text-green-700 border border-green-200',
    'Pending': 'bg-yellow-100 text-yellow-700 border border-yellow-200',
    'Cancelled': 'bg-red-100 text-red-700 border border-red-200',
    'Completed': 'bg-blue-100 text-blue-700 border border-blue-200',
    'Paid': 'bg-purple-100 text-purple-700 border border-purple-200'
  }
  return classes[status] || 'bg-gray-100 text-gray-600 border border-gray-200'
}

const alertTypeClass = (type) => {
  const classes = {
    'warning': 'bg-yellow-50 border-yellow-400 text-yellow-800',
    'error': 'bg-red-50 border-red-400 text-red-800',
    'info': 'bg-blue-50 border-blue-400 text-blue-800',
    'success': 'bg-green-50 border-green-400 text-green-800'
  }
  return classes[type] || 'bg-gray-50 border-gray-400 text-gray-800'
}

const alertIconClass = (type) => {
  const classes = {
    'warning': 'ph-warning-circle text-yellow-600',
    'error': 'ph-x-circle text-red-600',
    'info': 'ph-info text-blue-600',
    'success': 'ph-check-circle text-green-600'
  }
  return classes[type] || 'ph-bell text-gray-600'
}

// Lifecycle
onMounted(() => {
  fetchDashboardData()
})

onUnmounted(() => {
  // Clean up charts to prevent memory leaks
  if (ticketChartInstance) {
    ticketChartInstance.destroy()
    ticketChartInstance = null
  }
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
    revenueChartInstance = null
  }
})
</script>

<style scoped>
.poppins {
  font-family: 'Poppins', sans-serif;
}

/* Custom scrollbar for tables */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}
.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* Smooth transitions */
.transition-shadow {
  transition: box-shadow 0.2s ease-in-out;
}

/* Loading animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>