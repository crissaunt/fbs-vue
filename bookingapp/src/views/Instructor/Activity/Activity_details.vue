<template>
  <div class="p-0 m-0">
    <!-- Main Application UI (Hidden during print) -->
    <div v-if="!isPrinting" class="flex flex-col h-screen bg-gray-50 font-sans">
      <!-- Header -->
      <div class="bg-gradient-to-r from-pink-500 to-pink-400 text-white px-6 py-2.5 flex items-center justify-between shadow-sm z-20 border-b border-pink-400">
        <div class="flex items-center gap-4">
          <button @click="toggleSidebar" class="p-1.5 hover:bg-pink-600 rounded-md transition-colors focus:outline-none">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-xl shadow-inner">🎓</div>
          <div>
            <h1 class="text-[10px] font-bold uppercase tracking-widest text-white/90">Cabagan State University</h1>
            <p class="text-[9px] uppercase tracking-tighter opacity-60">Faculty Portal</p>
          </div>
        </div>
      </div>

      <div class="relative">
        <button @click="toggleDropdown" class="flex items-center gap-2 hover:bg-slate-800 p-1.5 rounded-md transition-colors focus:outline-none">
          <span class="text-xs font-medium">{{ fullName || 'Instructor' }}</span>
          <div class="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center overflow-hidden border border-slate-600">
             <div class="w-full h-full bg-slate-600 rounded-full flex items-center justify-center text-white text-xs font-bold uppercase">{{ initials }}</div>
          </div>
        </button>
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
          <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium">Logout</button>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar -->
      <div :class="['bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg border-r border-pink-400/20', sidebarOpen ? 'w-56' : 'w-16']">
        <div class="flex flex-col h-full overflow-y-auto">
          <button @click="router.push('/instructor/dashboard')" class="flex items-center py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/20 justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
            <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Home</span>
          </button>

          <button @click="router.push('/instructor/logs')" class="flex items-center py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/20 justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Activity Logs</span>
          </button>
          <div 
            v-for="section in sections" 
            :key="section.id" 
            @click="goToSection(section.id)" 
            :class="[
              'flex items-center py-2.5 hover:bg-pink-600 cursor-pointer transition-colors border-b border-pink-400/10',
              sidebarOpen ? 'px-5' : 'justify-center'
            ]"
          >
            <div class="w-7 h-7 rounded-full bg-white text-pink-500 flex items-center justify-center font-bold text-[10px] flex-shrink-0 shadow-sm uppercase">
              {{ section.section_name ? section.section_name.charAt(0) : 'S' }}
            </div>
            <span v-show="sidebarOpen" class="ml-3 truncate text-[11px] font-bold tracking-wider uppercase text-white">{{ section.section_name }}</span>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto bg-[#FDFBF7] p-8" :data-date="new Date().toLocaleDateString()">
        <div class="max-w-5xl mx-auto">
          
          <div class="flex justify-between items-center mb-6">
            <button @click="router.back()" class="flex items-center text-gray-500 hover:text-black font-bold text-sm uppercase">
              <span class="mr-2">←</span> BACK
            </button>
            <div class="flex gap-6 text-[11px] font-bold uppercase tracking-widest">
              <span 
                @click="activeTab = 'instructions'"
                :class="[activeTab === 'instructions' ? 'text-green-700 border-b-2 border-green-700 pb-1' : 'text-gray-400 cursor-pointer hover:text-gray-600']"
              >
                Instruction/s
              </span>
              <span 
                @click="activeTab = 'submissions'"
                :class="[activeTab === 'submissions' ? 'text-green-700 border-b-2 border-green-700 pb-1' : 'text-gray-400 cursor-pointer hover:text-gray-600']"
              >
                Student work
              </span>
                            <span 
                @click="router.push(`/instructor/activity/${route.params.activityId}/toplist`)"
                class="text-gray-400 cursor-pointer hover:text-gray-600"
              >
                Overview
              </span>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-10">
            <!-- Loading State (Skeleton UI) -->
            <div v-if="loading" class="animate-pulse">
              <div class="flex justify-between items-start mb-10">
                <div class="space-y-4 w-2/3">
                  <div class="h-10 bg-gray-200 rounded-lg w-3/4"></div>
                  <div class="h-4 bg-gray-100 rounded w-1/2"></div>
                  <div class="flex gap-2">
                    <div class="h-6 bg-gray-50 rounded w-20 border border-gray-100"></div>
                    <div class="h-6 bg-gray-50 rounded w-20 border border-gray-100"></div>
                  </div>
                </div>
                <div class="w-32 h-4 bg-gray-100 rounded"></div>
              </div>
              
              <div class="space-y-6">
                <!-- Activity Stats Skeleton -->
                <div class="grid grid-cols-3 gap-6 mb-10">
                  <div v-for="i in 3" :key="i" class="h-24 bg-gray-50 rounded-xl border border-gray-100"></div>
                </div>
                
                <!-- Content Placeholder -->
                <div class="space-y-4">
                  <div class="h-6 bg-gray-200 rounded w-48"></div>
                  <div class="space-y-2">
                    <div v-for="i in 5" :key="i" class="h-12 bg-gray-50 rounded border border-gray-100"></div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Activity Content -->
            <div v-else-if="activity">
              <div v-if="activeTab === 'instructions'">
                <div class="flex justify-between items-start mb-8">
                  <div>
                    <h1 class="text-4xl font-light text-gray-900 tracking-wide">{{ activity.title || 'Untitled Activity' }}</h1>
                    <p class="text-xs text-gray-400 font-bold mt-2 uppercase tracking-widest">
                      {{ activity.section_code }} - {{ activity.section_name }}
                    </p>
                    <div class="flex gap-2 mt-3">
                      <span class="px-2 py-1 bg-blue-50 text-blue-600 text-xs font-bold rounded uppercase border border-blue-100">Flight Booking</span>
                      <span class="px-2 py-1 bg-green-50 text-green-600 text-xs font-bold rounded uppercase border border-green-100">
                        {{ activity.is_code_active ? 'Active' : 'Inactive' }}
                      </span>
                      <span class="px-2 py-1 bg-purple-50 text-purple-600 text-xs font-bold rounded uppercase border border-purple-100">
                        Weight: 100%
                      </span>
                    </div>
                  </div>
                  <div class="text-right">
                    <p class="text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest">
                      Due: {{ activity.due_date || 'No due date' }}
                    </p>
                    <div v-if="activity.is_code_active" class="bg-green-100 text-green-700 px-4 py-2 rounded-lg text-xs font-bold border border-green-200">
                      Active Code: {{ activity.activity_code }}
                    </div>
                    <div v-else class="bg-gray-100 text-gray-400 px-4 py-2 rounded-lg text-xs font-bold">
                      Activity code: Not yet Activated
                    </div>
                  </div>
                </div>

                <hr class="mb-8 border-gray-100" />

                <!-- Instructions -->
                <div class="mb-10">
                  <h3 class="text-xs font-black uppercase text-gray-800 mb-4 tracking-widest">Instructions</h3>
                  <div class="border border-gray-100 bg-gray-50/50 p-6 rounded-xl italic text-gray-600 text-sm leading-relaxed whitespace-pre-wrap">
                    {{ activity.instructions || 'No instructions provided.' }}
                  </div>
                </div>

                <!-- Flight Requirements -->
                <div class="mb-10">
                  <h3 class="text-sm font-bold mb-4 text-gray-800">Flight Requirements</h3>
                  <div class="flex gap-2 mb-6">
                    <span class="bg-[#FFC145] px-6 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
                      {{ activity.required_trip_type || 'N/A' }}
                    </span>
                    <span class="bg-[#0D3111] text-white px-6 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
                      {{ activity.required_travel_class || 'N/A' }}
                    </span>
                  </div>

                  <!-- Dynamic Flight Requirements based on trip type -->
                  <div v-if="(activity.required_trip_type || '').toLowerCase().replace(/\s+/g, '_') === 'one_way' || ((!activity.segments || activity.segments.length <= 1) && (activity.required_trip_type || '').toLowerCase().replace(/\s+/g, '_') !== 'round_trip')" class="border border-yellow-200 rounded-3xl py-6 px-10 flex items-center justify-between bg-white relative overflow-hidden">
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">From</p>
                      <p class="text-xl font-bold text-gray-900">{{ activity.required_origin || '-' }}</p>
                    </div>
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">To</p>
                      <p class="text-xl font-bold text-gray-900">{{ activity.required_destination || '-' }}</p>
                    </div>
                    <div class="h-10 w-[1px] bg-gray-200 mx-2"></div>
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">Depart</p>
                      <p class="text-sm font-bold text-gray-800">{{ activity.required_departure_date || 'N/A' }}</p>
                    </div>
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">Return</p>
                      <p class="text-sm font-bold text-gray-800">{{ activity.required_return_date || 'N/A' }}</p>
                    </div>
                    <div class="h-10 w-[1px] bg-gray-200 mx-2"></div>
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">Passenger</p>
                      <p class="text-xs text-gray-700">
                        Adult: <b>{{ activity.required_passengers || 0 }}</b> 
                        child: <b>{{ activity.required_children || 0 }}</b> 
                        infant: <b>{{ activity.required_infants || 0 }}</b>
                      </p>
                    </div>
                  </div>

                  <!-- Multi-City / Round Trip Segments -->
                  <div v-else class="space-y-3">
                    <div v-for="(segment, idx) in activity.segments" :key="idx" class="border border-yellow-200 rounded-2xl py-4 px-8 flex items-center justify-between bg-white relative overflow-hidden">
                      <div class="absolute left-0 top-0 bottom-0 w-1.5 bg-yellow-400"></div>
                      <div class="flex items-center gap-6">
                        <div class="w-8 h-8 rounded-full bg-yellow-50 flex items-center justify-center font-bold text-yellow-600 text-xs shadow-sm">
                          {{ idx + 1 }}
                        </div>
                        <div class="flex items-center gap-10">
                          <div class="text-center">
                            <p class="text-[9px] text-gray-400 uppercase font-black tracking-widest">From</p>
                            <p class="text-lg font-bold text-gray-900 uppercase">{{ segment.origin }}</p>
                          </div>
                          <div class="flex flex-col items-center">
                            <div class="w-12 h-[1px] bg-gray-200 relative mb-1">
                              <div class="absolute -top-1 -right-0.5 text-[8px] text-gray-300">▶</div>
                            </div>
                          </div>
                          <div class="text-center">
                            <p class="text-[9px] text-gray-400 uppercase font-black tracking-widest">To</p>
                            <p class="text-lg font-bold text-gray-900 uppercase">{{ segment.destination }}</p>
                          </div>
                          <div class="ml-4">
                            <p class="text-[9px] text-gray-400 uppercase font-black tracking-widest">Departure Date</p>
                            <p class="text-xs font-bold text-gray-700">{{ segment.departure_date || 'N/A' }}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div v-if="idx === 0" class="text-right border-l border-gray-100 pl-8">
                        <p class="text-[9px] text-gray-400 uppercase font-black tracking-widest mb-1">Passengers</p>
                        <p class="text-[10px] text-gray-700 font-medium">
                          Adult: <b>{{ activity.required_passengers || 0 }}</b><br>
                          Child: <b>{{ activity.required_children || 0 }}</b><br>
                          Infant: <b>{{ activity.required_infants || 0 }}</b>
                        </p>
                      </div>
                      <div v-else class="w-24"></div> <!-- Spacer for other rows -->
                    </div>
                  </div>
                </div>

                <!-- Passenger Information -->
                <div class="border border-gray-200 rounded-xl p-8 bg-white">
                  <h3 class="text-lg font-bold mb-8 text-gray-800">Passenger Information</h3>
                  <div v-if="activity.passengers && activity.passengers.length > 0">
                    <div v-for="(p, index) in activity.passengers" :key="index" class="mb-10 last:mb-0 border-b border-gray-50 pb-8 last:border-0">
                      <div class="flex justify-between items-center mb-6">
                        <h4 class="font-black text-sm text-gray-900 uppercase tracking-tight">
                          Passenger {{ index + 1 }} ({{ p.type || 'Adult' }})
                        </h4>
                        <span v-if="p.seat_preference" class="text-xs font-bold uppercase tracking-widest text-gray-800">
                          seat preference: <span class="text-gray-400">{{ p.seat_preference }}</span>
                        </span>
                      </div>
                      
                      <!-- Dynamic Passenger Fields Grid -->
                      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <!-- Gender -->
                        <div v-if="hasValue(p.gender)">
                          <label class="text-xs font-bold text-red-500 uppercase tracking-tight">Gender*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                            {{ formatGender(p.gender) }}
                          </div>
                        </div>
                        
                        <!-- First Name -->
                        <div v-if="hasValue(p.first_name)">
                          <label class="text-[9px] font-black text-red-500 uppercase">First Name*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.first_name }}
                          </div>
                        </div>
                        
                        <!-- Middle Name -->
                        <div v-if="hasValue(p.middle_name)">
                          <label class="text-[9px] font-black text-gray-400 uppercase">Middle Name</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.middle_name }}
                          </div>
                        </div>
                        
                        <!-- Last Name -->
                        <div v-if="hasValue(p.last_name)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Last Name*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.last_name }}
                          </div>
                        </div>
                        
                        <!-- Date of Birth -->
                        <div v-if="hasValue(p.date_of_birth)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Date of Birth*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ formatDate(p.date_of_birth) }}
                          </div>
                        </div>
                        
                        <!-- Nationality -->
                        <div v-if="hasValue(p.nationality)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Nationality*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.nationality }}
                          </div>
                        </div>

                        <!-- Passenger Category -->
                        <div>
                          <label class="text-[9px] font-black text-red-500 uppercase">Category*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.passenger_category === 'senior' ? 'Senior Citizen' : (p.passenger_category === 'pwd' ? 'PWD' : 'Regular') }}
                          </div>
                        </div>

                        <!-- PWD ID Number (shown only for PWD passengers) -->
                        <div v-if="p.passenger_category === 'pwd' && hasValue(p.pwd_id_number)">
                          <label class="text-[9px] font-black text-blue-600 uppercase">PWD ID Number*</label>
                          <div class="mt-1 p-3 border border-blue-200 rounded-lg text-xs bg-blue-50/50 uppercase text-blue-800 font-mono">
                            {{ p.pwd_id_number }}
                          </div>
                        </div>

                        <!-- Senior Citizen ID (shown only for Senior passengers) -->
                        <div v-if="p.passenger_category === 'senior' && hasValue(p.senior_id_number)">
                          <label class="text-[9px] font-black text-amber-600 uppercase">Senior Citizen ID*</label>
                          <div class="mt-1 p-3 border border-amber-200 rounded-lg text-xs bg-amber-50/50 uppercase text-amber-800 font-mono">
                            {{ p.senior_id_number }}
                          </div>
                        </div>

                        <!-- Passport Expiry Date (shown only for non-Philippines nationality) -->
                        <div v-if="p.nationality && p.nationality.toLowerCase() !== 'philippines' && hasValue(p.passport_expiry_date)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Passport Expiry*</label>
                          <div class="mt-1 p-3 border border-red-200 rounded-lg text-xs bg-red-50/50 uppercase text-red-800">
                            {{ p.passport_expiry_date }}
                          </div>
                        </div>
                        
                        <!-- Passport Number -->
                        <div v-if="hasValue(p.passport_number)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Passport Number*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.passport_number }}
                          </div>
                        </div>
                        
                        <!-- Email -->
                        <div v-if="hasValue(p.email)">
                          <label class="text-[9px] font-black text-gray-400 uppercase">Email</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                            {{ p.email }}
                          </div>
                        </div>
                        
                        <!-- Phone -->
                        <div v-if="hasValue(p.phone)">
                          <label class="text-[9px] font-black text-gray-400 uppercase">Phone</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                            {{ p.phone }}
                          </div>
                        </div>
                        
                        <!-- Special Requirements -->
                        <div v-if="hasValue(p.special_requirements)" class="md:col-span-4">
                          <label class="text-[9px] font-black text-gray-400 uppercase">Special Requirements</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                            {{ p.special_requirements }}
                          </div>
                        </div>
                        
                        <!-- Passenger Add-ons -->
                        <div v-if="getPassengerAddons(p).length > 0" class="md:col-span-4 mt-2">
                          <label class="text-[9px] font-black text-pink-500 uppercase tracking-wide">Assigned Add-ons</label>
                          <div class="mt-1 flex flex-wrap gap-2">
                            <span v-for="addon in getPassengerAddons(p)" :key="addon.id" class="px-3 py-1.5 bg-pink-50 border border-pink-200 text-pink-700 rounded-md text-xs font-bold shadow-sm">
                              {{ addon.addon_name }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-10 text-gray-400">
                    No passenger information available.
                  </div>
                </div>
                
                <!-- Add-on & Insurance Requirements -->
                <div v-if="activity.activity_addons && activity.activity_addons.length > 0" class="mt-10 mb-10">
                  <h3 class="text-xs font-black uppercase text-gray-800 mb-4 tracking-widest">Add-ons & Insurance Requirements</h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div v-for="aa in activity.activity_addons" :key="aa.id" class="border border-pink-100 rounded-xl p-4 bg-pink-50/30 flex items-center justify-between">
                      <div>
                        <p class="text-xs font-bold text-gray-900 leading-tight">{{ aa.addon_name }}</p>
                        <p class="text-[10px] text-gray-400 mt-1 uppercase font-bold tracking-tight">
                          Assign to: {{ aa.passenger?.first_name }} {{ aa.passenger?.last_name || 'Passenger' }}
                        </p>
                      </div>
                      <div class="bg-white text-pink-500 h-8 w-8 rounded-full flex items-center justify-center shadow-sm border border-pink-100">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Activate Button -->
                <div class="mt-12 flex flex-col items-center">
                  <div v-if="activity.is_code_active && eligibleStudents.length > 0" class="mb-4 text-center">
                    <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mb-2">
                       {{ eligibleStudents.length }} student(s) haven't received this activity yet
                    </p>
                    <button 
                      @click="openActivationModal"
                      :disabled="activating"
                      class="px-8 py-3 bg-pink-500 hover:bg-pink-600 text-white rounded-xl font-bold text-xs uppercase tracking-widest transition-all shadow-md active:scale-95 disabled:opacity-50"
                    >
                      Release to more students
                    </button>
                  </div>

                  <button 
                    v-if="!activity.is_code_active"
                    @click="openActivationModal"
                    :disabled="activating"
                    class="w-full max-w-lg bg-[#FFC145] hover:bg-yellow-500 disabled:bg-gray-200 disabled:text-gray-400 py-4 rounded-xl font-bold text-sm uppercase tracking-widest transition-all shadow-md active:scale-95 disabled:cursor-not-allowed"
                  >
                    {{ activating ? 'Processing...' : 'Activate' }}
                  </button>
                  
                  <div v-else-if="eligibleStudents.length === 0" class="text-center py-4 px-8 bg-green-50 rounded-xl border border-green-100">
                     <p class="text-xs font-bold text-green-700 uppercase tracking-widest">Released to all students</p>
                  </div>
                </div>
              </div>

              <!-- Student Work Tab Content -->
              <div v-else-if="activeTab === 'submissions'">
                <div class="flex items-center justify-between mb-8">
                  <h2 class="text-2xl font-black text-gray-900 uppercase tracking-tight">Student Submissions</h2>
                  <div class="flex items-center gap-4">
                    <button 
                      v-if="activity && (!activity.grades_released || hasUnreleasedGradedSubmissions)"
                      @click="handleReleaseGrades" 
                      :disabled="releasingGrades"
                      class="text-xs font-bold bg-pink-500 text-white px-4 py-2 hover:bg-pink-600 uppercase tracking-widest flex items-center gap-2 rounded transition-all shadow-sm disabled:opacity-50"
                    >
                      <svg v-if="releasingGrades" class="animate-spin h-3 w-3 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span v-else>{{ activity.grades_released ? 'Release Pending Scores' : 'Release All Scores' }}</span>
                    </button>
                    <div v-else-if="activity?.grades_released" class="flex items-center gap-2 bg-green-50 text-green-700 px-4 py-2 rounded border border-green-100">
                       <span class="text-[9px] font-black uppercase tracking-widest">All Scores Released</span>
                       <span class="text-green-500 text-xs">✓</span>
                    </div>

                    <button 
                      @click="handlePrint" 
                      class="text-[10px] font-black text-green-600 hover:text-green-800 uppercase tracking-widest flex items-center gap-2"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                      </svg>
                      Print Report
                    </button>

                    <button 
                      @click="fetchSubmissions" 
                      class="text-[10px] font-black text-blue-600 hover:text-blue-800 uppercase tracking-widest flex items-center gap-2"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" :class="['h-3 w-3', submissionsLoading ? 'animate-spin' : '']" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Refresh
                    </button>
                  </div>
                </div>

                <div v-if="submissionsLoading && submissions.length === 0" class="text-center py-20">
                  <div class="inline-block w-8 h-8 border-4 border-pink-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                  <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Loading student work...</p>
                </div>

                <div v-else-if="submissions.length === 0" class="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                  <p class="text-gray-400 text-sm italic">No students are currently enrolled in this section.</p>
                </div>

                <div v-else id="printable-submission-table" class="overflow-hidden border border-gray-100 rounded-xl bg-white shadow-sm">
                  <table class="w-full text-left border-collapse">
                    <thead class="bg-gray-50 border-b border-gray-100">
                      <tr>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest">Student</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center">Accuracy</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center">Tech</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center">Org</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center">Comp</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center">Prof</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest">Grade</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center">Sub</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center">Rel</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest print:hidden text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50">
                      <tr v-for="sub in submissions" :key="sub.student_id" class="hover:bg-gray-50/50 transition-colors">
                        <td class="px-3 py-3">
                          <div class="font-bold text-xs text-gray-900 truncate max-w-[120px]">{{ sub.first_name }} {{ sub.last_name }}</div>
                          <div class="text-[9px] text-gray-400 font-medium tracking-tight uppercase">{{ sub.student_number }}</div>
                        </td>
                        <td class="px-3 py-3 text-center">
                          <span v-if="sub.booking" class="text-[10px] font-bold" :class="getRubricStats(sub).accuracy.ratio > 0 ? 'text-green-600' : 'text-gray-400'">
                            {{ getRubricStats(sub).accuracy.level }}
                          </span>
                          <span v-else class="text-gray-300">-</span>
                        </td>
                        <td class="px-3 py-3 text-center">
                          <span v-if="sub.booking" class="text-[10px] font-bold" :class="getRubricStats(sub).tech.ratio > 0 ? 'text-blue-600' : 'text-gray-400'">
                            {{ getRubricStats(sub).tech.level }}
                          </span>
                          <span v-else class="text-gray-300">-</span>
                        </td>
                        <td class="px-3 py-3 text-center">
                          <span v-if="sub.booking" class="text-[10px] font-bold" :class="getRubricStats(sub).org.ratio > 0 ? 'text-amber-600' : 'text-gray-400'">
                            {{ getRubricStats(sub).org.level }}
                          </span>
                          <span v-else class="text-gray-300">-</span>
                        </td>
                        <td class="px-3 py-3 text-center">
                          <span v-if="sub.booking" class="text-[10px] font-bold" :class="getRubricStats(sub).comp.ratio > 0 ? 'text-pink-600' : 'text-gray-400'">
                            {{ getRubricStats(sub).comp.level }}
                          </span>
                          <span v-else class="text-gray-300">-</span>
                        </td>
                        <td class="px-3 py-3 text-center">
                          <span v-if="sub.booking" class="text-[10px] font-bold" :class="getRubricStats(sub).prof.ratio > 0 ? 'text-purple-600' : 'text-gray-400'">
                            {{ getRubricStats(sub).prof.level }}
                          </span>
                          <span v-else class="text-gray-300">-</span>
                        </td>
                        <td class="px-3 py-3 text-[11px] font-bold text-gray-700">
                          <span v-if="sub.booking" class="text-pink-500 font-black">
                            {{ Math.round((getRubricStats(sub).total / (activity?.total_points || 100)) * 100) }}%
                          </span>
                          <span v-else class="text-gray-300">-</span>
                        </td>
                        <td class="px-3 py-3 text-center">
                          <span :class="['px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-wider', getStatusClass(sub.status)]">
                            {{ sub.status === 'graded' ? 'DONE' : sub.status === 'submitted' ? 'SUB' : 'NOT' }}
                          </span>
                        </td>
                        <td class="px-3 py-3 text-center">
                          <div v-if="sub.is_released" class="text-green-500 text-xs flex justify-center">✓</div>
                          <div v-else-if="sub.grade !== null" class="text-amber-500 text-xs flex justify-center">○</div>
                          <span v-else class="text-gray-300 text-[9px]">-</span>
                        </td>
                        <td class="px-3 py-3 print:hidden text-right">
                          <button 
                            v-if="sub.booking"
                            @click="goToAnalysis(sub)"
                            class="text-[8px] font-black text-pink-500 hover:text-pink-700 uppercase tracking-widest border border-pink-100 px-2 py-1 rounded hover:bg-pink-50 transition-all shadow-sm"
                          >
                            Details
                          </button>
                          <span v-else class="text-[8px] font-bold text-gray-300 uppercase tracking-widest">Waiting</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Error State -->
            <div v-else class="text-center py-20">
              <p class="text-red-400 font-bold uppercase mb-2">Failed to load activity details.</p>
              <p class="text-gray-400 text-xs italic mb-4">{{ errorMessage }}</p>
              <button 
                @click="fetchData" 
                class="px-6 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-white p-10 rounded-2xl text-center shadow-2xl max-w-sm w-full border border-gray-100">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 text-4xl shadow-inner">✅</div>
        <h2 class="text-2xl font-black mb-2 uppercase text-gray-900 tracking-tight">Activated</h2>
        <p class="text-gray-500 text-[11px] mb-8 leading-relaxed font-medium">Activity has been assigned to the selected students. Share this code with them:</p>
        <div class="bg-gray-50 text-4xl font-mono font-black py-5 rounded-2xl tracking-widest text-pink-600 border-2 border-dashed border-pink-200 mb-8 uppercase shadow-sm">
          {{ activity?.activity_code }}
        </div>
        <button @click="showSuccessModal = false" class="w-full bg-slate-900 text-white py-4 rounded-xl font-bold uppercase text-xs tracking-widest hover:bg-black transition-all shadow-lg active:scale-95">Complete</button>
      </div>
    </div>

    <!-- Activation Student Selection Modal -->
    <div v-if="showActivationModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-gray-100 flex flex-col max-h-[90vh]">
        <!-- Modal Header -->
        <div class="p-8 border-b border-gray-50 bg-gray-50/30">
          <div class="flex justify-between items-start mb-2">
            <div>
              <h2 class="text-2xl font-black uppercase text-gray-900 tracking-tight">Select Students</h2>
              <p class="text-[10px] font-bold text-pink-500 uppercase tracking-widest mt-1">
                {{ activity?.is_code_active ? 'Re-releasing to remaining students' : 'Assigning students to activity' }}
              </p>
            </div>
            <button @click="showActivationModal = false" class="text-gray-400 hover:text-gray-600 p-2 rounded-full hover:bg-gray-100 transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Selection Controls -->
        <div class="px-8 py-4 bg-white border-b border-gray-50 flex items-center justify-between">
          <label class="flex items-center gap-3 cursor-pointer group">
            <div class="relative flex items-center justify-center w-5 h-5 border-2 border-gray-200 rounded-md group-hover:border-pink-300 transition-colors" :class="isAllSelected ? 'bg-pink-500 border-pink-500' : 'bg-white'">
              <input type="checkbox" class="absolute inset-0 opacity-0 cursor-pointer" :checked="isAllSelected" @change="toggleSelectAll">
              <svg v-if="isAllSelected" class="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="4">
                <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </div>
            <span class="text-[11px] font-black uppercase tracking-widest text-gray-500 group-hover:text-pink-600 transition-colors">Select All ({{ eligibleStudents.length }})</span>
          </label>
          <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">{{ selectedStudentIds.length }} Selected</span>
        </div>

        <!-- Student List -->
        <div class="overflow-y-auto max-h-[400px] p-4 bg-gray-50/20">
          <div v-if="eligibleStudents.length === 0" class="text-center py-10 italic text-gray-400 text-sm">
            All enrolled students have already received this activity.
          </div>
          <div v-else class="space-y-2">
            <div 
              v-for="student in eligibleStudents" 
              :key="student.id"
              @click="toggleStudentSelection(student.id)"
              class="flex items-center justify-between p-4 bg-white rounded-2xl border transition-all cursor-pointer hover:shadow-md active:scale-[0.98]"
              :class="selectedStudentIds.includes(student.id) ? 'border-pink-500 shadow-sm ring-1 ring-pink-500/10' : 'border-gray-100 hover:border-pink-200'"
            >
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center font-bold text-slate-500 uppercase text-xs">
                  {{ student.first_name[0] }}{{ student.last_name[0] }}
                </div>
                <div>
                  <h3 class="text-sm font-bold text-gray-900 leading-tight">{{ student.first_name }} {{ student.last_name }}</h3>
                  <p class="text-[10px] text-gray-400 font-bold tracking-widest mt-0.5">{{ student.student_number }}</p>
                </div>
              </div>
              <div class="w-6 h-6 border-2 rounded-lg flex items-center justify-center transition-colors" :class="selectedStudentIds.includes(student.id) ? 'bg-pink-500 border-pink-500' : 'bg-gray-100 border-gray-200'">
                <svg v-if="selectedStudentIds.includes(student.id)" class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="p-8 border-t border-gray-50 bg-white">
          <button 
            @click="confirmActivation"
            :disabled="selectedStudentIds.length === 0 || activating"
            class="w-full bg-slate-900 hover:bg-black disabled:bg-gray-200 disabled:text-gray-400 text-white py-4 rounded-2xl font-black uppercase text-xs tracking-widest transition-all shadow-xl active:scale-95 flex items-center justify-center gap-3"
          >
            <span v-if="activating" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
             {{ activating ? 'Processing Activation...' : (activity?.is_code_active ? 'Release to Students' : 'Activate Activity') }}
          </button>
          <p v-if="selectedStudentIds.length === 0" class="text-center mt-4 text-[9px] font-bold text-red-400 uppercase tracking-widest italic animate-pulse">
            Select at least one student to continue
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- Strictly Table-Only Print Layout (Shown only during print) -->
  <div v-else class="bg-white" style="padding: 0; margin: 0;">
    <div style="border: 1px solid #e5e7eb; border-radius: 8px; margin: 12px; overflow: hidden;">
      <table style="width: 100%; border-collapse: collapse; text-align: left; line-height: 1.2; font-family: Arial, sans-serif; table-layout: fixed;">
        <colgroup>
          <col style="width: 22%;">
          <col style="width: 11%;">
          <col style="width: 11%;">
          <col style="width: 12%;">
          <col style="width: 12%;">
          <col style="width: 14%;">
          <col style="width: 11%;">
        </colgroup>
        <thead style="background-color: #f9fafb; border-bottom: 1px solid #e5e7eb;">
          <tr>
            <th style="padding: 6px 12px; font-size: 9px; font-weight: 900; color: #6b7280; letter-spacing: 0.08em; text-transform: uppercase;">STUDENT</th>
            <th style="padding: 6px 4px; font-size: 9px; font-weight: 900; color: #6b7280; text-align: center;">Accuracy</th>
            <th style="padding: 6px 4px; font-size: 9px; font-weight: 900; color: #6b7280; text-align: center;">Tech Skill</th>
            <th style="padding: 6px 4px; font-size: 9px; font-weight: 900; color: #6b7280; text-align: center;">Organization</th>
            <th style="padding: 6px 4px; font-size: 9px; font-weight: 900; color: #6b7280; text-align: center;">Completeness</th>
            <th style="padding: 6px 4px; font-size: 9px; font-weight: 900; color: #6b7280; text-align: center;">Professionalism</th>
            <th style="padding: 6px 8px; font-size: 9px; font-weight: 900; color: #6b7280; text-align: center;">Total Grade</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sub in submissions" :key="sub.student_id" style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 3px 12px;">
              <div style="font-weight: 700; font-size: 10px; color: #111827; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{{ sub.first_name }} {{ sub.last_name }}</div>
              <div style="font-size: 8px; color: #9ca3af; white-space: nowrap;">{{ sub.student_number }}</div>
            </td>
            <td style="padding: 3px 6px; text-align: center; font-size: 10px; font-weight: 700; color: #374151;">{{ sub.booking ? getRubricStats(sub).accuracy.level + '' : '-' }}</td>
            <td style="padding: 3px 6px; text-align: center; font-size: 10px; font-weight: 700; color: #374151;">{{ sub.booking ? getRubricStats(sub).tech.level + '' : '-' }}</td>
            <td style="padding: 3px 6px; text-align: center; font-size: 10px; font-weight: 700; color: #374151;">{{ sub.booking ? getRubricStats(sub).org.level + '' : '-' }}</td>
            <td style="padding: 3px 6px; text-align: center; font-size: 10px; font-weight: 700; color: #374151;">{{ sub.booking ? getRubricStats(sub).comp.level + '' : '-' }}</td>
            <td style="padding: 3px 6px; text-align: center; font-size: 10px; font-weight: 700; color: #374151;">{{ sub.booking ? getRubricStats(sub).prof.level + '' : '-' }}</td>
            <td style="padding: 3px 12px; text-align: center; font-size: 11px; font-weight: 900; color: #ec4899;">
              <span v-if="sub.booking">
                {{ Math.round((getRubricStats(sub).total / (activity?.total_points || 100)) * 100) }}%
              </span>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { activityDetailsService } from '@/services/instructor/activityDetailsService'
import { useNotificationStore } from '@/stores/notification'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const notificationStore = useNotificationStore()
const router = useRouter()
const route = useRoute()

// --- Helper Functions ---
// --- Granular Scoring Helpers ---
const getRubricStats = (sub) => {
    // Determine the source of breakdown data
    const rb = sub.rubric_breakdown || [];
    const analysis = sub.analysis || {};
    
    // We strictly use the backend's provided grade and breakdown to ensure perfect matching
    // with the Instructor Scoring area.
    return {
        accuracy: { 
            level: rb[0]?.level || (analysis.accuracy >= 1 ? 5 : (analysis.accuracy >= 0.8 ? 4 : (analysis.accuracy >= 0.5 ? 3 : 2))), 
            ratio: rb[0]?.ratio ?? analysis.accuracy ?? 0, 
            status: rb[0]?.status 
        },
        tech: { 
            level: rb[1]?.level || (analysis.tech >= 1 ? 5 : (analysis.tech >= 0.7 ? 4 : (analysis.tech >= 0.4 ? 3 : 2))), 
            ratio: rb[1]?.ratio ?? analysis.tech ?? 0, 
            status: rb[1]?.status 
        },
        org: { 
            level: rb[2]?.level || (analysis.org >= 1 ? 5 : (analysis.org >= 0.8 ? 4 : (analysis.org >= 0.5 ? 3 : 2))), 
            ratio: rb[2]?.ratio ?? analysis.org ?? 0, 
            status: rb[2]?.status 
        },
        comp: { 
            level: rb[3]?.level || (analysis.comp >= 1 ? 5 : (analysis.comp >= 0.5 ? 3 : 2)), 
            ratio: rb[3]?.ratio ?? analysis.comp ?? 0, 
            status: rb[3]?.status 
        },
        prof: { 
            level: rb[4]?.level || (analysis.prof >= 1 ? 5 : (analysis.prof >= 0.7 ? 4 : (analysis.prof >= 0.4 ? 3 : 2))), 
            ratio: rb[4]?.ratio ?? analysis.prof ?? 0, 
            status: rb[4]?.status 
        },
        total: sub.grade ?? 0
    };
}

const getStatusLabel = (status) => {
  const labels = {
    'assigned': 'Assigned',
    'in_progress': 'In Progress',
    'submitted': 'Submitted',
    'graded': 'Graded',
    'not_assigned': 'Not Taken'
  }
  return labels[status] || status
}

const getStatusClass = (status) => {
  const classes = {
    'assigned': 'bg-gray-100 text-gray-600',
    'in_progress': 'bg-blue-100 text-blue-600',
    'submitted': 'bg-green-100 text-green-700',
    'graded': 'bg-purple-100 text-purple-700',
    'not_assigned': 'bg-red-50 text-red-400'
  }
  return classes[status] || 'bg-gray-50 text-gray-500'
}

// --- UI State ---
const sidebarOpen = ref(false) 
const dropdownOpen = ref(false)
const showSuccessModal = ref(false)
const showActivationModal = ref(false)
const isPrinting = ref(false)
const loading = ref(true)
const activating = ref(false)
const errorMessage = ref('')
const activeTab = ref('instructions') // 'instructions' or 'submissions'
const submissionsLoading = ref(false)
const releasingGrades = ref(false)

// Selective Activation State
const eligibleStudents = ref([])
const selectedStudentIds = ref([])
const isAllSelected = computed(() => {
  return eligibleStudents.value.length > 0 && selectedStudentIds.value.length === eligibleStudents.value.length
})

// --- Data State ---
const sections = ref([])
const user = ref({ first_name: '', last_name: '', username: '' })
const activity = ref(null)
const submissions = ref([])

// --- Computed ---
const fullName = computed(() => {
  if (user.value.first_name && user.value.last_name) return `${user.value.first_name} ${user.value.last_name}`
  return user.value.username || 'Instructor'
})

const initials = computed(() => {
  const u = user.value.username || 'I'
  return u[0]?.toUpperCase() || 'I'
})

const hasUnreleasedGradedSubmissions = computed(() => {
  return submissions.value.some(sub => sub.grade !== null && !sub.is_released)
})

// --- Helper Functions ---
const hasValue = (value) => {
  return value !== null && value !== undefined && value !== '' && value !== '-'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return dateString
  }
}

