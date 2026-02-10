<template>
  <div class="p-6">
    <!-- Action Buttons -->
    <div class="flex  items-center mb-6">
      <div class="flex items-center gap-2">
        <button @click="exportPassengers" class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px]">
          <i class="ph ph-export"></i> Export
        </button>
        <button @click="refreshData" class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px]">
          <i class="ph ph-arrows-clockwise"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Passenger Stats -->
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
            placeholder="Search by name, passport..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedType" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px]"
          @change="fetchPassengers"
        >
          <option value="">All Types</option>
          <option value="Adult">Adult</option>
          <option value="Child">Child</option>
          <option value="Infant">Infant</option>
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
            <th class="px-6 py-4 poppins">Contact Info</th>
            <th class="px-6 py-4 poppins">Type</th>
            <th class="px-6 py-4 poppins">Date of Birth</th>
            <th class="px-6 py-4 poppins">Bookings</th>
            <th class="px-6 py-4 text-right poppins">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="passenger in paginatedPassengers" :key="passenger.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div>
                  <span class="font-semibold text-[#002D1E] block poppins">{{ passenger.first_name }} {{ passenger.last_name }}</span>
                  <span class=" text-gray-400 poppins">ID: #{{ passenger.id }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-1 mb-1">
                <i class="ph ph-passport text-gray-400 text-sm"></i>
                <span class="poppins">{{ passenger.passport_number || 'No passport' }}</span>
              </div>
              <div class=" text-gray-400 poppins">{{ passenger.nationality || 'Unknown' }}</div>
            </td>
            <td class="px-6 py-4">
              <span :class="typeClass(passenger.passenger_type)" class="px-3 py-1 rounded-full font-semibold uppercase poppins">
                {{ passenger.passenger_type }}
              </span>
              <div class=" text-gray-400 mt-1 poppins">Age: {{ passenger.age || 'N/A' }}</div>
            </td>
            <td class="px-6 py-4">
              <div class="font-medium poppins">{{ formatDate(passenger.date_of_birth) || 'Not specified' }}</div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <span :class="bookingClass(passenger.booking_count)" class="px-3 py-1 rounded-full font-semibold poppins">
                  {{ passenger.booking_count }} booking(s)
                </span>
              </div>
              <div v-if="passenger.last_booking" class=" text-gray-400 mt-1 poppins">
                Last: {{ formatDate(passenger.last_booking) }}
              </div>
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="editPassenger(passenger)" class="text-blue-600 hover:text-blue-400 p-2" title="Edit">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="deletePassenger(passenger.id)" class="text-red-600 hover:text-red-400 p-2" title="Delete">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="passengers.length === 0 && !loading" class="p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-users text-2xl text-gray-400"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No passengers found</h3>
        <p class="text-gray-500 poppins">Passenger information will appear here once bookings are made</p>
      </div>

      <!-- No Results State -->
      <div v-else-if="filteredPassengers.length === 0" class="p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-magnifying-glass text-[14px] text-gray-400"></i>
        </div>
        <h3 class="text-[14px] font-semibold text-gray-900 mb-2 poppins">No matching passengers found</h3>
        <p class="text-gray-500 poppins">Try adjusting your search or filters</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredPassengers.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredPassengers.length }} passengers
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

    <!-- Add/Edit Passenger Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Passenger' : 'Add New Passenger' }}</h2>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <i class="ph ph-x"></i>
          </button>
        </div>
        
        <form @submit.prevent="savePassenger" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">First Name *</label>
              <input v-model="form.first_name" type="text" class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" required>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Last Name *</label>
              <input v-model="form.last_name" type="text" class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" required>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passenger Type *</label>
            <select v-model="form.passenger_type" class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" required>
              <option value="">Select Type</option>
              <option value="Adult">Adult</option>
              <option value="Child">Child</option>
              <option value="Infant">Infant</option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Date of Birth</label>
            <input v-model="form.date_of_birth" type="date" class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins">
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passport Number</label>
              <input v-model="form.passport_number" type="text" class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins">
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Nationality</label>
              <input v-model="form.nationality" type="text" class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins">
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Title</label>
            <select v-model="form.title" class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins">
              <option value="">Select Title</option>
              <option value="MR">Mr.</option>
              <option value="MRS">Mrs.</option>
              <option value="MS">Ms.</option>
            </select>
          </div>
          
          <div v-if="isEditing && form.passenger_type === 'Infant'">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Linked Adult</label>
            <select v-model="form.linked_adult" class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins">
              <option value="">Select Adult</option>
              <option v-for="adult in adultPassengers" :key="adult.id" :value="adult.id">
                {{ adult.first_name }} {{ adult.last_name }}
              </option>
            </select>
          </div>
          
          <div class="flex justify-end gap-2 pt-4 border-t">
            <button type="button" @click="closeModal" class="px-4 py-2 text-gray-600 font-medium poppins">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px] font-medium hover:bg-[#e6327a] transition-colors poppins">
              {{ isEditing ? 'Update Passenger' : 'Save Passenger' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">Passenger Details</h2>
          <button @click="showDetailsModal = false" class="text-gray-400 hover:text-gray-600">
            <i class="ph ph-x"></i>
          </button>
        </div>
        
        <div class="space-y-4">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
              <i :class="getPassengerIcon(selectedPassenger?.passenger_type)" class="text-2xl text-gray-600"></i>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-[#002D1E] poppins">{{ selectedPassenger?.first_name }} {{ selectedPassenger?.last_name }}</h3>
              <p class="text-sm text-gray-500 poppins">ID: #{{ selectedPassenger?.id }}</p>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passenger Type</label>
              <div class="p-2 border border-gray-200 rounded-[1px]">
                <span :class="typeClass(selectedPassenger?.passenger_type)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                  {{ selectedPassenger?.passenger_type }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Age</label>
              <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ selectedPassenger?.age || 'N/A' }}</div>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Date of Birth</label>
            <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ formatDate(selectedPassenger?.date_of_birth) || 'Not specified' }}</div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passport Number</label>
              <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ selectedPassenger?.passport_number || 'Not provided' }}</div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Nationality</label>
              <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ selectedPassenger?.nationality || 'Not specified' }}</div>
            </div>
          </div>

          <div v-if="selectedPassenger?.booking_count > 0">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Booking Information</label>
            <div class="p-3 border border-gray-200 rounded-[1px] bg-gray-50">
              <div class="flex items-center gap-2 mb-2">
                <i class="ph ph-ticket text-[#fe3787]"></i>
                <span class="font-medium poppins">{{ selectedPassenger?.booking_count }} booking(s)</span>
              </div>
              <div v-if="selectedPassenger?.last_booking" class="text-xs text-gray-500 poppins">
                Last booking: {{ formatDate(selectedPassenger.last_booking) }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-2 pt-4 border-t mt-6">
          <button 
            type="button" 
            @click="showDetailsModal = false" 
            class="px-4 py-2 text-gray-600 font-medium poppins"
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
const passengers = ref([])
const loading = ref(false)
const showDetailsModal = ref(false)
const showAddModal = ref(false)
const showEditModal = ref(false)
const selectedPassenger = ref(null)
const isEditing = ref(false)
const currentId = ref(null)

// Filters and pagination
const searchQuery = ref('')
const selectedType = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Form data
const form = ref({
  first_name: '',
  last_name: '',
  passenger_type: '',
  date_of_birth: '',
  passport_number: '',
  nationality: '',
  title: '',
  linked_adult: null
})

// Computed properties
const stats = computed(() => {
  const total = passengers.value.length
  const adults = passengers.value.filter(p => p.passenger_type === 'Adult').length
  const children = passengers.value.filter(p => p.passenger_type === 'Child').length
  const infants = passengers.value.filter(p => p.passenger_type === 'Infant').length
  
  return {
    'Total Passengers': total,
    'Adults': adults,
    'Children': children,
    'Infants': infants,
  }
})

const adultPassengers = computed(() => {
  return passengers.value.filter(p => p.passenger_type === 'Adult')
})

const filteredPassengers = computed(() => {
  let filtered = passengers.value
  
  // Apply search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(passenger => 
      passenger.first_name.toLowerCase().includes(query) ||
      passenger.last_name.toLowerCase().includes(query) ||
      (passenger.passport_number && passenger.passport_number.toLowerCase().includes(query))
    )
  }
  
  // Apply type filter
  if (selectedType.value) {
    filtered = filtered.filter(passenger => passenger.passenger_type === selectedType.value)
  }
  
  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredPassengers.value.length / itemsPerPage)
})

