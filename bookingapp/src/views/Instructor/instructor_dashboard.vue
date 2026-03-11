<template>
  <div class="flex flex-col h-screen bg-gray-50 font-sans">
    <!-- Premium Loading Overlay -->
    <LoadingOverlay :loading="isLoading" />
    <div class="bg-gradient-to-r from-pink-500 to-pink-400 text-white px-6 py-2.5 flex items-center justify-between shadow-sm z-20 border-b border-pink-400">
      <div class="flex items-center gap-4">
        <button 
          @click="toggleSidebar" 
          class="p-1.5 hover:bg-pink-600 rounded-md transition-colors focus:outline-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-[#0E8028] rounded-full flex items-center justify-center text-xl shadow-inner">🎓</div>
          <div>
            <h1 class="text-[10px] font-bold uppercase tracking-widest font-sans text-white/90">Cabagan State University</h1>
            <p class="text-[9px] uppercase tracking-tighter opacity-60">Faculty Portal</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4 relative">
        <!-- Notification Bell (Newly Added) -->
        <div class="relative">
          <button 
            @click="toggleNotificationDropdown" 
            class="p-2 hover:bg-pink-600 rounded-full transition-colors relative focus:outline-none group"
            :class="{ 
              'bg-pink-600': notificationDropdownOpen,
              'animate-shake': unseenCount > 0 && !notificationDropdownOpen
            }"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <div v-if="unseenCount > 0" class="absolute -top-0.5 -right-0.5 flex items-center justify-center">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span class="relative flex items-center justify-center min-w-[18px] h-[18px] bg-white text-pink-500 text-[10px] font-black rounded-full border border-pink-500 shadow-sm px-1">
                {{ unseenCount }}
              </span>
            </div>
          </button>

          <!-- Notification Dropdown -->
          <div v-if="notificationDropdownOpen" class="absolute right-0 mt-2 w-72 bg-white rounded-2xl shadow-2xl py-2 z-[60] border border-gray-100 overflow-hidden animate-in slide-in-from-top-2 duration-200">
            <div class="px-4 py-2 border-b border-gray-50 flex items-center justify-between bg-slate-50/50">
              <span class="text-[10px] font-black uppercase tracking-widest text-slate-500">Scheduled Notifications</span>
              <span v-if="allNotifications.length > 0" class="text-[9px] bg-pink-100 text-pink-600 px-1.5 py-0.5 rounded-full font-black uppercase tracking-widest">Today</span>
            </div>
            
            <div class="max-h-80 overflow-y-auto">
              <div v-if="allNotifications.length === 0" class="p-10 text-center">
                <div class="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-3 rotate-3">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                </div>
                <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">No notifications yet</p>
              </div>
              
              <div 
                v-for="s in allNotifications" 
                :key="s.id"
                class="px-4 py-4 hover:bg-slate-50 transition-all border-b border-gray-50 last:border-0 group relative"
                :class="{ 'opacity-85 bg-slate-50/40': s.read }"
              >
                <div class="flex items-start gap-4">
                  <div :class="[
                    'w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 font-bold text-xs shadow-sm transition-transform group-hover:scale-110',
                    s.type === 'missed' ? 'bg-red-50 text-red-500 border border-red-100' : 'bg-emerald-50 text-emerald-600 border border-emerald-100',
                    { 'grayscale opacity-70': s.read }
                  ]">
                    {{ s.sectionName.charAt(0) }}
                  </div>
                  <div class="flex-1 text-left">
                    <div class="flex justify-between items-start mb-0.5">
                      <p class="text-[11px] font-black text-slate-800 uppercase tracking-tight" :class="{ 'text-slate-500': s.read }">{{ s.sectionName }}</p>
                      <div class="flex flex-col items-end gap-1">
                        <span :class="[
                          'text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded',
                          s.type === 'missed' ? 'text-red-400' : 'text-emerald-400',
                          { 'text-slate-400 bg-slate-100': s.read }
                        ]">
                          {{ s.type }}
                        </span>
                        <span v-if="s.read" class="text-[7px] font-bold text-slate-500 uppercase tracking-tighter bg-slate-200/50 px-1 rounded-sm border border-slate-200">Checked</span>
                      </div>
                    </div>
                    <p class="text-[10px] text-slate-500 font-medium leading-normal italic" :class="{ 'text-slate-400': s.read }">
                      {{ s.displayMessage }}
                    </p>
                    <div class="flex items-center gap-2 mt-2">
                       <span class="text-[9px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">{{ formatTimeOnly(s.start_time) }}</span>
                       <span class="text-[9px] font-bold text-slate-300">→</span>
                       <span class="text-[9px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">{{ formatTimeOnly(s.end_time) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="relative">
          <button 
            @click="toggleDropdown" 
            class="flex items-center gap-2 hover:bg-pink-600 p-1.5 rounded-md transition-colors focus:outline-none"
          >
            <span class="text-xs font-medium">{{ userStore.userFullName || 'Instructor' }}</span>
            <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center overflow-hidden border border-pink-300">
               <div class="w-full h-full bg-gray-300 rounded-full flex items-center justify-center text-gray-600 text-xs font-bold uppercase">{{ initials }}</div>
            </div>
          </button>

          <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
             <button @click="router.push('/profile')" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">My Profile</button>
             <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Logout</button>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <div 
        :class="[
          'bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg border-r border-pink-400/20', 
          sidebarOpen ? 'w-56' : 'w-16'
        ]"
      >
        <div class="flex flex-col h-full overflow-y-auto">
           <button class="flex items-center py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/20 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
             </svg>
             <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Home</span>
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
                {{ section.section_name.charAt(0) }}
              </div>
              <span v-show="sidebarOpen" class="ml-3 truncate text-[11px] font-bold tracking-wider uppercase text-white">{{ section.section_name }}</span>
           </div>
        </div>
      </div>

      <div class="flex-1 overflow-auto bg-[#F8FAFC]">
        <div class="p-4 lg:p-8 max-w-7xl mx-auto">
          <!-- Welcome and Breadcrumbs -->
          <div class="mb-8">
            <h2 class="text-2xl font-bold text-slate-800 tracking-tight">Instructor Dashboard</h2>
            <div class="flex items-center gap-2 text-sm text-slate-500 mt-1">
              <span>Main Console</span>
              <span class="text-slate-300">•</span>
              <span class="text-pink-500 font-medium">Overview</span>
            </div>
          </div>

          <!-- Stats Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4 transition-all hover:shadow-md">
              <div class="w-12 h-12 bg-pink-50 rounded-lg flex items-center justify-center text-pink-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Sections</p>
                <h4 class="text-2xl font-bold text-slate-700">{{ sections?.length || 0 }}</h4>
              </div>
            </div>

            <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4 transition-all hover:shadow-md">
              <div class="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center text-emerald-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Students</p>
                <h4 class="text-2xl font-bold text-slate-700">{{ totalStudents }}</h4>
              </div>
            </div>

            <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4 transition-all hover:shadow-md">
              <div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center text-blue-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Activities</p>
                <h4 class="text-2xl font-bold text-slate-700">{{ totalActivities }}</h4>
              </div>
            </div>

            <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4 transition-all hover:shadow-md">
              <div class="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center text-amber-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Last Sync</p>
                <h4 class="text-sm font-bold text-slate-700">{{ lastSyncTime }}</h4>
              </div>
            </div>
          </div>
          

          <!-- Section Controls -->
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <h3 class="text-lg font-bold text-slate-700">Academic Sections</h3>
            
            <div class="flex items-center gap-3 w-full sm:w-auto">
              <div class="relative flex-1 sm:w-64">
                <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </span>
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search sections..." 
                  class="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/20 focus:border-pink-500 transition-all shadow-sm"
                >
              </div>
              <button 
                @click="showModal = true"
                class="bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 shadow-sm transition-all active:scale-95 whitespace-nowrap"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Register New
              </button>
            </div>
          </div>

          <!-- Grid View -->
          <div v-if="!searchQuery || filteredSections.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <!-- Register New Section Card -->
            <div 
              v-if="!searchQuery"
              @click="showModal = true"
              class="group border-2 border-dashed border-slate-200 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer hover:border-pink-500 hover:bg-pink-50 transition-all duration-300 min-h-[260px] bg-white shadow-sm hover:shadow-md"
            >
              <div class="w-16 h-16 bg-slate-50 border-2 border-dashed border-slate-200 rounded-full flex items-center justify-center mb-4 group-hover:border-pink-500 group-hover:bg-white transition-all duration-300">
                <span class="text-3xl text-slate-300 group-hover:text-pink-500 transition-colors">+</span>
              </div>
              <p class="text-slate-500 font-bold uppercase text-xs tracking-widest group-hover:text-pink-600 transition-colors text-center">Register New Section</p>
            </div>

            <div 
              v-for="section in filteredSections" 
              :key="section.id" 
              @click="goToSection(section.id)" 
              class="group bg-white rounded-xl shadow-sm hover:shadow-xl border border-slate-100 overflow-hidden transition-all duration-300 cursor-pointer flex flex-col h-full"
            >
              <div class="p-1">
                <div class="bg-gradient-to-br from-pink-600 to-pink-500 text-white p-4 rounded-lg relative overflow-hidden">
                  <!-- Decorative Element -->
                  <div class="absolute -right-4 -top-4 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
                  
                  <div class="flex justify-between items-start relative z-10">
                    <div>
                      <span class="text-[10px] font-bold uppercase tracking-[0.2em] text-pink-400 mb-1 block">Course Code</span>
                      <h3 class="text-lg font-bold">{{ section.section_code }}</h3>
                    </div>
                    <div class="flex items-center gap-1">
                      <span v-if="!section.is_active" class="bg-red-500/20 text-red-200 text-[10px] px-2 py-0.5 rounded border border-red-500/30 font-bold uppercase">Inactive</span>
                      <button @click.stop="editSection(section)" class="p-1.5 hover:bg-white/10 rounded-md transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  
                  <div class="mt-4 flex items-center gap-3 relative z-10">
                    <div class="w-10 h-10 rounded-full bg-slate-100/10 flex items-center justify-center font-bold text-sm text-pink-400">
                      {{ section.section_name.charAt(0) }}
                    </div>
                    <div>
                      <p class="text-sm font-medium text-slate-100 leading-none mb-1">{{ section.section_name }}</p>
                      <div v-if="section.schedule" class="flex flex-wrap gap-1 mt-1">
                        <template v-if="Array.isArray(parsedSectionSchedule(section.schedule))">
                           <span v-for="(s, i) in parsedSectionSchedule(section.schedule).slice(0, 2)" :key="i" class="text-[9px] bg-white/10 text-white/90 px-1.5 py-0.5 rounded border border-white/10 backdrop-blur-sm font-bold">
                             {{ s.day.substring(0, 2) }} {{ formatTimeOnly(s.start_time) }}
                           </span>
                           <span v-if="parsedSectionSchedule(section.schedule).length > 2" class="text-[9px] text-white/40 self-center font-bold ml-1">+{{ parsedSectionSchedule(section.schedule).length - 2 }} more</span>
                        </template>
                        <p v-else class="text-[11px] text-slate-200 font-medium">{{ formatSchedule(section.schedule) }}</p>
                      </div>
                      <p v-else class="text-[11px] text-white/70 font-medium">No schedule set</p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <p class="text-sm text-slate-500 leading-relaxed line-clamp-2 italic mb-4">
                    {{ section.description || 'Provide a detailed overview of this section to help organize your curriculum.' }}
                  </p>
                </div>

                <div class="pt-4 border-t border-slate-50 flex items-center justify-end">
                  <div class="text-right">
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{{ section.semester }}</p>
                    <p class="text-[10px] font-black text-slate-600">{{ section.activity_count || 0 }} Activities</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-slate-50/50 px-5 py-3 flex items-center justify-between group-hover:bg-pink-50 transition-colors">
                <span class="text-[10px] font-bold text-slate-500 group-hover:text-pink-600 transition-colors flex items-center gap-1.5 uppercase">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  Manage Console
                </span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-300 group-hover:text-pink-500 transition-all transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Empty State (Only shown when searching and no results) -->
          <div v-else-if="searchQuery && filteredSections.length === 0" class="bg-white rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center">
            <div class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-slate-700 mb-1">No sections found</h3>
            <p class="text-slate-500 text-sm max-w-xs mx-auto mb-6">
              {{ searchQuery ? `We couldn't find any sections matching "${searchQuery}".` : "You haven't registered any academic sections yet. Start by creating your first class." }}
            </p>
            <button 
              v-if="!searchQuery"
              @click="showModal = true"
              class="bg-pink-500 hover:bg-pink-600 text-white px-6 py-2.5 rounded-lg text-sm font-bold shadow-lg shadow-pink-200 transition-all active:scale-95 inline-flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Create Your First Section
            </button>
            <button 
              v-else
              @click="searchQuery = ''"
              class="text-pink-500 font-bold text-sm hover:underline"
            >
              Clear search results
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] px-4">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-gradient-to-r from-pink-600 to-pink-500 text-white px-6 py-3 flex justify-between items-center rounded-t-lg">
          <h3 class="text-xs font-bold uppercase tracking-widest">Register New Academic Section</h3>
          <button @click="showModal = false" class="text-white hover:text-pink-100 text-2xl transition-colors">&times;</button>
        </div>

        <form @submit.prevent="submitSection" class="p-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-1.5">Section Designation <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.section_name" type="text" placeholder="e.g., BSIT 3A" class="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm font-medium" required>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Section Code <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.section_code" type="text" placeholder="e.g., IT311" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Semester <span class="text-red-500 font-bold">*</span></label>
              <select v-model="form.semester" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
                <option value="" disabled>Select Semester</option>
                <option value="1st Semester">1st Semester</option>
                <option value="2nd Semester">2nd Semester</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Academic Year <span class="text-red-500 font-bold">*</span></label>
              <select v-model="form.academic_year" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
                <option value="" disabled>Select Year</option>
                <option value="2024-2025">2024-2025</option>
                <option value="2025-2026">2025-2026</option>
                <option value="2026-2027">2026-2027</option>
                <option value="2027-2028">2027-2028</option>
                <option value="2029-2030">2029-2030</option>
              </select>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-2">Schedule(s)</label>
            <div v-for="(sched, index) in form.schedules" :key="index" class="flex gap-2 mb-2 items-center">
              <select v-model="sched.day" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
                <option value="" disabled>Day</option>
                <option value="Monday">Monday</option>
                <option value="Tuesday">Tuesday</option>
                <option value="Wednesday">Wednesday</option>
                <option value="Thursday">Thursday</option>
                <option value="Friday">Friday</option>
                <option value="Saturday">Saturday</option>
                <option value="Sunday">Sunday</option>
              </select>
              <input v-model="sched.start_time" type="time" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
              <span class="text-gray-400 text-xs">-</span>
              <input v-model="sched.end_time" type="time" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
              <button v-if="form.schedules.length > 1" type="button" @click="removeSchedule(index)" class="text-red-400 hover:text-red-500 p-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <button type="button" @click="addSchedule" class="text-pink-500 text-[10px] font-bold uppercase tracking-widest hover:text-pink-600 flex items-center gap-1 mt-1 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
              </svg>
              Add Another Schedule
            </button>
          </div>

          <div class="mb-6">
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Enter course details..." class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none resize-none bg-gray-50"></textarea>
          </div>

          <div class="flex justify-end gap-4 border-t pt-6">
            <button type="button" @click="showModal = false" class="text-gray-400 font-bold uppercase text-xs hover:text-gray-600 transition-colors">Cancel</button>
            <button type="submit" class="px-8 py-3 bg-pink-500 text-white rounded-lg font-black uppercase text-xs shadow-lg active:scale-95 transition-all">Create Section</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Real-time Schedule Alert Modal -->
    <div v-if="showScheduleAlert" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-md px-4 p-20">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in duration-300 border border-white/20">
        <!-- Professional Header -->
        <div class="bg-gradient-to-br from-slate-900 to-slate-800 p-8 text-center relative overflow-hidden">
          <div class="absolute inset-0 bg-pink-500/10 animate-pulse"></div>
          <div class="relative z-10">
            <div class="w-16 h-16 bg-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 rotate-3 shadow-lg shadow-pink-500/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-white text-xl font-black uppercase tracking-widest mb-1">Schedule Alert</h3>
            <p class="text-pink-400 text-[10px] font-bold uppercase tracking-[0.3em]">Cabagan State University • {{ currentTimeDisplay }}</p>
          </div>
        </div>

        <!-- Alert Content -->
        <div class="p-8 text-center bg-white">
          <p class="text-slate-500 text-sm font-medium mb-2 uppercase tracking-tight">You have a Schedule today in</p>
          <h2 class="text-3xl font-black text-slate-800 mb-2 leading-tight">{{ currentAlertSchedule?.sectionName }}</h2>
          <div class="inline-flex flex-center items-center gap-2 bg-pink-50 px-4 py-2 rounded-full border border-pink-100 mb-8">
            <span class="w-2 h-2 bg-pink-500 rounded-full animate-ping"></span>
            <span class="text-pink-600 font-black text-xs uppercase tracking-widest">
              {{ formatTimeOnly(currentAlertSchedule?.start_time) }} - {{ formatTimeOnly(currentAlertSchedule?.end_time) }}
            </span>
          </div>

          <div class="space-y-3">
             <button 
               @click="acknowledgeSchedule" 
               class="w-full py-4 bg-pink-500 hover:bg-pink-600 text-white rounded-2xl font-black uppercase text-xs tracking-[0.2em] shadow-xl shadow-pink-200 transition-all active:scale-[0.98]"
             >
               Dismiss
             </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
