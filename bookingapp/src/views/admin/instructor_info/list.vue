<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <button 
          @click="exportInstructors" 
          class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px]"
        >
          <i class="ph ph-export"></i> Export
        </button>
        <button 
          @click="openAddModal" 
          class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px]"
        >
          <i class="ph ph-plus"></i> Add Instructor
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Total Instructors</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ stats.total }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-[#fe3787]/10 flex items-center justify-center">
            <i class="ph ph-chalkboard-teacher text-[#fe3787] text-xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Active</p>
            <p class="text-2xl font-bold text-green-600 poppins">{{ stats.active }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
            <i class="ph ph-check-circle text-green-600 text-xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">With Bookings</p>
            <p class="text-2xl font-bold text-blue-600 poppins">{{ stats.withBookings }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <i class="ph ph-ticket text-blue-600 text-xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Avg Bookings</p>
            <p class="text-2xl font-bold text-purple-600 poppins">{{ stats.avgBookings }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
            <i class="ph ph-chart-bar text-purple-600 text-xl"></i>
          </div>
        </div>
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
            placeholder="Search by name, passport, employee ID..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedType" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px]"
          @change="fetchInstructors"
        >
          <option value="">All Types</option>
          <option value="Adult">Adult</option>
          <option value="Child">Child</option>
          <option value="Infant">Infant</option>
        </select>

        <select 
          v-model="bookingFilter" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px]"
          @change="fetchInstructors"
        >
          <option value="">All Instructors</option>
          <option value="yes">With Bookings</option>
          <option value="no">Without Bookings</option>
        </select>

        <button 
          @click="clearFilters" 
          class="text-white px-4 py-2 border bg-[#fe3787] rounded-[1px] hover:bg-[#fb1873] font-medium poppins text-[14px]"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Instructors Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Instructor Info</th>
            <th class="px-6 py-4 poppins">Contact Details</th>
            <th class="px-6 py-4 poppins">Type</th>
            <th class="px-6 py-4 poppins">Date of Birth</th>
            <th class="px-6 py-4 poppins">Bookings</th>
            <th class="px-6 py-4 text-right poppins">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="instructor in paginatedInstructors" :key="instructor.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-[#002D1E] flex items-center justify-center">
                  <i class="ph ph-chalkboard-teacher text-white text-lg"></i>
                </div>
                <div>
                  <span class="font-semibold text-[#002D1E] block poppins">{{ instructor.full_name }}</span>
                  <span class="text-gray-400 poppins">ID: #{{ instructor.id }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-1 mb-1">
                <i class="ph ph-passport text-gray-400 text-sm"></i>
                <span class="poppins">{{ instructor.passport_number || 'No passport' }}</span>
              </div>
              <div class="text-gray-400 poppins">{{ instructor.nationality || 'Unknown' }}</div>
            </td>
            <td class="px-6 py-4">
              <span :class="typeClass(instructor.passenger_type)" class="px-3 py-1 rounded-full font-semibold uppercase poppins text-xs">
                {{ instructor.passenger_type }}
              </span>
              <div class="text-gray-400 mt-1 poppins">Age: {{ instructor.age || 'N/A' }}</div>
            </td>
            <td class="px-6 py-4">
              <div class="font-medium poppins">{{ formatDate(instructor.date_of_birth) || 'Not specified' }}</div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <span :class="bookingClass(instructor.booking_count)" class="px-3 py-1 rounded-full font-semibold poppins text-xs">
                  {{ instructor.booking_count }} booking(s)
                </span>
              </div>
              <div v-if="instructor.last_booking" class="text-gray-400 mt-1 poppins">
                Last: {{ formatDate(instructor.last_booking) }}
              </div>
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="viewDetails(instructor)" class="text-blue-600 hover:text-blue-400 p-2" title="View Details">
                <i class="ph ph-eye text-lg"></i>
              </button>
              <button @click="editInstructor(instructor)" class="text-green-600 hover:text-green-400 p-2" title="Edit">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="deleteInstructor(instructor.id)" class="text-red-600 hover:text-red-400 p-2" title="Delete">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="instructors.length === 0 && !loading" class="p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-chalkboard-teacher text-2xl text-gray-400"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No instructors found</h3>
        <p class="text-gray-500 poppins">Instructor records will appear here once added</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center">
        <i class="ph ph-spinner animate-spin text-4xl text-[#fe3787]"></i>
        <p class="mt-2 text-gray-500 poppins">Loading instructors...</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredInstructors.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredInstructors.length }} instructors
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

    <!-- Add/Edit Instructor Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Instructor' : 'Add New Instructor' }}</h2>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <i class="ph ph-x"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveInstructor" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">First Name *</label>
              <input 
                v-model="form.first_name" 
                type="text" 
                class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
                required
              >
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Last Name *</label>
              <input 
                v-model="form.last_name" 
                type="text" 
                class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
                required
              >
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Middle Name</label>
            <input 
              v-model="form.middle_name" 
              type="text" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            >
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Instructor Type *</label>
            <select 
              v-model="form.passenger_type" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
              <option value="">Select Type</option>
              <option value="Adult">Adult</option>
              <option value="Child">Child</option>
              <option value="Infant">Infant</option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Date of Birth</label>
            <input 
              v-model="form.date_of_birth" 
              type="date" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            >
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passport Number</label>
              <input 
                v-model="form.passport_number" 
                type="text" 
                class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
              >
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Nationality</label>
              <input 
                v-model="form.nationality" 
                type="text" 
                class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
              >
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Title</label>
            <select 
              v-model="form.title" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            >
              <option value="">Select Title</option>
              <option value="MR">Mr.</option>
              <option value="MRS">Mrs.</option>
              <option value="MS">Ms.</option>
            </select>
          </div>

          <!-- Instructor-specific note -->
          <div class="bg-blue-50 border border-blue-200 rounded-[1px] p-3">
            <p class="text-xs text-blue-700 poppins flex items-center gap-2">
              <i class="ph ph-info"></i>
              Instructors are stored as passenger records for system compatibility.
            </p>
          </div>
          
          <div class="flex justify-end gap-2 pt-4 border-t">
            <button 
              type="button" 
              @click="closeModal" 
              class="px-4 py-2 text-gray-600 font-medium poppins hover:bg-gray-100 rounded-[1px]"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="px-4 py-2 bg-[#002D1E] text-white rounded-[1px] font-medium hover:bg-[#001f15] transition-colors poppins"
            >
              {{ isEditing ? 'Update Instructor' : 'Save Instructor' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">Instructor Details</h2>
          <button @click="showDetailsModal = false" class="text-gray-400 hover:text-gray-600">
            <i class="ph ph-x"></i>
          </button>
        </div>
        
        <div v-if="selectedInstructor" class="space-y-4">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-16 h-16 rounded-full bg-[#002D1E] flex items-center justify-center">
              <i class="ph ph-chalkboard-teacher text-3xl text-white"></i>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-[#002D1E] poppins">{{ selectedInstructor.full_name }}</h3>
              <p class="text-sm text-gray-500 poppins">Instructor ID: #{{ selectedInstructor.id }}</p>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Instructor Type</label>
              <div class="p-2 border border-gray-200 rounded-[1px]">
                <span :class="typeClass(selectedInstructor.passenger_type)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                  {{ selectedInstructor.passenger_type }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Age</label>
              <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ selectedInstructor.age || 'N/A' }} years old</div>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Date of Birth</label>
            <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ formatDate(selectedInstructor.date_of_birth) || 'Not specified' }}</div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passport Number</label>
              <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ selectedInstructor.passport_number || 'Not provided' }}</div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Nationality</label>
              <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ selectedInstructor.nationality || 'Not specified' }}</div>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Title</label>
            <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ selectedInstructor.title || 'Not specified' }}</div>
          </div>

          <div v-if="selectedInstructor.booking_count > 0">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Flight Bookings</label>
            <div class="p-3 border border-gray-200 rounded-[1px] bg-gray-50">
              <div class="flex items-center gap-2 mb-2">
                <i class="ph ph-airplane-tilt text-[#002D1E]"></i>
                <span class="font-medium poppins">{{ selectedInstructor.booking_count }} booking(s)</span>
              </div>
              <div v-if="selectedInstructor.last_booking" class="text-xs text-gray-500 poppins">
                Last booking: {{ formatDate(selectedInstructor.last_booking) }}
              </div>
            </div>
          </div>

          <!-- Instructor Status -->
          <div class="bg-[#002D1E] text-white p-4 rounded-[1px]">
            <div class="flex items-center gap-3">
              <i class="ph ph-seal-check text-2xl"></i>
              <div>
                <p class="font-semibold poppins">Verified Instructor</p>
                <p class="text-xs opacity-80 poppins">Active in the system</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-2 pt-4 border-t mt-6">
          <button 
            type="button" 
            @click="showDetailsModal = false" 
            class="px-4 py-2 text-gray-600 font-medium poppins hover:bg-gray-100 rounded-[1px]"
          >
            Close
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
const instructors = ref([])
const loading = ref(false)
const showModal = ref(false)
const showDetailsModal = ref(false)
const selectedInstructor = ref(null)
const isEditing = ref(false)
const currentId = ref(null)