const getPassengerAddons = (passenger) => {
  if (!activity.value?.activity_addons) return [];
  return activity.value.activity_addons.filter(aa => 
    aa.passenger?.first_name === passenger.first_name &&
    aa.passenger?.last_name === passenger.last_name
  );
}

// --- Actions ---
const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const fetchData = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    // 1. Fetch Dashboard data for sidebar sections and user info
    const dashData = await instructorDashboardService.getDashboard()
    sections.value = dashData.sections || []
    user.value = dashData.user || { first_name: '', last_name: '', username: '' }

    // 2. Fetch Activity details
    const activityId = route.params.activityId 
    
    if (!activityId) {
      errorMessage.value = "No activity ID found in URL"
      console.error("No activityId found in route parameters")
      activity.value = null
      return
    }

    console.log('Fetching activity with ID:', activityId)
    const data = await activityDetailsService.getActivity(activityId)
    console.log('Activity data received:', data)
    activity.value = data
    
    // 3. Fetch eligible students for activation
    await fetchEligibleStudents()
    
    // 4. Fetch submissions if we're on that tab
    if (activeTab.value === 'submissions') {
      await fetchSubmissions()
    }
    
  } catch (error) {
    console.error("Fetch Error:", error)
    errorMessage.value = error.response?.data?.error || error.response?.data?.detail || error.message || 'Unknown error occurred'
    activity.value = null
  } finally {
    loading.value = false
  }
}

