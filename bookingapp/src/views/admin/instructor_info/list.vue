<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <button 
          @click="exportInstructors" 
          class="bg-white border border-gray-200 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
        >
          <i class="ph ph-export"></i> Export CSV
        </button>
        <button 
          @click="openAddModal" 
          class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-bold poppins text-[14px] rounded-[1px] shadow-lg shadow-[#fe3787]/20 transition-all"
        >
          <i class="ph ph-plus-circle"></i> New Instructor
        </button>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div 
        v-for="(stat, key) in statsItems" 
        :key="key" 
        class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins mb-1">{{ key }}</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ stat.value }}</p>
          </div>
          <div :class="stat.iconBg" class="w-12 h-12 rounded-full flex items-center justify-center transition-transform hover:scale-110">
            <i :class="[stat.icon, stat.iconColor, 'text-xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="relative flex-1">
          <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search instructors by name or ID..." 
            class="pl-10 pr-4 py-2 border border-gray-200 rounded-[1px] w-full outline-none focus:border-[#fe3787] transition-all poppins text-sm"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedType" 
          class="border border-gray-200 px-3 py-2 rounded-[1px] outline-none focus:border-[#fe3787] transition-all poppins text-sm bg-white min-w-[140px]"
          @change="fetchInstructors"
        >
          <option value="">All Categories</option>
          <option value="Adult">Adult Instructor</option>
          <option value="Child">Junior Staff</option>
        </select>

        <select 
          v-model="bookingFilter" 
          class="border border-gray-200 px-3 py-2 rounded-[1px] outline-none focus:border-[#fe3787] transition-all poppins text-sm bg-white min-w-[140px]"
          @change="fetchInstructors"
        >
          <option value="">All Statuses</option>
          <option value="yes">Active Bookings</option>
          <option value="no">No Bookings</option>
        </select>

        <button 
          @click="clearFilters" 
          class="bg-gray-100 text-gray-600 px-6 py-2 rounded-[1px] hover:bg-gray-200 font-bold poppins text-sm transition-all"
        >
          Reset Filters
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="px-6 py-4 text-[11px] uppercase tracking-widest font-bold text-gray-400 poppins">Instructor/Personnel</th>
            <th class="px-6 py-4 text-[11px] uppercase tracking-widest font-bold text-gray-400 poppins">Identification</th>
            <th class="px-6 py-4 text-[11px] uppercase tracking-widest font-bold text-gray-400 poppins">Classification</th>
            <th class="px-6 py-4 text-[11px] uppercase tracking-widest font-bold text-gray-400 poppins">Status</th>
            <th class="px-6 py-4 text-right text-[11px] uppercase tracking-widest font-bold text-gray-400 poppins">Management</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="instructor in paginatedInstructors" :key="instructor.id" class="hover:bg-gray-50/50 transition-colors group">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-[#002D1E] flex items-center justify-center shadow-inner">
                  <i class="ph ph-chalkboard-teacher text-white text-lg"></i>
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] block poppins">{{ instructor.full_name }}</span>
                  <span class="text-[10px] uppercase font-bold text-gray-400 tracking-tighter poppins">SYSID: {{ instructor.id }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2 mb-1">
                <i class="ph ph-identification-card text-[#fe3787] text-sm"></i>
                <span class="text-[13px] font-semibold text-gray-700 poppins">{{ instructor.passport_number || 'PENDING' }}</span>
              </div>
              <div class="text-[11px] font-bold text-gray-400 uppercase poppins">{{ instructor.nationality || 'NON-RESIDENT' }}</div>
            </td>
            <td class="px-6 py-4">
              <span :class="typeClass(instructor.passenger_type)" class="px-2 py-1 rounded-[1px] font-bold uppercase poppins text-[10px] tracking-widest">
                {{ instructor.passenger_type }}
              </span>
              <div class="text-[11px] font-semibold text-gray-400 mt-1 poppins">Vat Reg: {{ instructor.age ? instructor.age + 'Y' : 'N/A' }}</div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <span :class="bookingClass(instructor.booking_count)" class="px-2 py-1 rounded-[1px] font-bold poppins text-[10px] uppercase tracking-widest">
                  {{ instructor.booking_count }} Assignments
                </span>
              </div>
              <div v-if="instructor.last_booking" class="text-[10px] font-bold text-gray-400 mt-1 uppercase poppins">
                Active Since: {{ formatDate(instructor.last_booking) }}
              </div>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button @click="viewDetails(instructor)" class="p-2 text-gray-400 hover:text-blue-600 transition-colors" title="Audit View">
                  <i class="ph ph-eye text-xl"></i>
                </button>
                <button @click="editInstructor(instructor)" class="p-2 text-gray-400 hover:text-green-600 transition-colors" title="Modify Record">
                  <i class="ph ph-pencil-simple text-xl"></i>
                </button>
                <button @click="deleteInstructor(instructor.id)" class="p-2 text-gray-400 hover:text-red-600 transition-colors" title="Purge Record">
                  <i class="ph ph-trash text-xl"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="instructors.length === 0 && !loading" class="p-16 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-50 rounded-full flex items-center justify-center border border-gray-100 shadow-inner">
          <i class="ph ph-chalkboard-teacher text-3xl text-gray-200"></i>
        </div>
        <h3 class="text-lg font-bold text-[#002D1E] mb-2 poppins uppercase tracking-wider">Empty Registry</h3>
        <p class="text-sm text-gray-400 poppins max-w-xs mx-auto">No instructor personnel found matching your criteria in the system.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-16 text-center">
        <i class="ph ph-circle-notch animate-spin text-4xl text-[#fe3787]"></i>
        <p class="mt-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins">Accessing Personnel Files...</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredInstructors.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ filteredInstructors.length }} Operators
          </div>
          <div class="flex gap-1">
            <button 
              @click="prevPage" 
              :disabled="currentPage === 1"
              class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
            >
              Prev
            </button>
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="goToPage(page)"
              :disabled="page === '...'"
              :class="[
                'px-4 py-2 border rounded-[1px] text-xs font-bold uppercase poppins transition-all shadow-sm',
                page === '...' ? 'bg-white border-gray-200 text-gray-400 underline underline-offset-4' : 
                currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'bg-white border-gray-200 text-[#002D1E] hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
              class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals (Add/Edit) -->
    <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#001f15]/80 backdrop-blur-md px-4">
      <div class="bg-white w-full max-w-md rounded-[1px] shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300">
        <div class="bg-gray-50 border-b border-gray-100 px-6 py-4 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-[#fe3787]/10 flex items-center justify-center">
              <i class="ph ph-chalkboard-teacher text-[#fe3787]"></i>
            </div>
            <h2 class="text-sm font-bold text-[#002D1E] uppercase tracking-widest poppins">{{ isEditing ? 'Modify Personnel' : 'Add Personnel' }}</h2>
          </div>
          <button @click="closeModal" class="text-gray-400 hover:text-red-500 transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveInstructor" class="p-6 space-y-5">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 poppins">First Name</label>
              <input v-model="form.first_name" type="text" class="w-full border border-gray-200 p-2.5 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm bg-gray-50/50" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 poppins">Last Name</label>
              <input v-model="form.last_name" type="text" class="w-full border border-gray-200 p-2.5 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm bg-gray-50/50" required>
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 poppins">Middle Name</label>
            <input v-model="form.middle_name" type="text" class="w-full border border-gray-200 p-2.5 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm bg-gray-50/50">
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 poppins">Category</label>
              <select v-model="form.passenger_type" class="w-full border border-gray-200 p-2.5 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm bg-gray-50/50" required>
                <option value="Adult">Adult Personnel</option>
                <option value="Child">Junior Staff</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 poppins">Date of Birth</label>
              <input v-model="form.date_of_birth" type="date" class="w-full border border-gray-200 p-2.5 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm bg-gray-50/50">
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 poppins">ID/Passport</label>
              <input v-model="form.passport_number" type="text" class="w-full border border-gray-200 p-2.5 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm bg-gray-50/50">
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 poppins">Nationality</label>
              <input v-model="form.nationality" type="text" class="w-full border border-gray-200 p-2.5 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm bg-gray-50/50">
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-6 border-t border-gray-50 mt-4">
            <button type="button" @click="closeModal" class="px-6 py-2.5 text-xs font-bold uppercase text-gray-400 hover:text-gray-600 transition-colors poppins">Cancel</button>
            <button type="submit" class="px-8 py-2.5 bg-[#002D1E] text-white rounded-[1px] text-xs font-bold uppercase tracking-widest hover:bg-black transition-all shadow-lg poppins">
              {{ isEditing ? 'Update Registry' : 'Commit Record' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Details View Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#001f15]/90 backdrop-blur-lg px-4">
      <div class="bg-white w-full max-w-lg rounded-[1px] shadow-2xl overflow-hidden animate-in slide-in-from-bottom-4 duration-500">
        <div class="relative h-24 bg-[#002D1E]">
          <div class="absolute -bottom-8 left-8 p-1 bg-white rounded-full">
            <div class="w-20 h-20 rounded-full bg-gray-50 flex items-center justify-center border-2 border-gray-100">
              <i class="ph ph-user-circle-plus text-5xl text-[#fe3787]"></i>
            </div>
          </div>
          <button @click="showDetailsModal = false" class="absolute top-4 right-4 w-8 h-8 rounded-full bg-black/20 flex items-center justify-center text-white hover:bg-red-500 transition-colors">
            <i class="ph ph-x"></i>
          </button>
        </div>

        <div v-if="selectedInstructor" class="p-8 pt-12 space-y-6">
          <div>
            <h3 class="text-2xl font-black text-[#002D1E] poppins tracking-tight">{{ selectedInstructor.full_name }}</h3>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins">Personnel ID: #{{ selectedInstructor.id }}</span>
              <span class="w-1 h-1 rounded-full bg-gray-200"></span>
              <span class="text-[10px] font-bold text-[#fe3787] uppercase tracking-widest poppins">Class: {{ selectedInstructor.passenger_type }}</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-8 border-y border-gray-50 py-6">
            <div class="space-y-4">
              <div>
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1 poppins">Credentials</p>
                <div class="flex items-center gap-2 text-sm font-bold text-[#002D1E] poppins">
                  <i class="ph ph-identification-card text-gray-300"></i>
                  {{ selectedInstructor.passport_number || 'UNVERIFIED' }}
                </div>
              </div>
              <div>
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1 poppins">Provenance</p>
                <div class="flex items-center gap-2 text-sm font-bold text-[#002D1E] poppins">
                  <i class="ph ph-globe text-gray-300"></i>
                  {{ selectedInstructor.nationality || 'UNKNOWN' }}
                </div>
              </div>
            </div>
            <div class="space-y-4">
              <div>
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1 poppins">Audit Age</p>
                <div class="flex items-center gap-2 text-sm font-bold text-[#002D1E] poppins">
                  <i class="ph ph-calendar-blank text-gray-300"></i>
                  {{ selectedInstructor.age || 'N/A' }} Years
                </div>
              </div>
              <div>
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1 poppins">Ops Scale</p>
                <div class="flex items-center gap-2 text-sm font-bold text-[#fe3787] poppins">
                  <i class="ph ph-chart-line-up"></i>
                  {{ selectedInstructor.booking_count }} Assignments
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedInstructor.booking_count > 0" class="bg-gray-50 p-4 rounded-[1px] border border-gray-100">
            <div class="flex justify-between items-center">
              <span class="text-[10px] font-bold text-[#002D1E] uppercase tracking-widest poppins">Last Mission Sync</span>
              <span class="text-[10px] font-black text-gray-400 poppins">{{ formatDate(selectedInstructor.last_booking) }}</span>
            </div>
          </div>

          <div class="flex justify-end pt-4">
            <button @click="showDetailsModal = false" class="px-10 py-3 bg-gray-900 text-white text-[10px] font-black uppercase tracking-widest hover:bg-[#fe3787] transition-all shadow-xl poppins">Close Access</button>
          </div>
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
  first_name: '', last_name: '', middle_name: '', passenger_type: '', 
  date_of_birth: '', passport_number: '', nationality: '', title: ''
})

