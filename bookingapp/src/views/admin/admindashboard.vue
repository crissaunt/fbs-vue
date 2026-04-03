<template>
  <div class="p-0.5 space-y-2 bg-gray-100 min-h-screen">
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

    <!-- Glassmorphism Welcome Header -->
    <div class="relative overflow-hidden p-3 rounded-[1px] border border-white/20 shadow-2xl bg-gradient-to-br from-[#002D1E] to-[#013d29] mb-2 group">
      <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
      <div class="absolute -right-20 -top-20 w-64 h-64 bg-[#fe3787] rounded-full blur-[100px] opacity-20 group-hover:opacity-30 transition-opacity"></div>
      
      <div class="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/10 mb-4">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          </div>
          <h1 class="text-xl font-black text-white poppins tracking-tight mb-2">
            {{ greeting }}, <span class="text-[#fe3787] drop-shadow-sm font-black italic">Administrator</span>
          </h1>
          <p class="text-gray-300 poppins text-sm max-w-md">Welcome to your command center. Flight operations and booking metrics are currently optimized.</p>
        </div>
        
        <div class="flex items-center gap-3 bg-black/20 backdrop-blur-xl p-3 rounded-[1px] border border-white/10 shadow-inner">
          <div class="w-12 h-12 rounded-[1px] bg-[#fe3787] flex items-center justify-center shadow-lg">
            <i class="ph ph-calendar-check text-white text-2xl"></i>
          </div>
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-400 tracking-widest poppins mb-1">Session Data</p>
            <p class="text-sm font-black text-white poppins leading-none">{{ currentDate }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-2 mb-2">
      <!-- Passengers Card (LMS & Flight) -->
      <div v-if="userRole === 'superadmin' || userRole === 'lms_admin' || userRole === 'flight_admin'" class="group bg-white p-2.5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-blue-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Passenger Traffic</p>
            <p class="text-xl font-black text-[#002D1E] poppins mt-1 tracking-tighter">{{ stats.passengersToday }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-blue-50 flex items-center justify-center border border-blue-100 shadow-inner">
            <i class="ph ph-student text-blue-600 text-xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins">
          <div :class="stats.passengerGrowth >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'" class="flex items-center gap-1 px-2 py-1 rounded-full font-bold">
            <i class="ph" :class="stats.passengerGrowth >= 0 ? 'ph-trend-up' : 'ph-trend-down'"></i>
            {{ stats.passengerGrowth >= 0 ? '+' : '' }}{{ stats.passengerGrowth }}%
          </div>
          <span class="text-gray-400 ml-2 font-medium">vs yesterday</span>
        </div>
      </div>

      <!-- Revenue Card (Flight & Superadmin) -->
      <div v-if="userRole === 'superadmin' || userRole === 'flight_admin'" class="group bg-[#002D1E] p-2.5 border border-[#002D1E] rounded-[1px] shadow-sm hover:shadow-2xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-[#fe3787]/10 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between text-white">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-400 tracking-[0.2em] poppins">Net Revenue</p>
            <p class="text-xl font-black text-[#fe3787] poppins mt-1 tracking-tighter">₱{{ formatNumber(stats.totalRevenue) }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-white/5 flex items-center justify-center border border-white/10 shadow-inner backdrop-blur-sm">
            <i class="ph ph-hand-coins text-[#fe3787] text-xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins">
          <div :class="stats.revenueGrowth >= 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'" class="flex items-center gap-1 px-2 py-1 rounded-full font-bold border border-white/10">
            <i class="ph" :class="stats.revenueGrowth >= 0 ? 'ph-trend-up' : 'ph-trend-down'"></i>
            {{ stats.revenueGrowth >= 0 ? '+' : '' }}{{ stats.revenueGrowth }}%
          </div>
          <span class="text-gray-400 ml-2 font-medium">vs last month</span>
        </div>
      </div>

      <!-- Bookings Card (Flight & Superadmin) -->
      <div v-if="userRole === 'superadmin' || userRole === 'flight_admin'" class="group bg-white p-2.5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-green-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between text-[#002D1E]">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Total Bookings</p>
            <p class="text-xl font-black poppins mt-1 tracking-tighter">{{ stats.totalBookings }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-green-50 flex items-center justify-center border border-green-100 shadow-inner">
            <i class="ph ph-ticket text-green-600 text-xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins font-bold">
          <span class="text-[#fe3787] bg-pink-50 px-2 py-1 rounded-full border border-pink-100">{{ stats.pendingBookings }}</span>
          <span class="text-gray-400 ml-2 font-medium uppercase tracking-wider text-[9px]">Awaiting Confirmation</span>
        </div>
      </div>

      <!-- Flights Card (Flight & Superadmin) -->
      <div v-if="userRole === 'superadmin' || userRole === 'flight_admin'" class="group bg-white p-2.5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-purple-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between text-[#002D1E]">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Active Flights</p>
            <p class="text-xl font-black poppins mt-1 tracking-tighter">{{ stats.activeFlights }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-purple-50 flex items-center justify-center border border-purple-100 shadow-inner">
            <i class="ph ph-airplane text-purple-600 text-xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins font-bold">
          <span class="text-purple-600 bg-purple-50 px-2 py-1 rounded-full border border-purple-100">{{ stats.scheduledFlights }}</span>
          <span class="text-gray-400 ml-2 font-medium uppercase tracking-wider text-[9px]">Schedules Today</span>
        </div>
      </div>

      <!-- Check-ins Card (Flight & Superadmin) -->
      <div v-if="userRole === 'superadmin' || userRole === 'flight_admin'" class="group bg-white p-2.5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-pink-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between text-[#002D1E]">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Check-ins</p>
            <p class="text-xl font-black poppins mt-1 tracking-tighter">{{ stats.checkins }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-pink-50 flex items-center justify-center border border-pink-100 shadow-inner">
            <i class="ph ph-user-check text-[#fe3787] text-xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins font-bold">
          <router-link to="/admin/passenger/check-ins" class="text-[#fe3787] hover:underline flex items-center gap-1">
            View Registry <i class="ph ph-arrow-right text-[10px]"></i>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Main Charts Section (Flight & Superadmin) -->
    <div v-if="userRole === 'superadmin' || userRole === 'flight_admin'" class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
      <!-- Main Sales Chart -->
      <div class="lg:col-span-8 bg-white p-3 border border-gray-200 rounded-[1px] shadow-sm relative overflow-hidden group">
        <div class="absolute top-0 left-0 w-1 h-full bg-[#fe3787] opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="flex items-center justify-between mb-8">
          <div>
            <h3 class="text-lg font-black text-[#002D1E] poppins tracking-tight">Revenue Stream</h3>
            <p class="text-xs text-gray-400 poppins uppercase tracking-wider font-bold">Ticket sales performance</p>
          </div>
          <select 
            v-model="chartPeriod" 
            @change="fetchTicketSales"
            class="bg-gray-50 border border-gray-200 rounded-[1px] px-4 py-2 text-xs font-bold uppercase tracking-widest poppins focus:outline-none focus:ring-2 focus:ring-[#fe3787] cursor-pointer"
          >
            <option value="1">Today</option>
            <option value="7">Week</option>
            <option value="30">Month</option>
            <option value="365">Year</option>
          </select>
        </div>
        <div class="h-[200px] relative">
          <canvas ref="ticketChartRef"></canvas>
          <div v-if="!hasTicketData && !loading" class="absolute inset-0 flex flex-col items-center justify-center bg-white/90 backdrop-blur-sm">
             <i class="ph ph-chart-line-up text-3xl text-gray-200 mb-4"></i>
             <p class="text-gray-400 text-xs font-bold uppercase tracking-[0.2em]">Gathering data...</p>
          </div>
        </div>
      </div>

      <!-- Fee Distribution -->
      <div class="lg:col-span-4 bg-white p-3 border border-gray-200 rounded-[1px] shadow-sm relative group overflow-hidden flex flex-col">
          <div class="absolute top-0 right-0 w-32 h-32 bg-purple-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110"></div>
          <h3 class="text-sm font-black text-[#002D1E] poppins uppercase tracking-widest mb-6 relative">Fee Distribution</h3>
          <div class="flex-grow flex items-center justify-center min-h-[200px]">
            <canvas ref="revenueChartRef"></canvas>
          </div>
          <div class="mt-6 space-y-2 relative">
            <div v-for="(item, index) in revenueBreakdown" :key="index" class="flex items-center justify-between text-[11px] font-bold uppercase poppins">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :style="{ background: item.color }"></span>
                <span class="text-gray-400">{{ item.label }}</span>
              </div>
              <span class="text-[#002D1E]">₱{{ formatNumber(item.value) }}</span>
            </div>
          </div>
      </div>
    </div>

    <!-- Revenue Performance by Route (Flight & Superadmin) -->
    <div v-if="userRole === 'superadmin' || userRole === 'flight_admin'" class="grid grid-cols-1 gap-6 mb-8">
       <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm relative group overflow-hidden">
          <div class="absolute top-0 left-0 w-1 h-full bg-[#002D1E] opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <h3 class="text-sm font-black text-[#002D1E] poppins uppercase tracking-widest mb-6 relative">Revenue Performance by Route</h3>
          <div class="h-64 relative">
             <canvas ref="revenueByRouteChartRef"></canvas>
          </div>
       </div>
    </div>

    <!-- Recent Bookings Ledger (Flight & Superadmin) -->
    <div v-if="userRole === 'superadmin' || userRole === 'flight_admin'" class="grid grid-cols-1 gap-6 mb-8">
       <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden flex flex-col">
         <div class="p-6 border-b border-gray-200 flex items-center justify-between">
           <h3 class="text-lg font-black text-[#002D1E] poppins flex items-center gap-2">
             <i class="ph ph-list-checks text-[#fe3787]"></i>
             Recent Bookings
           </h3>
           <router-link to="/admin/booking/list" class="text-[#fe3787] hover:bg-pink-50 px-3 py-1 rounded-[1px] text-xs font-black uppercase tracking-widest poppins flex items-center gap-2 transition-all border border-transparent hover:border-pink-100">
             View All <i class="ph ph-arrow-right"></i>
           </router-link>
         </div>
         <div class="overflow-x-auto">
           <table class="w-full text-left" v-if="recentBookings.length > 0">
             <thead class="bg-gray-50 text-gray-600 text-[10px] uppercase font-bold tracking-[0.1em]">
               <tr>
                 <th class="px-6 py-4 poppins">Ref #</th>
                 <th class="px-6 py-4 poppins">Passenger</th>
                 <th class="px-6 py-4 poppins">Flight</th>
                 <th class="px-6 py-4 poppins">Status</th>
               </tr>
             </thead>
             <tbody class="divide-y divide-gray-100">
               <tr v-for="booking in recentBookings" :key="booking.id" class="hover:bg-gray-50/50 transition-colors group/row">
                 <td class="px-6 py-4 font-mono text-xs font-bold text-[#fe3787]">#{{ booking.id }}</td>
                 <td class="px-6 py-4 font-bold text-[#002D1E] poppins text-xs">{{ booking.passenger }}</td>
                 <td class="px-6 py-4 text-xs text-gray-400 poppins font-mono">{{ booking.flight }}</td>
                 <td class="px-6 py-4">
                   <span :class="statusClass(booking.status)" class="px-2 py-0.5 rounded-[1px] text-[9px] font-black uppercase poppins border">
                     {{ booking.status }}
                   </span>
                 </td>
               </tr>
             </tbody>
           </table>
           <div v-else class="h-64 flex flex-col items-center justify-center text-gray-300">
              <i class="ph ph-scroll text-4xl mb-2"></i>
              <p class="text-[10px] uppercase font-black tracking-[0.2em] poppins">No recent activity</p>
           </div>
         </div>
       </div>
    </div>

    <!-- Cabin Mix (Flight & Superadmin) -->
    <div v-if="userRole === 'superadmin' || userRole === 'flight_admin'" class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
      <div class="lg:col-span-5 bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 group relative overflow-hidden">
        <div class="absolute top-0 left-0 w-1 h-full bg-[#fe3787] opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <h3 class="text-sm font-black text-[#002D1E] poppins uppercase tracking-widest flex items-center gap-2 mb-6">
          <i class="ph ph-chart-donut text-[#fe3787]"></i>
          Seat Class Distribution
        </h3>
        <div class="flex items-center justify-center h-32 relative">
          <div v-if="seatclassLoading" class="animate-spin text-[#fe3787] text-4xl">
            <i class="ph ph-spinner-gap"></i>
          </div>
          <template v-else>
            <canvas ref="seatClassChartRef"></canvas>
            <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span class="text-2xl font-black text-[#002D1E] poppins">{{ seatclassDist.total }}</span>
              <span class="text-[8px] font-bold text-gray-400 uppercase tracking-widest poppins">Bookings</span>
            </div>
          </template>
        </div>
      </div>

      <div class="lg:col-span-7 bg-white border border-gray-200 rounded-[1px] shadow-sm p-4">
        <h3 class="text-sm font-black text-[#002D1E] poppins uppercase tracking-widest mb-6">Class Breakdown</h3>
        <div class="space-y-4">
          <div v-for="cls in seatclassDist.classes" :key="cls.label">
            <div class="flex items-center justify-between mb-1">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full" :style="{ background: cls.color }"></span>
                <span class="text-xs font-bold text-[#002D1E] poppins">{{ cls.label }}</span>
              </div>
              <span class="text-[10px] font-black poppins" :style="{ color: cls.color }">{{ cls.percentage }}%</span>
            </div>
            <div class="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full transition-all duration-700" :style="{ width: cls.percentage + '%', background: cls.color }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
       <div v-for="action in quickActions" :key="action.label" class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-all group">
          <div class="flex items-start justify-between">
             <div :class="action.colorClass" class="w-12 h-12 rounded-[1px] flex items-center justify-center text-xl shadow-inner">
                <i :class="action.icon"></i>
             </div>
             <router-link :to="action.link" class="text-[#fe3787] opacity-0 group-hover:opacity-100 transition-opacity">
                <i class="ph ph-arrow-square-out text-xl"></i>
             </router-link>
          </div>
          <h4 class="mt-6 text-sm font-black text-[#002D1E] poppins uppercase tracking-wider">{{ action.label }}</h4>
          <p class="text-[10px] text-gray-400 poppins font-medium mt-1">{{ action.description }}</p>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '@/services/admin/api'
import AuthStorage from '@/utils/authStorage'

Chart.register(...registerables)

// Core State
const loading = ref(false)
const error = ref(null)
const chartPeriod = ref('7')

// Data Refs
const stats = ref({
  passengersToday: 0,
  passengerGrowth: 0,
  totalRevenue: 0,
  revenueGrowth: 0,
  totalBookings: 0,
  pendingBookings: 0,
  activeFlights: 0,
  scheduledFlights: 0,
  checkins: 0
})
const recentBookings = ref([])
const revenueByRouteData = ref({ labels: [], data: [] })
const ticketSalesData = ref({ labels: [], data: [] })
const revenueBreakdown = ref([
  { label: 'Airfare', value: 0, color: '#fe3787' },
  { label: 'Add-ons', value: 0, color: '#002D1E' },
  { label: 'Taxes', value: 0, color: '#3b82f6' }
])
const seatclassLoading = ref(false)
const seatclassDist = ref({ total: 0, classes: [] })

// Chart Refs
const ticketChartRef = ref(null)
const revenueChartRef = ref(null)
const seatClassChartRef = ref(null)
const revenueByRouteChartRef = ref(null)

let ticketChartInstance = null
let revenueChartInstance = null
let seatClassChartInstance = null
let revenueByRouteChartInstance = null

// Computed
const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-PH', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good Morning'
  if (hour < 18) return 'Good Afternoon'
  return 'Good Evening'
})

const userRole = computed(() => {
  return AuthStorage.getRole() || 'admin'
})

const hasTicketData = computed(() => ticketSalesData.value.data.some(val => val > 0))

// Actions & Logic
const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  try {
    const responses = await Promise.allSettled([
      api.get('/dashboard/stats/'),
      api.get('/dashboard/revenue_breakdown/'),
      api.get('/dashboard/recent_bookings/'),
      api.get(`/dashboard/ticket_sales/?days=${chartPeriod.value}`)
    ])

    if (responses[0].status === 'fulfilled') {
      const d = responses[0].value.data
      stats.value = {
        passengersToday: d.passengersToday || 0,
        passengerGrowth: d.passengerGrowth || 0,
        totalRevenue: d.totalRevenue || 0,
        revenueGrowth: d.revenueGrowth || 0,
        totalBookings: d.totalBookings || 0,
        pendingBookings: d.pendingBookings || 0,
        activeFlights: d.activeFlights || 0,
        scheduledFlights: d.scheduledFlights || 0,
        checkins: d.totalCheckins || 0
      }
    }
    
    if (responses[1].status === 'fulfilled' && responses[1].value.data?.breakdown) {
      const b = responses[1].value.data.breakdown
      revenueBreakdown.value = [
        { label: 'Airfare', value: b.tickets || 0, color: '#fe3787' },
        { label: 'Add-ons', value: b.addons || 0, color: '#002D1E' },
        { label: 'Taxes', value: b.taxes || 0, color: '#3b82f6' }
      ]
    }

    if (responses[2].status === 'fulfilled') {
      recentBookings.value = responses[2].value.data || []
    }

    if (responses[3].status === 'fulfilled') {
      ticketSalesData.value = {
        labels: responses[3].value.data.labels || [],
        data: responses[3].value.data.data || []
      }
    }

    fetchSeatClassDistribution()
    fetchRevenueStats()

    await nextTick()
    initCharts()
  } catch (err) {
    error.value = 'Failed to load dashboard data.'
  } finally {
    loading.value = false
  }
}

const fetchTicketSales = async () => {
  try {
    const res = await api.get(`/dashboard/ticket_sales/?days=${chartPeriod.value}`)
    ticketSalesData.value = { labels: res.data.labels || [], data: res.data.data || [] }
    updateTicketChart()
  } catch (err) { console.error(err) }
}

const fetchRevenueStats = async () => {
  try {
    const res = await api.get('/dashboard/revenue_by_route/')
    revenueByRouteData.value = res.data
    nextTick(initRevenueByRouteChart)
  } catch (err) { console.error(err) }
}

const fetchSeatClassDistribution = async () => {
  seatclassLoading.value = true
  try {
    const res = await api.get('/dashboard/seat_class_distribution/')
    seatclassDist.value = res.data || { total: 0, classes: [] }
    nextTick(initSeatClassChart)
  } catch (err) { console.error(err) }
  finally { seatclassLoading.value = false }
}

const initCharts = () => {
  initTicketChart()
  initRevenueChart()
}

const initTicketChart = () => {
  if (!ticketChartRef.value) return
  if (ticketChartInstance) ticketChartInstance.destroy()
  const ctx = ticketChartRef.value.getContext('2d')
  const gradient = ctx.createLinearGradient(0, 0, 0, 400)
  gradient.addColorStop(0, 'rgba(254, 55, 135, 0.2)')
  gradient.addColorStop(1, 'rgba(254, 55, 135, 0)')

  ticketChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ticketSalesData.value.labels,
      datasets: [{
        label: 'Tickets',
        data: ticketSalesData.value.data,
        borderColor: '#fe3787',
        borderWidth: 3,
        backgroundColor: gradient,
        tension: 0.4,
        fill: true,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { 
        y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
        x: { grid: { display: false } }
      }
    }
  })
}

const updateTicketChart = () => {
  if (ticketChartInstance) {
    ticketChartInstance.data.labels = ticketSalesData.value.labels
    ticketChartInstance.data.datasets[0].data = ticketSalesData.value.data
    ticketChartInstance.update()
  }
}

const initRevenueChart = () => {
  if (!revenueChartRef.value) return
  if (revenueChartInstance) revenueChartInstance.destroy()
  const ctx = revenueChartRef.value.getContext('2d')
  const data = revenueBreakdown.value.map(i => i.value)
  const colors = revenueBreakdown.value.map(i => i.color)
  const hasData = data.some(v => v > 0)

  revenueChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: revenueBreakdown.value.map(i => i.label),
      datasets: [{
        data: hasData ? data : [1, 1, 1],
        backgroundColor: hasData ? colors : ['#eee', '#eee', '#eee'],
        borderWidth: 0
      }]
    },
    options: { 
      responsive: true, maintainAspectRatio: false, cutout: '75%',
      plugins: { legend: { display: false } }
    }
  })
}

const initRevenueByRouteChart = () => {
  if (!revenueByRouteChartRef.value) return
  if (revenueByRouteChartInstance) revenueByRouteChartInstance.destroy()
  const ctx = revenueByRouteChartRef.value.getContext('2d')
  revenueByRouteChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: revenueByRouteData.value.labels,
      datasets: [{
        label: 'Revenue',
        data: revenueByRouteData.value.data,
        backgroundColor: '#fe3787',
        borderRadius: 2
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: '#f3f4f6' } }
      }
    }
  })
}