const fetchSubmissions = async () => {
  if (!activity.value) return
  
  submissionsLoading.value = true
  try {
    const data = await activityDetailsService.getSubmissions(activity.value.id)
    submissions.value = data.submissions || []
    console.log('Submissions received:', submissions.value)
  } catch (error) {
    console.error("Error fetching submissions:", error)
  } finally {
    submissionsLoading.value = false
  }
}

const getBookingRoute = (booking) => {
  if (!booking || !booking.details || booking.details.length === 0) return '-';
  
  const segments = booking.details;
  if (segments.length === 1) {
    return `${segments[0].origin} → ${segments[0].destination}`;
  }
  
  // For multi-city or round trip, show the sequence
  const cities = [segments[0].origin];
  segments.forEach(seg => {
    if (cities[cities.length - 1] !== seg.destination) {
      cities.push(seg.destination);
    }
  });
  return cities.join(' → ');
};

const fetchEligibleStudents = async () => {
  const activityId = route.params.activityId
  if (!activityId) return

  try {
    const res = await activityDetailsService.getEligibleStudents(activityId)
    eligibleStudents.value = res.eligible_students || []
    console.log('Eligible students:', eligibleStudents.value)
  } catch (error) {
    console.error("Error fetching eligible students:", error)
  }
}

const toggleStudentSelection = (id) => {
  const index = selectedStudentIds.value.indexOf(id)
  if (index === -1) {
    selectedStudentIds.value.push(id)
  } else {
    selectedStudentIds.value.splice(index, 1)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedStudentIds.value = []
  } else {
    selectedStudentIds.value = eligibleStudents.value.map(s => s.id)
  }
}