// Import the new API service
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import LoadingOverlay from '@/components/instructor/LoadingOverlay.vue'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useModalStore } from '@/stores/modal'

const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const modalStore = useModalStore()

const isLoading = ref(false)
const sidebarOpen = ref(false) 
const dropdownOpen = ref(false)
const showModal = ref(false)
const sections = ref([])
const searchQuery = ref('')
const lastSyncTime = ref(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))

// Notification & Alert State - Persisted via localStorage (User-Specific)
const dismissedSchedules = ref(new Set())
const shownAlerts = ref(new Set())
const readNotificationIds = ref(new Set())
const showScheduleAlert = ref(false)
const notificationDropdownOpen = ref(false)
const currentAlertSchedule = ref(null)
const currentTimeDisplay = ref(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
let scheduleInterval = null

// Helper to get user-specific storage keys
const getStorageKey = (base) => {
  const userId = userStore.user?.id || 'anon'
  return `${base}_${userId}`
}

// Function to load user-specific state
const loadUserState = () => {
  const userId = userStore.user?.id
  if (!userId) return

  dismissedSchedules.value = new Set(JSON.parse(localStorage.getItem(getStorageKey('dismissedSchedules')) || '[]'))
  shownAlerts.value = new Set(JSON.parse(localStorage.getItem(getStorageKey('shownAlerts')) || '[]'))
  readNotificationIds.value = new Set(JSON.parse(localStorage.getItem(getStorageKey('readNotificationIds')) || '[]'))
}

// Watchers for persistence - including user-specific tagging
watch(dismissedSchedules, (newVal) => {
  if (userStore.user?.id) {
    localStorage.setItem(getStorageKey('dismissedSchedules'), JSON.stringify([...newVal]))
  }
}, { deep: true })

watch(shownAlerts, (newVal) => {
  if (userStore.user?.id) {
    localStorage.setItem(getStorageKey('shownAlerts'), JSON.stringify([...newVal]))
  }
}, { deep: true })

watch(readNotificationIds, (newVal) => {
  if (userStore.user?.id) {
    localStorage.setItem(getStorageKey('readNotificationIds'), JSON.stringify([...newVal]))
  }
}, { deep: true })

// Watch for user changes (login/logout/switch) to reload state
watch(() => userStore.user?.id, (newUserId) => {
  if (newUserId) loadUserState()
})

// Form state for creating a new section
const form = ref({
  section_name: '',
  section_code: '',
  semester: '',
  academic_year: '',
  schedules: [{ day: '', start_time: '', end_time: '' }],
  description: ''
})

const addSchedule = () => {
  form.value.schedules.push({ day: '', start_time: '', end_time: '' })
}

const removeSchedule = (index) => {
  form.value.schedules.splice(index, 1)
}

const formatTimeOnly = (t) => {
  if (!t) return ''
  const [h, m] = t.split(':')
  const hour = parseInt(h)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const h12 = hour % 12 || 12
  return `${h12}:${m} ${ampm}`
}

const parsedSectionSchedule = (scheduleData) => {
  if (!scheduleData) return null
  try {
    const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
    if (Array.isArray(schedules) && schedules.length > 0) return schedules
  } catch (e) {}
  return null
}

const formatSchedule = (scheduleData) => {
  if (!scheduleData) return 'No schedule set'
  
  // Handle new structured format if it comes back as string from backend
  try {
    const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
    if (Array.isArray(schedules)) {
      if (schedules.length === 0) return 'No schedule set'
      return schedules.map(s => {
        const dayShort = s.day.substring(0, 3)
        const formatTime = (t) => {
          if (!t) return ''
          const [h, m] = t.split(':')
          const hour = parseInt(h)
          const ampm = hour >= 12 ? 'PM' : 'AM'
          const h12 = hour % 12 || 12
          return `${h12}:${m} ${ampm}`
        }
        return `${dayShort} ${formatTime(s.start_time)}-${formatTime(s.end_time)}`
      }).join(', ')
    }
  } catch (e) {
    // Fallback to plain text if not JSON
  }
  
  return scheduleData
}

// Filtered sections based on search query
const filteredSections = computed(() => {
  if (!searchQuery.value) return sections.value
  const query = searchQuery.value.toLowerCase()
  return sections.value.filter(s => 
    s.section_name.toLowerCase().includes(query) || 
    s.section_code.toLowerCase().includes(query) ||
    (s.semester && s.semester.toLowerCase().includes(query)) ||
    (s.academic_year && s.academic_year.toLowerCase().includes(query))
  )
})

// Statistics
const totalStudents = computed(() => {
  return sections.value.reduce((acc, s) => acc + (s.student_count || 0), 0)
})

const totalActivities = computed(() => {
  return sections.value.reduce((acc, s) => acc + (s.activity_count || 0), 0)
})

const currentFullTime = ref(new Date())

// Helper to find the most recent occurrence of a Weekly slot (e.g., "Monday 10:00")
const getMostRecentOccurrence = (dayName, timeStr, now = new Date()) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const shortDays = ['su', 'mo', 'tu', 'we', 'th', 'fr', 'sa']
  
  let targetDayIndex = days.findIndex(d => d.toLowerCase() === dayName.toLowerCase())
  if (targetDayIndex === -1) {
    targetDayIndex = shortDays.findIndex(d => d === dayName.toLowerCase().substring(0, 2))
  }
  
  if (targetDayIndex === -1) return null
  
  const [hours, minutes] = timeStr.split(':').map(Number)
  const occurrence = new Date(now)
  
  // Set time
  occurrence.setHours(hours, minutes, 0, 0)
  
  // Adjust day to match the provided dayName
  const currentDayIndex = now.getDay()
  const daysDiff = (currentDayIndex - targetDayIndex + 7) % 7
  occurrence.setDate(now.getDate() - daysDiff)
  
  // If the occurrence calculated is in the future compared to 'now', it must be the previous week's occurrence
  if (occurrence > now) {
    occurrence.setDate(occurrence.getDate() - 7)
  }
  
  return occurrence
}

