<template>
  <div class="p-6">
    <!-- Action Buttons -->
    <div class="flex items-center mb-6">
      <div class="flex items-center gap-2">
        <button @click="showTodayCheckIns" class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px]">
          <i class="ph ph-calendar-check"></i> Today's Check-ins
        </button>
        <button @click="refreshData" class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px]">
          <i class="ph ph-arrows-clockwise"></i> Refresh
        </button>
        <button @click="printAllBoarding" class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px]">
          <i class="ph ph-printer"></i> Print All
        </button>
      </div>
    </div>

    <!-- Check-in Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div v-for="(count, label) in stats" :key="label" class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">{{ label }}</p>
        <p class="text-2xl font-bold text-[#002D1E] poppins">{{ count }}</p>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6 text-[14px]">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="relative flex-1">
          <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by passenger or flight..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedFlight" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px]"
          @change="fetchCheckIns"
        >
          <option value="">All Flights</option>
          <option v-for="flight in uniqueFlights" :key="flight" :value="flight">
            {{ flight }}
          </option>
        </select>

        <select 
          v-model="selectedStatus" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px]"
          @change="fetchCheckIns"
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="checked-in">Checked-in</option>
          <option value="boarding">Boarding</option>
          <option value="completed">Completed</option>
        </select>

        <button 
          @click="clearFilters" 
          class="text-white px-4 py-2 border bg-[#fe3787] rounded-[1px] hover:bg-[#fb1873] font-medium poppins text-[14px]"
        >
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Main Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Passenger</th>
            <th class="px-6 py-4 poppins">Flight Information</th>
            <th class="px-6 py-4 poppins">Check-in Details</th>
            <th class="px-6 py-4 poppins">Baggage</th>
            <th class="px-6 py-4 poppins">Boarding Pass</th>
            <th class="px-6 py-4 text-right poppins">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="checkIn in paginatedCheckIns" :key="checkIn.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div>
                <span class="font-semibold text-[#002D1E] block poppins">{{ checkIn.passenger_name }}</span>
                <span class="text-gray-400 poppins">Seat: {{ checkIn.seat_number || 'Not assigned' }}</span>
              </div>
            </td>
            <td class="px-6 py-4">
              <div>
                <span class="font-semibold text-blue-600 block poppins">{{ checkIn.flight_number }}</span>
                <span class="text-gray-400 poppins">{{ formatRoute(checkIn.route) }}</span>
                <span class="text-gray-400 poppins">{{ formatTime(checkIn.departure_time) }}</span>
              </div>
            </td>
            <td class="px-6 py-4">
              <span :class="statusClass(checkIn.status)" class="px-3 py-1 rounded-full font-semibold uppercase poppins mb-1 inline-block">
                {{ checkIn.status }}
              </span>
              <div class="text-gray-400 poppins">{{ formatDateTime(checkIn.check_in_time) }}</div>
              <div v-if="checkIn.check_in_counter" class="text-gray-400 poppins">Counter: {{ checkIn.check_in_counter }}</div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <i class="ph ph-suitcase-simple text-gray-400"></i>
                <span class="poppins">{{ checkIn.baggage_count || 0 }} bags</span>
              </div>
              <div class="text-gray-400 poppins">{{ checkIn.baggage_weight || 0 }} kg</div>
            </td>
            <td class="px-6 py-4">
              <div v-if="checkIn.boarding_pass" class="flex items-center gap-2">
                <i class="ph ph-ticket text-green-500"></i>
                <span class="font-mono text-sm poppins">{{ checkIn.boarding_pass }}</span>
              </div>
              <div v-else class="text-yellow-600 poppins">Not issued</div>
            </td>
            <td class="px-6 py-4 text-right space-x-2">
              <button @click="checkInPassenger(checkIn)" class="text-green-600 hover:text-green-400 p-2" title="Check-in" v-if="!checkIn.status || checkIn.status === 'pending'">
                <i class="ph ph-check-circle text-lg"></i>
              </button>
              <button @click="printBoardingPass(checkIn)" class="text-purple-600 hover:text-purple-400 p-2" title="Print Boarding Pass" v-if="checkIn.boarding_pass">
                <i class="ph ph-printer text-lg"></i>
              </button>
              <button @click="editCheckIn(checkIn)" class="text-blue-600 hover:text-blue-400 p-2" title="Edit">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="deleteCheckIn(checkIn.id)" class="text-red-600 hover:text-red-400 p-2" title="Delete">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="checkIns.length === 0 && !loading" class="p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-airplane-takeoff text-2xl text-gray-400"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No check-ins found</h3>
        <p class="text-gray-500 poppins">Check-in information will appear here once passengers start checking in</p>
      </div>

      <!-- No Results State -->
      <div v-else-if="filteredCheckIns.length === 0" class="p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-magnifying-glass text-[14px] text-gray-400"></i>
        </div>
        <h3 class="text-[14px] font-semibold text-gray-900 mb-2 poppins">No matching check-ins found</h3>
        <p class="text-gray-500 poppins">Try adjusting your search or filters</p>
        <button 
          @click="clearFilters" 
          class="mt-4 bg-[#fe3787] text-gray-700 px-4 py-2 rounded-[1px] font-medium hover:bg-gray-50 poppins"
        >
          Clear Filters
        </button>
      </div>

      <!-- Pagination -->
      <div v-if="filteredCheckIns.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredCheckIns.length }} check-ins
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

    <!-- Check-in Modal -->
    <div v-if="showCheckInModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">Check-in Passenger</h2>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <i class="ph ph-x"></i>
          </button>
        </div>
        
        <div v-if="selectedCheckIn" class="space-y-4">
          <div class="bg-gray-50 p-4 rounded-[1px]">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                <i class="ph ph-user text-blue-600 text-xl"></i>
              </div>
              <div>
                <h3 class="font-semibold text-[#002D1E] poppins">{{ selectedCheckIn.passenger_name }}</h3>
                <p class="text-sm text-gray-500 poppins">Flight: {{ selectedCheckIn.flight_number }}</p>
              </div>
            </div>
          </div>
          
          <form @submit.prevent="processCheckIn" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Seat Number *</label>
                <input 
                  v-model="checkInForm.seat_number" 
                  type="text" 
                  class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
                  placeholder="e.g., 12A"
                  required
                >
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Check-in Counter</label>
                <input 
                  v-model="checkInForm.check_in_counter" 
                  type="text" 
                  class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
                  placeholder="e.g., 3"
                >
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Baggage Count</label>
                <input 
                  v-model="checkInForm.baggage_count" 
                  type="number" 
                  min="0"
                  class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
                >
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Baggage Weight (kg)</label>
                <input 
                  v-model="checkInForm.baggage_weight" 
                  type="number" 
                  min="0"
                  step="0.1"
                  class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
                >
              </div>
            </div>
            
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Special Instructions</label>
              <textarea 
                v-model="checkInForm.special_instructions" 
                rows="2"
                class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
                placeholder="Any special requirements..."
              ></textarea>
            </div>
            
            <div class="flex justify-end gap-2 pt-4 border-t">
              <button type="button" @click="closeModal" class="px-4 py-2 text-gray-600 font-medium poppins">Cancel</button>
              <button type="submit" class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px] font-medium hover:bg-[#e6327a] transition-colors poppins">
                Process Check-in
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Boarding Pass Modal -->
    <div v-if="showBoardingModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl" id="boardingPassPrint">
        <div class="border-2 border-gray-800 p-4 mb-4">
          <div class="text-center mb-4">
            <h2 class="text-xl font-bold text-gray-900 poppins">BOARDING PASS</h2>
            <p class="text-sm text-gray-500 poppins">{{ selectedCheckIn?.flight_number }}</p>
          </div>
          
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 poppins">Passenger:</span>
              <span class="font-semibold poppins">{{ selectedCheckIn?.passenger_name }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 poppins">Flight:</span>
              <span class="font-semibold poppins">{{ selectedCheckIn?.flight_number }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 poppins">Seat:</span>
              <span class="font-semibold text-blue-600 poppins">{{ selectedCheckIn?.seat_number }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 poppins">Departure:</span>
              <span class="font-semibold poppins">{{ formatTime(selectedCheckIn?.departure_time) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 poppins">Gate:</span>
              <span class="font-semibold poppins">TBD</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600 poppins">Boarding Time:</span>
              <span class="font-semibold poppins">{{ calculateBoardingTime(selectedCheckIn?.departure_time) }}</span>
            </div>
          </div>
          
          <div class="mt-4 pt-4 border-t text-center">
            <div class="font-mono text-lg mb-2 poppins">{{ selectedCheckIn?.boarding_pass }}</div>
            <div class="text-xs text-gray-500 poppins">
              ||| ||| ||| ||| ||| ||| ||| ||| ||| |||
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-2">
          <button @click="closeBoardingModal" class="px-4 py-2 text-gray-600 font-medium poppins">Close</button>
          <button @click="printCurrentBoardingPass" class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px] font-medium hover:bg-[#e6327a] poppins">
            <i class="ph ph-printer mr-2"></i> Print
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/services/admin/api'

// Reactive state
const checkIns = ref([])
const loading = ref(false)
const showCheckInModal = ref(false)
const showBoardingModal = ref(false)
const selectedCheckIn = ref(null)

// Filters and pagination
const searchQuery = ref('')
const selectedFlight = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Form data
const checkInForm = ref({
  seat_number: '',
  check_in_counter: '',
  baggage_count: 0,
  baggage_weight: 0,
  special_instructions: '',
  status: 'checked-in'
})

// Computed properties
const stats = computed(() => {
  const total = checkIns.value.length
  const today = new Date().toISOString().split('T')[0]
  const todays = checkIns.value.filter(c => {
    const checkInDate = new Date(c.check_in_time).toISOString().split('T')[0]
    return checkInDate === today
  }).length
  
  const pending = checkIns.value.filter(c => c.status === 'pending').length
  const checkedIn = checkIns.value.filter(c => c.status === 'checked-in').length
  const boarding = checkIns.value.filter(c => c.status === 'boarding').length
  
  const totalBaggage = checkIns.value.reduce((sum, c) => sum + (c.baggage_count || 0), 0)
  
  return {
    'Total Check-ins': total,
    "Today's Check-ins": todays,
    'Pending Check-ins': pending,
    'Checked-in': checkedIn,
    'Boarding': boarding,
    'Total Baggage': totalBaggage
  }
})

const uniqueFlights = computed(() => {
  const flights = new Set()
  checkIns.value.forEach(checkIn => {
    if (checkIn.flight_number) flights.add(checkIn.flight_number)
  })
  return Array.from(flights).sort()
})

const filteredCheckIns = computed(() => {
  let filtered = checkIns.value
  
  // Apply search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(checkIn => 
      checkIn.passenger_name?.toLowerCase().includes(query) ||
      checkIn.flight_number?.toLowerCase().includes(query) ||
      checkIn.boarding_pass?.toLowerCase().includes(query)
    )
  }
  
  // Apply flight filter
  if (selectedFlight.value) {
    filtered = filtered.filter(checkIn => checkIn.flight_number === selectedFlight.value)
  }
  
  // Apply status filter
  if (selectedStatus.value) {
    filtered = filtered.filter(checkIn => checkIn.status === selectedStatus.value)
  }
  
  // Sort by check-in time (most recent first)
  return [...filtered].sort((a, b) => {
    return new Date(b.check_in_time) - new Date(a.check_in_time)
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredCheckIns.value.length / itemsPerPage)
})

const paginatedCheckIns = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredCheckIns.value.slice(start, end)
})

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredCheckIns.value.length))

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
const fetchCheckIns = async () => {
  loading.value = true
  
  try {
    // Build query parameters
    const params = {}
    if (selectedFlight.value) params.flight = selectedFlight.value
    if (selectedStatus.value) params.status = selectedStatus.value
    if (searchQuery.value) params.search = searchQuery.value
    
    const response = await api.get('/check-ins/', { params })
    
    // Format the check-in data
    checkIns.value = response.data.map(checkIn => ({
      ...checkIn,
      passenger_name: `${checkIn.passenger?.first_name || ''} ${checkIn.passenger?.last_name || ''}`.trim(),
      flight_number: checkIn.booking_detail?.schedule?.flight?.flight_number || '',
      route: checkIn.booking_detail?.schedule?.flight?.route || '',
      departure_time: checkIn.booking_detail?.schedule?.departure_time || '',
      seat_number: checkIn.booking_detail?.seat?.seat_number || '',
      status: checkIn.status || 'pending'
    }))
  } catch (err) {
    console.error('Fetch error:', err)
    alert('Failed to load check-in data.')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchCheckIns()
}

const showTodayCheckIns = () => {
  // Filter to show today's check-ins
  const today = new Date().toISOString().split('T')[0]
  const todaysCheckIns = checkIns.value.filter(c => {
    const checkInDate = new Date(c.check_in_time).toISOString().split('T')[0]
    return checkInDate === today
  })
  
  // You could set a special filter or just alert
  alert(`Today's check-ins: ${todaysCheckIns.length} passengers`)
}

const checkInPassenger = (checkIn) => {
  selectedCheckIn.value = checkIn
  // Pre-fill form with existing data
  checkInForm.value = {
    seat_number: checkIn.seat_number || '',
    check_in_counter: checkIn.check_in_counter || '',
    baggage_count: checkIn.baggage_count || 0,
    baggage_weight: checkIn.baggage_weight || 0,
    special_instructions: '',
    status: 'checked-in'
  }
  showCheckInModal.value = true
}

const processCheckIn = async () => {
  try {
    // Generate boarding pass number
    const boardingPass = generateBoardingPass(selectedCheckIn.value)
    
    // Prepare update data
    const updateData = {
      ...checkInForm.value,
      boarding_pass: boardingPass,
      check_in_time: new Date().toISOString(),
      status: 'checked-in'
    }
    
    // Update check-in record
    await api.put(`/check-ins/${selectedCheckIn.value.id}/`, updateData)
    
    // Update local data
    const index = checkIns.value.findIndex(c => c.id === selectedCheckIn.value.id)
    if (index !== -1) {
      checkIns.value[index] = {
        ...checkIns.value[index],
        ...updateData
      }
    }
    
    alert('Passenger checked in successfully! Boarding pass generated.')
    closeModal()
    
    // Show boarding pass
    selectedCheckIn.value = checkIns.value[index]
    showBoardingModal.value = true
    
  } catch (err) {
    console.error('Check-in error:', err)
    alert('Failed to check in passenger.')
  }
}

const generateBoardingPass = (checkIn) => {
  const flightCode = checkIn.flight_number?.replace(/\s+/g, '').substring(0, 6) || 'FLIGHT'
  const passengerInitials = checkIn.passenger_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'PASS'
  const randomNum = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
  return `${flightCode}-${passengerInitials}-${randomNum}`
}

const printBoardingPass = (checkIn) => {
  if (!checkIn.boarding_pass) {
    alert('No boarding pass available. Please check in passenger first.')
    return
  }
  
  selectedCheckIn.value = checkIn
  showBoardingModal.value = true
}

const printCurrentBoardingPass = () => {
  const printContent = document.getElementById('boardingPassPrint').innerHTML
  const originalContent = document.body.innerHTML
  
  document.body.innerHTML = printContent
  window.print()
  document.body.innerHTML = originalContent
  window.location.reload()
}

const printAllBoarding = async () => {
  const checkedInPassengers = checkIns.value.filter(c => c.status === 'checked-in' && c.boarding_pass)
  
  if (checkedInPassengers.length === 0) {
    alert('No checked-in passengers with boarding passes.')
    return
  }
  
  if (confirm(`Print boarding passes for ${checkedInPassengers.length} passengers?`)) {
    // In a real application, you might generate a PDF or multiple printouts
    alert(`Printing boarding passes for ${checkedInPassengers.length} passengers...`)
  }
}

const editCheckIn = (checkIn) => {
  selectedCheckIn.value = checkIn
  checkInForm.value = {
    seat_number: checkIn.seat_number || '',
    check_in_counter: checkIn.check_in_counter || '',
    baggage_count: checkIn.baggage_count || 0,
    baggage_weight: checkIn.baggage_weight || 0,
    special_instructions: '',
    status: checkIn.status
  }
  showCheckInModal.value = true
}

const deleteCheckIn = async (id) => {
  if (confirm('Are you sure you want to delete this check-in record?')) {
    try {
      await api.delete(`/check-ins/${id}/`)
      checkIns.value = checkIns.value.filter(c => c.id !== id)
    } catch (err) {
      console.error('Delete error:', err)
      alert('Failed to delete check-in record.')
    }
  }
}

const closeModal = () => {
  showCheckInModal.value = false
  selectedCheckIn.value = null
  checkInForm.value = {
    seat_number: '',
    check_in_counter: '',
    baggage_count: 0,
    baggage_weight: 0,
    special_instructions: '',
    status: 'checked-in'
  }
}

const closeBoardingModal = () => {
  showBoardingModal.value = false
  selectedCheckIn.value = null
}

const statusClass = (status) => {
  switch(status?.toLowerCase()) {
    case 'pending': return 'bg-yellow-100 text-yellow-700'
    case 'checked-in': return 'bg-green-100 text-green-700'
    case 'boarding': return 'bg-blue-100 text-blue-700'
    case 'completed': return 'bg-gray-100 text-gray-700'
    default: return 'bg-gray-100 text-gray-500'
  }
}

const formatRoute = (route) => {
  if (!route) return 'N/A'
  // Extract origin and destination from route string
  const parts = route.split('→')
  if (parts.length === 2) {
    return `${parts[0].trim()} to ${parts[1].trim()}`
  }
  return route
}

const formatTime = (dateTime) => {
  if (!dateTime) return 'N/A'
  return new Date(dateTime).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return 'N/A'
  return new Date(dateTime).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const calculateBoardingTime = (departureTime) => {
  if (!departureTime) return 'TBD'
  const departure = new Date(departureTime)
  const boardingTime = new Date(departure.getTime() - 30 * 60000) // 30 minutes before
  return boardingTime.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedFlight.value = ''
  selectedStatus.value = ''
  currentPage.value = 1
  fetchCheckIns()
}

// Debounce search input
let searchTimeout = null
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchCheckIns()
  }, 500)
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const goToPage = (page) => {
  if (page !== '...') {
    currentPage.value = page
  }
}

// Watch for filter changes
watch([searchQuery, selectedFlight, selectedStatus], () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(fetchCheckIns)
</script>

<style scoped>
/* Font classes */
.poppins {
  font-family: 'Poppins', sans-serif;
}

/* Design consistency */
.border {
  border-color: #e5e7eb;
}

.border-gray-200 {
  border-color: #e5e7eb;
}

.rounded-\[1px\] {
  border-radius: 1px;
}

.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}
</style>