const openActivationModal = async () => {
  await fetchEligibleStudents()
  selectedStudentIds.value = eligibleStudents.value.map(s => s.id) // Default checked all
  showActivationModal.value = true
}

const confirmActivation = async () => {
  if (!activity.value || activating.value || selectedStudentIds.value.length === 0) return
  
  activating.value = true
  
  try {
    console.log('Confirming activation for students:', selectedStudentIds.value)
    const res = await activityDetailsService.activateActivity(activity.value.id, selectedStudentIds.value)
    
    console.log('Activation response:', res)
    
    // Update activity data
    activity.value.activity_code = res.activity_code
    activity.value.is_code_active = true
    
    showActivationModal.value = false
    showSuccessModal.value = true
    
    // Refresh eligible students and submissions
    await fetchEligibleStudents()
    if (activeTab.value === 'submissions') {
      await fetchSubmissions()
    }
    
    notificationStore.success(res.message)
  } catch (error) {
    console.error("Activation error:", error)
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Failed to activate activity.'
    notificationStore.error(errorMsg)
  } finally {
    activating.value = false
  }
}

const handleActivation = () => {
  openActivationModal()
}

const goToAnalysis = (sub) => {
  if (!sub.booking) return
  router.push(`/instructor/activity/${activity.value.id}/student/${sub.student_id}/score`)
}