const paginatedPassengers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredPassengers.value.slice(start, end)
})

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredPassengers.value.length))

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
const fetchPassengers = async () => {
  loading.value = true
  
  try {
    // Build query parameters
    const params = {}
    if (selectedType.value) params.type = selectedType.value
    if (searchQuery.value) params.search = searchQuery.value
    
    const response = await api.get('/passengers/', { params })
    passengers.value = response.data.map(p => ({
      ...p,
      age: calculateAge(p.date_of_birth)
    }))
  } catch (err) {
    console.error('Fetch error:', err)
    alert('Failed to load passenger data.')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchPassengers()
}

const viewDetails = (passenger) => {
  selectedPassenger.value = passenger
  showDetailsModal.value = true
}

const editPassenger = (passenger) => {
  isEditing.value = true
  currentId.value = passenger.id
  form.value = {
    first_name: passenger.first_name,
    last_name: passenger.last_name,
    passenger_type: passenger.passenger_type,
    date_of_birth: passenger.date_of_birth ? passenger.date_of_birth.split('T')[0] : '',
    passport_number: passenger.passport_number || '',
    nationality: passenger.nationality || '',
    title: passenger.title || '',
    linked_adult: passenger.linked_adult || null
  }
  showEditModal.value = true
}

const deletePassenger = async (id) => {
  if (confirm('Are you sure you want to delete this passenger?')) {
    try {
      await api.delete(`/passengers/${id}/`)
      passengers.value = passengers.value.filter(p => p.id !== id)
    } catch (err) {
      console.error('Delete error:', err)
      alert('Failed to delete passenger. They may have active bookings.')
    }
  }
}

const savePassenger = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/passengers/${currentId.value}/`, form.value)
      alert('Passenger updated successfully!')
    } else {
      await api.post('/passengers/', form.value)
      alert('Passenger added successfully!')
    }
    
    await fetchPassengers()
    closeModal()
  } catch (err) {
    console.error('Save error:', err)
    alert('Error saving passenger. Please check your input.')
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  showDetailsModal.value = false
  isEditing.value = false
  currentId.value = null
  form.value = {
    first_name: '',
    last_name: '',
    passenger_type: '',
    date_of_birth: '',
    passport_number: '',
    nationality: '',
    title: '',
    linked_adult: null
  }
}

const exportPassengers = async () => {
  try {
    const response = await api.get('/passengers/export/', {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `passengers_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error('Export error:', err)
    alert('Failed to export passengers.')
  }
}

const getPassengerIcon = (type) => {
  switch(type) {
    case 'Adult': return 'ph ph-user'
    case 'Child': return 'ph ph-baby'
    case 'Infant': return 'ph ph-infant'
    default: return 'ph ph-user-circle'
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

const calculateAge = (dateString) => {
  if (!dateString) return null
  const birthDate = new Date(dateString)
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
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
  currentPage.value = 1
  fetchPassengers()
}

// Debounce search input
let searchTimeout = null
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchPassengers()
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
watch([searchQuery, selectedType], () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(fetchPassengers)
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