const allNotifications = computed(() => {
  const now = currentFullTime.value
  const notifications = []
  
  // Detect and Add Missed Schedules using precise occurrence timestamps
  sections.value.forEach(section => {
    const schedules = parsedSectionSchedule(section.schedule)
    if (schedules) {
      schedules.forEach(s => {
        const occurrence = getMostRecentOccurrence(s.day, s.start_time, now)
        if (!occurrence) return
        
        // Window check: We show missed schedules from the last 48 hours
        const diffMs = now - occurrence
        const isPast = occurrence < now
        const isWithinWindow = diffMs < 48 * 60 * 60 * 1000 // 48-hour history window
        
        if (isPast && isWithinWindow) {
          const scheduleId = `${section.id}-${s.day}-${s.start_time}`
          // Stable ID based on the date this specific occurrence happened
          const dateStr = occurrence.toDateString().replace(/\s+/g, '_')
          const notificationId = `${scheduleId}_${dateStr}_missed`
          
          if (!dismissedSchedules.value.has(scheduleId)) {
            notifications.push({
              ...s,
              type: 'missed',
              sectionId: section.id,
              sectionName: section.section_name,
              scheduleId,
              id: notificationId,
              read: readNotificationIds.value.has(notificationId),
              occurrenceTime: occurrence,
              displayMessage: `You missed your ${formatTimeOnly(s.start_time)} session.`
            })
          }
        }
      })
    }
  })
  
  // Show most recent first
  return notifications.sort((a, b) => b.occurrenceTime - a.occurrenceTime)
})