const initSeatClassChart = () => {
  if (!seatClassChartRef.value || seatclassDist.value.classes.length === 0) return
  if (seatClassChartInstance) seatClassChartInstance.destroy()
  const ctx = seatClassChartRef.value.getContext('2d')
  seatClassChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: seatclassDist.value.classes.map(c => c.label),
      datasets: [{
        data: seatclassDist.value.classes.map(c => c.count),
        backgroundColor: seatclassDist.value.classes.map(c => c.color),
        borderWidth: 4,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '70%',
      plugins: { legend: { display: false } }
    }
  })
}

const quickActions = computed(() => {
  const actions = [
    { label: 'Add Flight', description: 'Schedule new departure', icon: 'ph ph-calendar-plus', link: '/admin/manage-flight/schedules', colorClass: 'bg-blue-50 text-blue-600', roles: ['superadmin', 'flight_admin'] },
    { label: 'Check-in Registry', description: 'Manage trainee check-ins', icon: 'ph ph-user-check', link: '/admin/passenger/check-ins', colorClass: 'bg-pink-50 text-[#fe3787]', roles: ['superadmin', 'flight_admin'] },
    { label: 'LMS Performance', description: 'Student success & activities', icon: 'ph ph-student', link: '/admin/student-info/lms-overview', colorClass: 'bg-emerald-50 text-emerald-600', roles: ['superadmin', 'lms_admin'] }
  ]
  return actions.filter(action => action.roles.includes(userRole.value))
})

const formatNumber = (num) => {
  if (!num) return '0'
  return parseFloat(num).toLocaleString('en-PH')
}

const statusClass = (status) => {
  const map = {
    'Confirmed': 'bg-emerald-50 text-emerald-700 border-emerald-100',
    'Pending': 'bg-amber-50 text-amber-700 border-amber-100',
    'Cancelled': 'bg-rose-50 text-rose-700 border-rose-100',
    'Completed': 'bg-blue-50 text-blue-700 border-blue-100'
  }
  return map[status] || 'bg-gray-50 text-gray-600 border-gray-100'
}

onMounted(fetchDashboardData)
onUnmounted(() => {
  [ticketChartInstance, revenueChartInstance, seatClassChartInstance, revenueByRouteChartInstance].forEach(i => i?.destroy())
})
</script>

<style scoped>
.poppins { font-family: 'Poppins', sans-serif; }
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }
</style>