const handlePrint = async () => {
  if (!submissions.value || submissions.value.length === 0) {
    notificationStore.error('No submissions to print.');
    return;
  }

  // Check if any student hasn't taken/completed the activity
  const incompleteStudents = submissions.value.filter(sub => 
    sub.status === 'assigned' || sub.status === 'not_assigned' || sub.status === 'in_progress'
  );

  if (incompleteStudents.length > 0) {
    const confirmMessage = `There are still ${incompleteStudents.length} student/s who haven't taken or finished their activities yet. \n\nDo you want to print the grade report anyway?`;
    if (!window.confirm(confirmMessage)) {
      return;
    }
  }

  // Switch to print-only view
  isPrinting.value = true
  
  // Wait for Vue to fully re-render the print table before calling print
  await nextTick()
  await nextTick() // double nextTick for extra certainty
  // Log the print action to the backend
  if (activity.value) {
    instructorDashboardService.logPrintReport({
      activity_id: activity.value.id,
      report_type: 'Grade Report'
    })
  }
  
  window.print()
  isPrinting.value = false
}

const handleReleaseGrades = async () => {
  if (!activity.value || releasingGrades.value) return
  
  if (!confirm('Are you sure you want to release scores to all students? This will make their grades visible on their dashboard.')) {
    return
  }

  releasingGrades.value = true
  try {
    const res = await activityDetailsService.releaseGrades(activity.value.id)
    activity.value.grades_released = res.grades_released
    notificationStore.success(res.message)
    // Refresh submissions to ensure everything is in sync
    await fetchSubmissions()
  } catch (error) {
    console.error("Release error:", error)
    notificationStore.error(error.response?.data?.error || 'Failed to release grades.')
  } finally {
    releasingGrades.value = false
  }
}