// Stats
const stats = ref({ total: 0, active: 0, withBookings: 0, avgBookings: 0 })

const statsItems = computed(() => ({
  'Global Instructors': { value: stats.value.total, icon: 'ph ph-chalkboard-teacher', iconBg: 'bg-blue-100', iconColor: 'text-blue-600' },
  'Active Personnel': { value: stats.value.active, icon: 'ph ph-user-check', iconBg: 'bg-green-100', iconColor: 'text-green-600' },
  'Mission Loaded': { value: stats.value.withBookings, icon: 'ph ph-ticket', iconBg: 'bg-[#fe3787]/10', iconColor: 'text-[#fe3787]' },
  'Ops Efficiency': { value: stats.value.avgBookings, icon: 'ph ph-chart-pie', iconBg: 'bg-purple-100', iconColor: 'text-purple-600' }
}))

// Computed properties
const filteredInstructors = computed(() => {
  let f = instructors.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    f = f.filter(i => i.full_name?.toLowerCase().includes(q) || i.passport_number?.toLowerCase().includes(q) || String(i.id).includes(q))
  }
  if (selectedType.value) f = f.filter(i => i.passenger_type === selectedType.value)
  return f
})

const totalPages = computed(() => Math.ceil(filteredInstructors.value.length / itemsPerPage))
const paginatedInstructors = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredInstructors.value.slice(start, start + itemsPerPage)
})
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredInstructors.value.length))