// Filters and pagination
const searchQuery = ref('')
const selectedType = ref('')
const bookingFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Form data
const form = ref({
  first_name: '',
  last_name: '',
  middle_name: '',
  passenger_type: '',
  date_of_birth: '',
  passport_number: '',
  nationality: '',
  title: ''
})

// Stats
const stats = ref({
  total: 0,
  active: 0,
  withBookings: 0,
  avgBookings: 0
})

// Computed properties
const filteredInstructors = computed(() => {
  let filtered = instructors.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(instructor => 
      instructor.first_name?.toLowerCase().includes(query) ||
      instructor.last_name?.toLowerCase().includes(query) ||
      (instructor.passport_number && instructor.passport_number.toLowerCase().includes(query))
    )
  }
  
  if (selectedType.value) {
    filtered = filtered.filter(instructor => instructor.passenger_type === selectedType.value)
  }
  
  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredInstructors.value.length / itemsPerPage)
})

const paginatedInstructors = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredInstructors.value.slice(start, end)
})

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredInstructors.value.length))

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
const fetchInstructors = async () => {
  loading.value = true
  
  try {
    const params = {}
    if (selectedType.value) params.type = selectedType.value
    if (searchQuery.value) params.search = searchQuery.value
    if (bookingFilter.value) params.has_booking = bookingFilter.value
    
    const response = await api.get('/passengers/', { params })
    instructors.value = response.data
    
    // Calculate stats
    calculateStats()
  } catch (err) {
    console.error('Fetch error:', err)
    alert('Failed to load instructor data.')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const total = instructors.value.length
  const withBookings = instructors.value.filter(i => i.booking_count > 0).length
  const active = instructors.value.filter(i => i.booking_count > 0 || !i.date_of_birth).length
  
  const totalBookings = instructors.value.reduce((sum, i) => sum + (i.booking_count || 0), 0)
  const avgBookings = total > 0 ? (totalBookings / total).toFixed(1) : 0
  
  stats.value = { total, active, withBookings, avgBookings }
}

const openAddModal = () => {
  isEditing.value = false
  currentId.value = null
  form.value = {
    first_name: '',
    last_name: '',
    middle_name: '',
    passenger_type: '',
    date_of_birth: '',
    passport_number: '',
    nationality: '',
    title: ''
  }
  showModal.value = true
}

const editInstructor = (instructor) => {
  isEditing.value = true
  currentId.value = instructor.id
  form.value = {
    first_name: instructor.first_name,
    last_name: instructor.last_name,
    middle_name: instructor.middle_name || '',
    passenger_type: instructor.passenger_type,
    date_of_birth: instructor.date_of_birth ? instructor.date_of_birth.split('T')[0] : '',
    passport_number: instructor.passport_number || '',
    nationality: instructor.nationality || '',
    title: instructor.title || ''
  }
  showModal.value = true
}

const viewDetails = (instructor) => {
  selectedInstructor.value = instructor
  showDetailsModal.value = true
}

const saveInstructor = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/passengers/${currentId.value}/`, form.value)
      alert('Instructor updated successfully!')
    } else {
      await api.post('/passengers/', form.value)
      alert('Instructor added successfully!')
    }
    
    await fetchInstructors()
    closeModal()
  } catch (err) {
    console.error('Save error:', err)
    alert('Error saving instructor. Please check your input.')
  }
}

const deleteInstructor = async (id) => {
  if (confirm('Are you sure you want to delete this instructor?')) {
    try {
      await api.delete(`/passengers/${id}/`)
      instructors.value = instructors.value.filter(i => i.id !== id)
      calculateStats()
      alert('Instructor deleted successfully!')
    } catch (err) {
      console.error('Delete error:', err)
      alert('Failed to delete instructor. They may have active bookings.')
    }
  }
}

const closeModal = () => {
  showModal.value = false
  showDetailsModal.value = false
  isEditing.value = false
  currentId.value = null
  form.value = {
    first_name: '',
    last_name: '',
    middle_name: '',
    passenger_type: '',
    date_of_birth: '',
    passport_number: '',
    nationality: '',
    title: ''
  }
}

const exportInstructors = async () => {
  try {
    const response = await api.get('/passengers/export/', {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `instructors_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error('Export error:', err)
    alert('Failed to export instructors.')
  }
}

const typeClass = (type) => {
  switch(type) {
    case 'Adult': return 'bg-blue-100 text-blue-700'
    case 'Child': return 'bg-yellow-100 text-yellow-700'
    case 'Infant': return 'bg-purple-100 text-purple-700'
    default: return 'bg-gray-100 text-gray-500'
  }
}

const bookingClass = (count) => {
  if (count === 0) return 'bg-gray-100 text-gray-500'
  if (count === 1) return 'bg-green-100 text-green-700'
  return 'bg-blue-100 text-blue-700'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedType.value = ''
  bookingFilter.value = ''
  currentPage.value = 1
  fetchInstructors()
}

// Debounce search input
let searchTimeout = null
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchInstructors()
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
watch([searchQuery, selectedType, bookingFilter], () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(fetchInstructors)
</script>

<style scoped>
.poppins {
  font-family: 'Poppins', sans-serif;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>