// --- Watchers ---
watch(activeTab, (newTab) => {
  if (newTab === 'submissions') {
    fetchSubmissions()
  }
})

onMounted(() => {
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
  fetchData()
})

const formatGender = (g) => {
  if (!g) return '-';
  const val = g.toLowerCase().trim();
  if (val === 'mr' || val === 'male') return 'Mr.';
  if (val === 'mrs' || val === 'female') return 'Mrs.';
  if (val === 'ms') return 'Ms.';
  return g.charAt(0).toUpperCase() + g.slice(1);
};
</script>

<style>
@media print {
  /* HIDE THE ENTIRE PAGE CONTENT BY DEFAULT IF IT LEAKS */
  body {
    background: white !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* ENSURE THE TABLE WRAPPER LOOKS PREMIUM */
  .bg-white.p-0.m-0 {
    display: block !important;
    width: 100% !important;
  }

  table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin-top: 20px !important;
  }

  th {
    background-color: #f9fafb !important;
    color: #6b7280 !important;
    font-size: 10px !important;
    font-weight: 900 !important;
    padding: 16px !important;
    border-bottom: 1px solid #f3f4f6 !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  td {
    padding: 20px 24px !important;
    border-bottom: 1px solid #f9fafb !important;
    color: #111827 !important;
  }

  .font-bold { font-weight: 700 !important; }
  .text-pink-500 { color: #ec4899 !important; }
  .text-gray-400 { color: #9ca3af !important; }

  @page {
    margin: 1cm !important;
    size: auto !important;
  }
}
</style>