const visiblePages = computed(() => {
  const pages = []
  const t = totalPages.value; const c = currentPage.value;
  if (t <= 5) for (let i = 1; i <= t; i++) pages.push(i)
  else {
    if (c <= 3) { for (let i = 1; i <= 4; i++) pages.push(i); pages.push('...', t) }
    else if (c >= t - 2) { pages.push(1, '...'); for (let i = t - 3; i <= t; i++) pages.push(i) }
    else pages.push(1, '...', c - 1, c, c + 1, '...', t)
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
    instructors.value = response.data.results || response.data
    calculateStats()
  } catch (err) { console.error(err) } finally { loading.value = false }
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
  isEditing.value = false; currentId.value = null;
  form.value = { first_name: '', last_name: '', middle_name: '', passenger_type: '', date_of_birth: '', passport_number: '', nationality: '', title: '' }
  showModal.value = true
}

const editInstructor = (i) => {
  isEditing.value = true; currentId.value = i.id;
  form.value = { ...i, date_of_birth: i.date_of_birth ? i.date_of_birth.split('T')[0] : '' }
  showModal.value = true
}

const viewDetails = (i) => { selectedInstructor.value = i; showDetailsModal.value = true }

const saveInstructor = async () => {
  try {
    if (isEditing.value) await api.put(`/passengers/${currentId.value}/`, form.value)
    else await api.post('/passengers/', form.value)
    await fetchInstructors(); closeModal()
  } catch (err) { console.error(err) }
}

const deleteInstructor = async (id) => {
  if (confirm('Permanently redact instructor record?')) {
    try {
      await api.delete(`/passengers/${id}/`)
      instructors.value = instructors.value.filter(i => i.id !== id); calculateStats()
    } catch (err) { console.error(err) }
  }
}

const closeModal = () => { showModal.value = false; showDetailsModal.value = false; isEditing.value = false; currentId.value = null }

const exportInstructors = async () => {
  try {
    const response = await api.get('/passengers/export/', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `instructors_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click(); link.remove()
  } catch (err) { console.error(err) }
}

const typeClass = (type) => {
  switch(type) {
    case 'Adult': return 'bg-blue-50 text-blue-600 border border-blue-100'
    case 'Child': return 'bg-yellow-50 text-yellow-600 border border-yellow-100'
    default: return 'bg-gray-50 text-gray-400 border border-gray-100'
  }
}

const bookingClass = (count) => {
  if (count === 0) return 'bg-gray-50 text-gray-300'
  if (count === 1) return 'bg-green-50 text-green-600'
  return 'bg-[#fe3787]/5 text-[#fe3787]'
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : ''
const clearFilters = () => { searchQuery.value = ''; selectedType.value = ''; bookingFilter.value = ''; currentPage.value = 1; fetchInstructors() }

let searchTimeout = null
const debounceSearch = () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => fetchInstructors(), 500) }

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (p) => { if (p !== '...') currentPage.value = p }

watch([searchQuery, selectedType, bookingFilter], () => currentPage.value = 1)
onMounted(fetchInstructors)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
.poppins { font-family: 'Poppins', sans-serif; }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }
</style>