const unseenCount = computed(() => {
  return allNotifications.value.filter(n => !n.read).length
})

// Computed: User initials for the avatar
const initials = computed(() => {
  const u = userStore.user?.username || userStore.user?.first_name || 'I'
  return u[0].toUpperCase()
})

// UI Toggles
const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { 
  dropdownOpen.value = !dropdownOpen.value
  if (dropdownOpen.value) notificationDropdownOpen.value = false
}
const toggleNotificationDropdown = () => {
  notificationDropdownOpen.value = !notificationDropdownOpen.value
  if (notificationDropdownOpen.value) {
    dropdownOpen.value = false
    // Mark all current as read
    allNotifications.value.forEach(n => readNotificationIds.value.add(n.id))
    readNotificationIds.value = new Set(readNotificationIds.value)
  }
}

// Navigation logic for Section Details
const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

// Edit Section logic - Redirect to Settings
const editSection = (section) => {
  router.push(`/instructor/section/${section.id}/settings`)
}

// Logout logic
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const dismissSchedule = (id) => {
  dismissedSchedules.value.add(id)
}

const acknowledgeSchedule = () => {
  if (currentAlertSchedule.value) {
    const scheduleId = `${currentAlertSchedule.value.sectionId}-${currentAlertSchedule.value.day}-${currentAlertSchedule.value.start_time}`
    dismissedSchedules.value.add(scheduleId)
    // Force a re-render/save
    dismissedSchedules.value = new Set(dismissedSchedules.value)
  }
  showScheduleAlert.value = false
}

