<template>
  <div class="min-h-screen bg-[#f5f3ef] py-6 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Back Button -->
      <div class="mb-4">
        <button 
          @click="goToHome" 
          class="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span class="text-sm font-medium">Back</span>
        </button>
      </div>

      <!-- Loading State (Skeleton UI) -->
      <div v-if="loading" class="animate-pulse">
        <div class="bg-white rounded-lg shadow-sm border border-gray-300 overflow-hidden">
          <!-- Header Skeleton -->
          <div class="px-8 pt-8 pb-6 border-b border-gray-200">
            <div class="flex items-start justify-between mb-6">
              <div class="flex-1">
                <div class="h-9 bg-gray-200 rounded-lg w-3/4 mb-4"></div>
                <div class="h-4 bg-gray-100 rounded w-1/3"></div>
              </div>
              <div class="w-32 space-y-2">
                <div class="h-3 bg-gray-100 rounded ml-auto w-full"></div>
                <div class="h-3 bg-gray-100 rounded ml-auto w-3/4"></div>
              </div>
            </div>
            <div class="flex gap-2">
              <div v-for="i in 4" :key="i" class="h-6 bg-gray-50 rounded-full w-20 border border-gray-100"></div>
            </div>
          </div>
          
          <!-- Instructions Skeleton -->
          <div class="px-8 py-6 border-b border-gray-200">
            <div class="h-5 bg-gray-200 rounded w-32 mb-4"></div>
            <div class="space-y-2">
              <div class="h-4 bg-gray-100 rounded w-full"></div>
              <div class="h-4 bg-gray-100 rounded w-5/6"></div>
              <div class="h-4 bg-gray-100 rounded w-4/5"></div>
            </div>
          </div>

          <!-- Quick Info Bar Skeleton -->
          <div class="px-8 py-4 bg-gray-50/50 border-b border-gray-200 flex justify-around">
            <div v-for="i in 4" :key="i" class="text-center space-y-2">
              <div class="h-3 bg-gray-200 rounded w-12 mx-auto"></div>
              <div class="h-4 bg-gray-300 rounded w-20 mx-auto"></div>
            </div>
          </div>

          <!-- Passenger Info Skeleton -->
          <div class="px-8 py-6">
            <div class="h-5 bg-gray-200 rounded w-40 mb-6"></div>
            <div v-for="i in 2" :key="i" class="border border-gray-200 rounded-lg p-6 mb-6">
              <div class="flex justify-between mb-6">
                <div class="h-4 bg-gray-200 rounded w-48"></div>
                <div class="h-4 bg-gray-100 rounded w-32"></div>
              </div>
              <div class="grid grid-cols-12 gap-3 mb-4">
                <div class="col-span-2 h-10 bg-gray-50 rounded border border-gray-100"></div>
                <div class="col-span-4 h-10 bg-gray-50 rounded border border-gray-100"></div>
                <div class="col-span-5 h-10 bg-gray-50 rounded border border-gray-100"></div>
                <div class="col-span-1 h-10 bg-gray-50 rounded border border-gray-100"></div>
              </div>
              <div class="grid grid-cols-3 gap-3">
                <div v-for="j in 3" :key="j" class="h-10 bg-gray-50 rounded border border-gray-100"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-5">
        <div class="flex items-start gap-3">
          <svg class="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div class="flex-1">
            <h3 class="text-sm font-semibold text-red-800 mb-1">Error Loading Activity</h3>
            <p class="text-sm text-red-600 mb-3">{{ error }}</p>
            <div class="flex gap-2">
              <button 
                @click="loadActivityDetails" 
                class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
              >
                Try Again
              </button>
              <button 
                @click="goToHome" 
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300 transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Card -->
      <div v-else class="bg-white rounded-lg shadow-sm border border-gray-300">
        <!-- Header -->
        <div class="px-8 pt-8 pb-6 border-b border-gray-200">
          <div class="flex items-start justify-between mb-3">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ activity.title }}</h1>
              <div class="flex items-center gap-2 text-sm text-gray-600">
                <span>{{ activity.section_code }}</span>
                <span>•</span>
                <span>Block {{ activity.section_name }}</span>
              </div>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-500 mb-1">Due: {{ formatDueDate(activity.due_date) }}</p>
              <p v-if="instructor" class="text-xs text-gray-500">Instructor: {{ instructor.first_name }} {{ instructor.last_name }}</p>
            </div>
          </div>
          
          <!-- Tags -->
          <div class="flex flex-wrap gap-2 mt-4">
            <span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
              {{ activity.activity_type || 'Flight Booking' }}
            </span>
            <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
              {{ activity.section_code }}
            </span>
            <span :class="[
              'px-3 py-1 text-xs font-medium rounded-full',
              activity.required_travel_class?.toLowerCase() === 'business' ? 'bg-green-800 text-white' : 'bg-yellow-100 text-yellow-700'
            ]">
              {{ activity.required_travel_class || 'Economy' }}
            </span>
            <span :class="[
              'px-3 py-1 text-xs font-medium rounded-full',
              activity.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
            ]">
              {{ activity.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>

        <!-- Instructions Section -->
        <div class="px-8 py-6 border-b border-gray-200">
          <h2 class="text-base font-bold text-gray-900 mb-3">Instructions</h2>
          <div class="text-sm text-gray-700 leading-relaxed space-y-3">
            <p class="whitespace-pre-wrap">{{ activity.description || 'No instructions provided.' }}</p>
          </div>
        </div>

        <!-- Flight Requirements Section -->
        <div class="px-8 py-6 border-b border-gray-200">
          <h2 class="text-base font-bold text-gray-900 mb-4">Flight Requirements</h2>
          
          <!-- Trip Type Buttons -->
          <div class="flex gap-3 mb-5">
            <div 
              :class="[
                'px-6 py-2 rounded-full text-sm font-bold uppercase tracking-wide',
                normalizedTripType === 'round trip'
                  ? 'bg-[#f5c842] text-gray-900' 
                  : 'bg-[#f5c842] text-black'
              ]"
            >
              {{ activity.required_trip_type || 'One Way' }}
            </div>
            <div 
              :class="[
                'px-6 py-2 rounded-full text-sm font-bold uppercase tracking-wide',
                normalizedTravelClass === 'business'
                  ? 'bg-[#1a472a] text-white' 
                  : 'bg-[#093704] text-white'
              ]"
            >
              {{ activity.required_travel_class || 'Economy' }}
            </div>
          </div>

          <!-- Flight Details Box - Pill Shape with Yellow Border -->
          <div class="border-2 border-[#f5c842] rounded-full py-6 px-8 bg-white">
            <div class="grid grid-cols-5 gap-6 items-center">
              <!-- From -->
              <div class="text-center">
                <p class="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-1">From</p>
                <p class="text-2xl font-black text-gray-900">{{ activity.required_origin || 'N/A' }}</p>
              </div>

              <!-- To -->
              <div class="text-center">
                <p class="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-1">To</p>
                <p class="text-2xl font-black text-gray-900">{{ activity.required_destination || 'N/A' }}</p>
              </div>

              <!-- Depart -->
              <div class="text-center">
                <p class="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-1">Depart</p>
                <p class="text-sm font-bold text-gray-900">{{ formatFullDate(activity.departure_date) }}</p>
              </div>

              <!-- Return -->
              <div class="text-center">
                <p class="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-1">Return</p>
                <p class="text-sm font-bold text-gray-900">{{ formatFullDate(activity.arrival_date) }}</p>
              </div>

              <!-- Passenger -->
              <div class="text-center">
                <p class="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-1">Passenger</p>
                <div class="flex flex-col items-center gap-0.5 text-[11px] text-gray-700">
                  <div class="flex items-center gap-1">
                    <span class="text-gray-500">Adult:</span>
                    <span class="font-bold">{{ activity.required_passengers || 0 }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <span class="text-gray-500">Child:</span>
                    <span class="font-bold">{{ activity.required_children || 0 }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <span class="text-gray-500">Infant:</span>
                    <span class="font-bold">{{ activity.required_infants || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Passenger Information Section -->
        <div class="px-8 py-6">
          <h2 class="text-base font-bold text-gray-900 mb-4">Passenger Information</h2>
          
          <!-- No passengers message -->
          <div v-if="displayPassengers.length === 0" class="text-center py-8 text-gray-500">
            <p>No passenger information available for this activity.</p>
          </div>
          
          <!-- Passenger Cards -->
          <div v-for="(passenger, index) in displayPassengers" :key="index" class="mb-6">
            <div class="border border-gray-300 rounded-lg p-6">
              <!-- Passenger Header -->
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wide">
                  Passenger {{ index + 1 }} ({{ passenger.type }})
                </h3>
                <span class="text-xs text-gray-600 uppercase tracking-wide">
                  seat preference: <strong>{{ passenger.seat_preference || 'Window' }}</strong>
                </span>
              </div>

              <!-- Form Fields -->
              <div class="space-y-4">
                <!-- Row 1: Gender, First Name, Last Name, MI -->
                <div class="grid grid-cols-12 gap-3">
                  <div class="col-span-2">
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Gender*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.gender || 'N/A' }}
                    </div>
                  </div>
                  <div class="col-span-4">
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">First Name*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.first_name || 'N/A' }}
                    </div>
                  </div>
                  <div class="col-span-5">
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Last Name*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.last_name || 'N/A' }}
                    </div>
                  </div>
                  <div class="col-span-1">
                    <label class="block text-[10px] font-bold text-gray-600 uppercase mb-1.5 tracking-wide">MI</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700 text-center">
                      {{ passenger.middle_initial || '-' }}
                    </div>
                  </div>
                </div>

                <!-- Row 2: Date of Birth -->
                <div>
                  <label class="block text-[10px] font-bold text-gray-700 uppercase mb-1.5 tracking-wide">Date of Birth</label>
                  <div class="grid grid-cols-3 gap-3">
                    <div>
                      <label class="block text-[10px] text-gray-500 mb-1">Day*</label>
                      <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                        {{ passenger.birth_day || 'N/A' }}
                      </div>
                    </div>
                    <div>
                      <label class="block text-[10px] text-gray-500 mb-1">Month*</label>
                      <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                        {{ passenger.birth_month || 'N/A' }}
                      </div>
                    </div>
                    <div>
                      <label class="block text-[10px] text-gray-500 mb-1">Year*</label>
                      <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                        {{ passenger.birth_year || 'N/A' }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Row 3: Nationality and Passport -->
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Nationality*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.nationality || 'N/A' }}
                    </div>
                  </div>
                  <div>
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Passport*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.passport || 'N/A' }}
                    </div>
                  </div>
                </div>

                <!-- Checkboxes -->
                <div class="space-y-2 pt-2">
                  <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer">
                    <div :class="[
                      'w-4 h-4 border border-gray-400 rounded flex items-center justify-center flex-shrink-0',
                      passenger.has_reservation ? 'bg-blue-500 border-blue-500' : 'bg-white'
                    ]">
                      <svg v-if="passenger.has_reservation" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                      </svg>
                    </div>
                    <span>I have a reservation / request</span>
                  </label>
                  <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer">
                    <div :class="[
                      'w-4 h-4 border border-gray-400 rounded flex items-center justify-center flex-shrink-0',
                      passenger.is_pwd ? 'bg-blue-500 border-blue-500' : 'bg-white'
                    ]">
                      <svg v-if="passenger.is_pwd" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                      </svg>
                    </div>
                    <span>I am a Person with Disability</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Submission & Grading Section (Always visible for clarity) -->
          <div class="mb-8 border-2 border-dashed border-gray-200 rounded-xl p-6 bg-gray-50/50">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-base font-bold text-gray-900 uppercase tracking-tight">Submission & Grading</h2>
              <span :class="['px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider', getStatusClass(activity.status)]">
                {{ getStatusLabel(activity.status) }}
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Grade Card -->
              <div class="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex items-center gap-4">
                <div class="w-12 h-12 bg-pink-50 rounded-full flex items-center justify-center text-pink-500">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Score / Grade</p>
                  <p class="text-2xl font-black text-gray-900">
                    {{ activity.grade !== null ? activity.grade : '-' }}
                    <span class="text-xs text-gray-400 font-medium">/ {{ activity.total_points }} pts</span>
                  </p>
                </div>
              </div>

              <!-- Date Submitted -->
              <div class="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex items-center gap-4">
                <div class="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center text-blue-500">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Submitted At</p>
                  <p class="text-sm font-bold text-gray-900">
                    {{ activity.submitted_at ? formatDateTime(activity.submitted_at) : 'Not submitted yet' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Feedback -->
            <div v-if="activity.feedback" class="mt-6 bg-white p-5 rounded-lg border border-gray-200 shadow-sm">
              <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-2 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
                Feedback
              </p>
              <p class="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap italic">{{ activity.feedback }}</p>
            </div>
            
            <!-- View Work Button -->
            <div v-if="activity.completed" class="mt-6 flex justify-center">
              <button 
                @click="openComparisonModal"
                class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold rounded-lg transition-all shadow-md flex items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                   <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                </svg>
                View Work
              </button>
            </div>
          </div>

          <!-- Start Button -->
          <div class="flex flex-col items-center gap-3 mt-8">
            <button 
              @click="openCodeModal"
              :disabled="!activity.is_active || activity.grade !== null || activity.status === 'submitted' || activity.status === 'graded'"
              :class="[
                'w-full max-w-md py-4 rounded-lg font-bold text-sm uppercase tracking-wider transition-all shadow-md',
                activity.is_active && activity.grade === null
                  ? 'bg-[#f5c842] hover:bg-[#e5b832] text-gray-900' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              ]"
            >
              {{ getButtonText() }}
            </button>
            <p v-if="activity.grade !== null" class="text-[10px] text-gray-400 italic">
              Activity has been graded. You cannot re-submit.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Code Verification Modal -->
      <div
        v-if="showCodeModal"
        class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/80"
        @click.self="closeCodeModal"
      >

      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-8 transform transition-all">
        <!-- Modal Header -->
        <div class="text-center mb-6">
          <div class="mx-auto w-16 h-16 bg-[#f5c842] rounded-full flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-gray-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Enter Activity Code</h3>
          <p class="text-sm text-gray-600">Please enter the code provided by your instructor</p>
        </div>

        <!-- Code Input -->
        <div class="mb-6">
          <input 
            v-model="enteredCode"
            type="text"
            placeholder="Enter code"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-center text-lg font-mono uppercase tracking-widest focus:outline-none focus:border-[#f5c842] transition-colors"
            :class="{ 'border-red-500 animate-shake': showError }"
            @keyup.enter="verifyCode"
            @input="showError = false"
            maxlength="20"
            autocomplete="off"
          />
          
          <!-- Error Message -->
          <div v-if="showError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
            <svg class="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p class="text-sm text-red-600 font-medium">{{ errorMessage }}</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3">
          <button 
            @click="closeCodeModal"
            class="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            :disabled="verifying"
          >
            Cancel
          </button>
          <button 
            @click="verifyCode"
            :disabled="!enteredCode.trim() || verifying"
            class="flex-1 px-4 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :class="[
              enteredCode.trim() && !verifying
                ? 'bg-[#f5c842] hover:bg-[#e5b832] text-gray-900'
                : 'bg-gray-300 text-gray-500'
            ]"
          >
            <span v-if="verifying" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Verifying...
            </span>
            <span v-else>START</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Comparison Modal -->
    <ComparisonModal
      :is-open="showComparison"
      :is-loading="isLoadingBooking"
      :error-message="comparisonError"
      :activity="activity"
      :booking="comparisonBooking"
      :grade="activity.grade"
      @close="showComparison = false"
    />
  </div>
</template>

<script>
import { studentActivityDetailsService } from '@/services/Student/studentActivityDetailsService.js';
import { useBookingStore } from '@/stores/booking';
import ComparisonModal from '@/components/common/ComparisonModal.vue';
import { comparisonService } from '@/services/Student/comparisonService';
import { useUserStore } from '@/stores/user'
import api from '@/services/api/axios';

export default {
  name: 'StudentActivityDetails',
  setup() {
    const userStore = useUserStore()
    return { userStore }
  },
  components: {
    ComparisonModal
  },
  data() {
    return {
      activity: {
        id: null,
        title: '',
        description: '',
        activity_type: '',
        due_date: null,
        total_points: 0,
        section_code: '',
        section_name: '',
        required_trip_type: '',
        required_origin: '',
        required_destination: '',
        required_travel_class: '',
        required_passengers: 0,
        required_children: 0,
        required_infants: 0,
        departure_date: null,
        arrival_date: null,
        status: '',
        is_active: false,
        activity_code: '' // Store the activity code
      },
      instructor: null,
      passengers: [],
      studentEmail: '',
      studentFirstName: '',
      studentLastName: '',
      loading: true,
      error: null,
      
      // Code Modal State
      showCodeModal: false,
      enteredCode: '',
      showError: false,
      errorMessage: '',
      verifying: false,

      // Comparison Modal State
      showComparison: false,
      comparisonBooking: null,
      isLoadingBooking: false,
      comparisonError: null
    }
  },
  computed: {
    fullName() {
      return `${this.studentFirstName} ${this.studentLastName}`.trim() || 'Student';
    },
    initials() {
      const first = this.studentFirstName?.charAt(0) || '';
      const last = this.studentLastName?.charAt(0) || '';
      return (first + last).toUpperCase() || 'ST';
    },
    normalizedTripType() {
      return (this.activity.required_trip_type || '').toLowerCase();
    },
    normalizedTravelClass() {
      return (this.activity.required_travel_class || '').toLowerCase();
    },
    displayPassengers() {
      if (this.passengers && this.passengers.length > 0) {
        console.log('✅ Using passengers from backend:', this.passengers.length);
        return this.passengers;
      }
      
      console.log('ℹ️ No passenger data from backend');
      return [];
    }
  },
  async created() {
    console.log('🔐 Activity Details Component Created');
    
    if (!this.userStore.isAuthenticated) {
      console.error('❌ No token found!');
      this.error = "Authentication required. Please login.";
      this.loading = false;
      
      setTimeout(() => {
        this.$router.push('/login');
      }, 2000);
      return;
    }
    
    // Ensure user profile is loaded (handles cache clears)
    await this.userStore.ensureUserLoaded();

    if (this.userStore.studentProfile) {
      this.studentEmail = this.userStore.studentProfile.email || '';
      this.studentFirstName = this.userStore.studentProfile.first_name || '';
      this.studentLastName = this.userStore.studentProfile.last_name || '';
      console.log('✅ Student data loaded from store');
    }
    
    await this.loadActivityDetails();
  },
  methods: {
    async loadActivityDetails() {
      try {
        this.loading = true;
        this.error = null;
        
        const activityId = this.$route.params.id;
        console.log('\n' + '='.repeat(60));
        console.log('📡 LOADING ACTIVITY DETAILS');
        console.log('='.repeat(60));
        console.log('Activity ID:', activityId);
        
        if (!activityId) {
          throw new Error('No activity ID provided in route');
        }
        
        console.log('🌐 Making API request...');
        const response = await studentActivityDetailsService.getActivityDetails(activityId);
        
        console.log('✅ Response received:', response.data);
        
        if (!response.data || !response.data.activity) {
          throw new Error('Invalid response format from server');
        }
        
        const activityData = response.data.activity;
        
        // Populate activity data
        this.activity = {
          id: activityData.id,
          title: activityData.title || 'Untitled Activity',
          description: activityData.description || '',
          activity_type: activityData.activity_type || 'Flight Booking',
          due_date: activityData.due_date,
          total_points: activityData.total_points || 0,
          section_code: activityData.section_code || '',
          section_name: activityData.section_name || '',
          section_id: activityData.section_id,
          
          // Flight requirements
          required_trip_type: activityData.required_trip_type || '',
          required_origin: activityData.required_origin || '',
          required_destination: activityData.required_destination || '',
          required_travel_class: activityData.required_travel_class || '',
          required_passengers: activityData.required_passengers || 0,
          required_children: activityData.required_children || 0,
          required_infants: activityData.required_infants || 0,
          
          // Dates
          departure_date: activityData.departure_date,
          arrival_date: activityData.arrival_date,
          
          // Status
          status: activityData.status || 'assigned',
          is_active: activityData.is_active || false,
          
          // Activity Code
          activity_code: activityData.activity_code || '',
          
          // Metadata
          assigned_at: activityData.assigned_at,
          submitted_at: activityData.submitted_at,
          grade: activityData.grade,
          feedback: activityData.feedback || '',
          completed: activityData.completed || false,
          created_at: activityData.created_at
        };
        
        console.log('✅ Activity populated with code:', this.activity.activity_code);
        
        // Load instructor
        if (response.data.instructor) {
          this.instructor = response.data.instructor;
          console.log('✅ Instructor loaded:', this.instructor.first_name, this.instructor.last_name);
        }
        
        // Load passengers
        if (response.data.passengers && Array.isArray(response.data.passengers)) {
          this.passengers = response.data.passengers;
          console.log('✅ Passengers loaded:', this.passengers.length);
        } else {
          console.log('ℹ️ No passengers in response');
        }
        
        console.log('='.repeat(60) + '\n');
        
      } catch (error) {
        console.error('\n' + '='.repeat(60));
        console.error('❌ ERROR LOADING ACTIVITY');
        console.error('='.repeat(60));
        console.error('Error:', error);
        
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
          
          switch (error.response.status) {
            case 404:
              this.error = "Activity not found or you don't have access.";
              break;
            case 403:
              this.error = error.response.data?.error || "Access denied.";
              break;
            case 401:
              this.error = "Session expired. Redirecting to login...";
              localStorage.clear();
              setTimeout(() => this.$router.push('/login'), 2000);
              break;
            default:
              this.error = error.response.data?.error || `Error ${error.response.status}`;
          }
        } else if (error.request) {
          this.error = "Cannot connect to server. Please check your connection.";
        } else {
          this.error = error.message || "An unexpected error occurred.";
        }
        
        console.error('='.repeat(60) + '\n');
        
      } finally {
        this.loading = false;
      }
    },
    
    goToHome() {
      this.$router.push('/student/dashboard');
    },

    async openComparisonModal() {
      this.showComparison = true;
      this.comparisonBooking = null;
      this.isLoadingBooking = true;
      this.comparisonError = null;

      try {
        console.log('🔍 Loading comparison data for activity:', this.activity.id);
        const data = await comparisonService.getComparisonData(this.activity.id, this.activity.confirmed_booking_id);
        
        if (data.success) {
          if (data.activity) this.activity = { ...this.activity, ...data.activity };
          this.comparisonBooking = data.booking;
        } else {
          this.comparisonError = data.error || "Could not find booking data for this activity.";
        }
      } catch (error) {
        console.error("Error loading comparison data:", error);
        this.comparisonError = "Failed to connect to the server. Please try again later.";
      } finally {
        this.isLoadingBooking = false;
      }
    },
    
    openCodeModal() {
      if (!this.activity.is_active) return;
      console.log('🔓 Opening code modal');
      this.showCodeModal = true;
      this.enteredCode = '';
      this.showError = false;
      this.errorMessage = '';
      
      // Focus input after modal opens
      this.$nextTick(() => {
        const input = this.$el.querySelector('input[type="text"]');
        if (input) input.focus();
      });
    },
    
    closeCodeModal() {
      console.log('❌ Closing code modal');
      this.showCodeModal = false;
      this.enteredCode = '';
      this.showError = false;
      this.errorMessage = '';
      this.verifying = false;
    },
    
    async verifyCode() {
      if (!this.enteredCode.trim() || this.verifying) return;
      
      this.verifying = true;
      this.showError = false;
      this.errorMessage = '';
      
      console.log('🔍 Verifying code:', this.enteredCode);
      console.log('📋 Expected code:', this.activity.activity_code);
      
      // Simulate slight delay for better UX
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Compare codes (case-insensitive)
      const enteredCodeClean = this.enteredCode.trim().toUpperCase();
      const activityCodeClean = (this.activity.activity_code || '').trim().toUpperCase();
      
      if (enteredCodeClean === activityCodeClean) {
        console.log('✅ Code verified successfully!');
        
        // Update the booking store
        const bookingStore = useBookingStore();
        bookingStore.setActivityCode(this.enteredCode, {
          id: this.activity.id,
          title: this.activity.title
        });
        
        // Store code verification in localStorage (optional)
        const verificationKey = `activity_${this.activity.id}_verified`;
        localStorage.setItem(verificationKey, 'true');
        localStorage.setItem(`${verificationKey}_timestamp`, Date.now().toString());
        
        // Close modal
        this.closeCodeModal();
        
        // Navigate to home route
        this.$router.push('/');
      } else {
        console.log('❌ Invalid code entered');
        this.showError = true;
        this.errorMessage = 'Invalid code. Please check and try again.';
        this.verifying = false;
        
        // Shake animation
        setTimeout(() => {
          this.showError = false;
        }, 3000);
      }
    },
    
    formatDueDate(dateString) {
      if (!dateString) return 'No due date';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'Invalid date';
        return date.toLocaleDateString('en-US', { 
          month: 'long', 
          day: 'numeric', 
          year: 'numeric' 
        });
      } catch (e) {
        return 'Invalid date';
      }
    },
    
    formatFullDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleDateString('en-US', { 
          month: 'long',
          day: 'numeric'
        });
      } catch (e) {
        return 'N/A';
      }
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleDateString('en-US', { 
          month: 'long',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (e) {
        return 'N/A';
      }
    },
    
    getStatusLabel(status) {
      const labels = {
        'assigned': 'Assigned',
        'in_progress': 'In Progress',
        'submitted': 'Submitted',
        'graded': 'Graded'
      };
      return labels[status] || status;
    },
    
    getStatusClass(status) {
      const classes = {
        'assigned': 'bg-gray-100 text-gray-600',
        'in_progress': 'bg-blue-100 text-blue-600',
        'submitted': 'bg-green-100 text-green-700',
        'graded': 'bg-purple-100 text-purple-700'
      };
      return classes[status] || 'bg-gray-50 text-gray-500';
    },
    
    getButtonText() {
      if (this.activity.completed || this.activity.grade !== null || this.activity.status === 'submitted' || this.activity.status === 'graded') {
        return 'Activity Completed';
      }
      if (!this.activity.is_active) return 'Activity Not Active';
      return 'Start';
    }
  }
}
</script>

<style scoped>
/* Shake animation for error state */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}

/* Modal fade-in animation */
.fixed {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Focus styles for input */
input:focus {
  box-shadow: 0 0 0 3px rgba(245, 200, 66, 0.3);
}
</style>