const checkScheduleAlerts = () => {
  const now = new Date()
  currentFullTime.value = now // Update reactive time for notifications
  currentTimeDisplay.value = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  
  const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const today = days[now.getDay()]

  sections.value.forEach(section => {
    const schedules = parsedSectionSchedule(section.schedule)
    if (schedules) {
      schedules.forEach(s => {
        if (s.day === today && s.start_time === currentTime) {
          const alertId = `${section.id}-${s.day}-${s.start_time}-${now.toDateString()}`
          if (!shownAlerts.value.has(alertId)) {
            currentAlertSchedule.value = {
              ...s,
              sectionId: section.id,
              sectionName: section.section_name,
              scheduleId: alertId
            }
            showScheduleAlert.value = true
            shownAlerts.value.add(alertId)
            shownAlerts.value = new Set(shownAlerts.value)
            // Increment unseenCount for the alert itself? 
            // The user said "if missed ... OR click i understand ... then show the alert the new alert like ther is a number"
            // Wait, if it alerts, does it count as unseen yet? 
            // "if missed can you add a bell ... if click i understand when alert show then show the alert the new alert like ther is a number"
            // So yes, after modal it adds to bell.
            
            console.log('SCHEDULE ALERT:', currentAlertSchedule.value.sectionName)
          }
        }
      })
    }
  })
}

/**
 * Action: Fetch data from Backend
 */
const fetchInstructorData = async () => {
  isLoading.value = true
  try {
    const data = await instructorDashboardService.getDashboard();
    
    // Update local refs with data from Django
    sections.value = data.sections;
    if (data.user) {
      userStore.user = data.user;
    }
    // Update sync time
    lastSyncTime.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (error) {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // If unauthorized, boot to login
      handleLogout();
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * Action: Submit new section
 */
const submitSection = async () => {
  try {
    const payload = {
      ...form.value,
      schedule: JSON.stringify(form.value.schedules)
    }
    await instructorDashboardService.createSection(payload);
    
    // Reset UI state
    showModal.value = false;
    form.value = { 
      section_name: '', section_code: '', semester: '', 
      academic_year: '', schedules: [{ day: '', start_time: '', end_time: '' }], description: '' 
    };
    
    // Refresh the list immediately
    await fetchInstructorData();
    notificationStore.success("Section created successfully!");
  } catch (error) {
    const serverMessage = error.response?.data?.error || "Check if Section Code is unique.";
    notificationStore.error("Backend Error: " + serverMessage);
  }
};

// Lifecycle: Initialize data
onMounted(async () => {
  await userStore.ensureUserLoaded();
  loadUserState(); // Ensure state is loaded for the current user
  await fetchInstructorData();
  
  // Start schedule alert checker (High Precision - 1s)
  checkScheduleAlerts() // Initial check
  scheduleInterval = setInterval(checkScheduleAlerts, 1000)
})

onUnmounted(() => {
  if (scheduleInterval) clearInterval(scheduleInterval)
})
</script>

<style scoped>
@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  20% { transform: rotate(8deg); }
  40% { transform: rotate(-8deg); }
  60% { transform: rotate(8deg); }
  80% { transform: rotate(-8deg); }
}

.animate-shake {
  animation: shake 0.6s cubic-bezier(.36,.07,.19,.97) both;
  animation-iteration-count: infinite;
  transform-origin: center top;
}
</style>
