<template>
  <div class="h-[calc(100vh-100px)] flex flex-col bg-gray-100 poppins">
    <!-- Header / Toolbar -->
    <div class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm z-10">
      <div>
        <h1 class="text-xl font-black text-[#002D1E] tracking-tight flex items-center gap-3">
          <i class="ph ph-broadcast text-[#fe3787] text-2xl animate-pulse"></i>
          Live Simulation Command Center
        </h1>
        <p class="text-[10px] text-gray-400 uppercase font-black tracking-widest mt-1">Real-time aircraft tracking & simulation telemetry</p>
      </div>

      <div class="flex items-center gap-6">
        <!-- Live Status Indicators -->
        <div class="hidden md:flex items-center gap-4 border-r border-gray-100 pr-6 mr-2">
          <div class="text-right">
            <p class="text-[9px] text-gray-400 uppercase font-bold leading-none">Status</p>
            <p class="text-xs font-black text-emerald-500">SYSTEM ONLINE</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-emerald-50 border border-emerald-100 flex items-center justify-center">
            <div class="w-3 h-3 bg-emerald-500 rounded-full animate-ping"></div>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <div class="bg-gray-50 border border-gray-200 rounded-[1px] px-4 py-2 flex items-center gap-3">
            <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Active Flights:</span>
            <span class="text-sm font-black text-[#fe3787]">{{ activeFlights.length }}</span>
          </div>
          
          <button 
            @click="fetchActiveFlights" 
            class="p-2.5 bg-white border border-gray-200 rounded-[1px] hover:bg-gray-50 transition-all text-[#002D1E] shadow-sm flex items-center gap-2 group"
            :disabled="mapLoading"
          >
            <i class="ph ph-arrows-clockwise text-lg" :class="{'animate-spin text-[#fe3787]': mapLoading}"></i>
            <span class="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Refresh Data</span>
          </button>

          <button 
            @click="toggleFullScreen" 
            class="p-2.5 bg-[#002D1E] text-white rounded-[1px] hover:bg-black transition-all shadow-lg flex items-center gap-2"
          >
            <i class="ph ph-corners-out text-lg"></i>
            <span class="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Fullscreen Radar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content: Map + Sidebar -->
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Sidebar Information (Optional, for more detail) -->
      <div v-if="showSidebar" class="w-80 bg-white border-r border-gray-200 overflow-y-auto hidden xl:block shadow-xl z-20">
        <div class="p-6 space-y-6">
          <h2 class="text-sm font-black text-[#002D1E] uppercase tracking-widest border-b border-gray-100 pb-4">Flight Manifest</h2>
          
          <div v-if="activeFlights.length === 0" class="py-12 text-center">
             <i class="ph ph-airplane-slash text-4xl text-gray-100 mb-4"></i>
             <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">No Active Simulations</p>
          </div>
          
          <div v-for="flight in activeFlights" :key="flight.id" 
               @click="centerOnFlight(flight)"
               class="p-4 border border-gray-100 rounded-[1px] hover:border-[#fe3787] hover:shadow-md transition-all cursor-pointer group bg-gray-50/50">
            <div class="flex justify-between items-start mb-3">
              <div>
                <p class="text-xs font-black text-[#002D1E] group-hover:text-[#fe3787] transition-colors">{{ flight.flight_number }}</p>
                <p class="text-[9px] text-gray-400 font-bold uppercase">{{ flight.airline }}</p>
              </div>
              <span class="px-2 py-0.5 rounded-[1px] text-[8px] font-black uppercase bg-emerald-100 text-emerald-700">IN-FLIGHT</span>
            </div>
            <div class="flex items-center justify-between text-[10px] font-bold poppins">
              <span class="text-gray-500">{{ flight.origin.code }}</span>
              <div class="flex-1 mx-2 h-[1px] bg-gray-200 relative">
                <i class="ph ph-airplane-tilt absolute -top-1.5 left-1/2 -translate-x-1/2 text-[10px] text-[#fe3787]"></i>
              </div>
              <span class="text-gray-500">{{ flight.destination.code }}</span>
            </div>
            <div class="mt-4 w-full h-1 bg-gray-100 rounded-full overflow-hidden">
               <div class="h-full bg-[#fe3787] transition-all duration-1000" :style="{ width: Math.round(getFlightProgress(flight) * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Map Container -->
      <div class="flex-1 relative group" ref="mapCardRef">
        <div ref="mapContainer" class="absolute inset-0 z-0"></div>
        
        <!-- Toggle Manifest Button -->
        <button @click="showSidebar = !showSidebar" 
                class="absolute left-4 top-4 z-[400] bg-white border border-gray-200 p-2 rounded-[1px] shadow-lg hover:bg-gray-50 transition-all text-[#002D1E]">
          <i class="ph" :class="showSidebar ? 'ph-caret-double-left' : 'ph-caret-double-right'"></i>
        </button>

        <!-- Map Legend -->
        <div class="absolute bottom-6 left-6 z-[400] bg-white/90 backdrop-blur-md border border-gray-200 p-4 rounded-[1px] shadow-2xl space-y-3 min-w-[200px]">
          <h4 class="text-[10px] font-black text-[#002D1E] uppercase tracking-widest border-b border-gray-100 pb-2">Radar Legend</h4>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-[#fe3787]"></span>
            <span class="text-[10px] font-bold text-gray-600 uppercase">Active Aircraft</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-[2px] bg-[#fe3787] border-dashed border-t border-b"></span>
            <span class="text-[10px] font-bold text-gray-600 uppercase">Flight Path</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
            <span class="text-[10px] font-bold text-gray-600 uppercase">System Sync</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '@/services/admin/api'

// Leaflet fix for icons
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

// State
const mapContainer = ref(null)
const mapCardRef = ref(null)
const mapLoading = ref(false)
const showSidebar = ref(true)
const activeFlights = ref([])
const isMapFullScreen = ref(false)

// Map instances
let mapInstance = null
let flightMarkers = []
let flightPolylines = []
let animationInterval = null
let mapRefreshInterval = null

// Methods
const fetchActiveFlights = async () => {
  mapLoading.value = true
  try {
    const res = await api.get('/dashboard/active_flights_map/')
    activeFlights.value = res.data || []
    if (mapInstance) {
      updateMapMarkers()
    } else {
      await nextTick()
      initMap()
    }
    startFlightAnimation()
  } catch (err) {
    console.error('Map data fetch error:', err)
  } finally {
    mapLoading.value = false
  }
}

const initMap = () => {
  if (!mapContainer.value || mapInstance) return

  mapInstance = L.map(mapContainer.value, {
    center: [12.8797, 121.7740], // Centered on Philippines
    zoom: 6,
    zoomControl: false,
    attributionControl: false
  })

  // Use a professional Dark Matter or Light theme for the radar look
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19
  }).addTo(mapInstance)

  L.control.zoom({ position: 'topright' }).addTo(mapInstance)
  
  updateMapMarkers()
}

const updateMapMarkers = () => {
  if (!mapInstance) return

  // Store existing popup states if any
  const openPopups = []
  flightMarkers.forEach(m => {
    if (m.isPopupOpen()) {
       // We'll try to find the flight number from the marker's flight data
       // For now, let's just clear and rebuild for simplicity
    }
  })

  // Clear existing
  flightMarkers.forEach(m => m.remove())
  flightPolylines.forEach(p => p.remove())
  flightMarkers = []
  flightPolylines = []

  activeFlights.value.forEach(flight => {
    const origin = [flight.origin.lat, flight.origin.lng]
    const dest = [flight.destination.lat, flight.destination.lng]

    // Draw Route Line
    const polyline = L.polyline([origin, dest], {
      color: '#fe3787',
      weight: 2,
      dashArray: '5, 8',
      opacity: 0.4
    }).addTo(mapInstance)
    flightPolylines.push(polyline)

    // Calculate actual position based on flight progress
    const t = getFlightProgress(flight)
    const aircraftPos = [
      origin[0] + (dest[0] - origin[0]) * t,
      origin[1] + (dest[1] - origin[1]) * t
    ]

    const bearing = calculateBearing(flight.origin.lat, flight.origin.lng, flight.destination.lat, flight.destination.lng)
    const progressPct = Math.round(t * 100)
    
    // Custom Aircraft Icon
    const planeIcon = L.divIcon({
      html: `<div class="relative aircraft-icon-wrapper" style="transform: rotate(${bearing - 45}deg)">
               <i class="ph ph-airplane-tilt text-[#fe3787] text-3xl drop-shadow-2xl"></i>
               <div class="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full border-2 border-white bg-emerald-500 animate-pulse"></div>
             </div>`,
      className: 'custom-plane-icon',
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    })

    const depStr = new Date(flight.departure_time).toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' })
    const arrStr = new Date(flight.arrival_time).toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' })

    const marker = L.marker(aircraftPos, { icon: planeIcon })
      .addTo(mapInstance)
      .bindPopup(`
        <div class="poppins p-2 min-w-[180px]">
          <div class="flex justify-between items-center mb-2">
            <span class="font-black text-[#002D1E] text-sm">${flight.flight_number}</span>
            <span class="text-[8px] font-black text-[#fe3787] uppercase">${progressPct}% COMPLETE</span>
          </div>
          <p class="text-[9px] text-gray-400 uppercase font-black leading-none mb-3">${flight.airline}</p>
          
          <div class="grid grid-cols-2 gap-4 border-t border-gray-100 pt-3">
             <div>
                <p class="text-[7px] text-gray-400 uppercase font-bold tracking-widest">Departure</p>
                <p class="text-[10px] font-black">${flight.origin.code}</p>
                <p class="text-[8px] text-gray-500 font-bold">${depStr}</p>
             </div>
             <div class="text-right">
                <p class="text-[7px] text-gray-400 uppercase font-bold tracking-widest">Arrival</p>
                <p class="text-[10px] font-black">${flight.destination.code}</p>
                <p class="text-[8px] text-gray-500 font-bold">${arrStr}</p>
             </div>
          </div>
          
          <div class="mt-3 flex items-center justify-between gap-2">
             <div class="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-[#fe3787]" style="width: ${progressPct}%"></div>
             </div>
          </div>
        </div>
      `, {
        className: 'custom-radar-popup',
        closeButton: false
      })
    
    // Store flight info on marker for centering
    marker.customFlightInfo = flight
    flightMarkers.push(marker)
  })

  // Fit bounds initially if we have flights and map just loaded
  if (flightMarkers.length > 0 && !animationInterval) {
    const group = new L.featureGroup(flightPolylines)
    mapInstance.fitBounds(group.getBounds().pad(0.2))
  }
}

const getFlightProgress = (flight) => {
  const now = Date.now()
  const dep = new Date(flight.departure_time).getTime()
  const arr = new Date(flight.arrival_time).getTime()
  if (now <= dep) return 0
  if (now >= arr) return 1
  return (now - dep) / (arr - dep)
}

const calculateBearing = (startLat, startLng, endLat, endLng) => {
  const startLatRad = startLat * Math.PI / 180
  const startLngRad = startLng * Math.PI / 180
  const endLatRad = endLat * Math.PI / 180
  const endLngRad = endLng * Math.PI / 180
  const y = Math.sin(endLngRad - startLngRad) * Math.cos(endLatRad)
  const x = Math.cos(startLatRad) * Math.sin(endLatRad) -
    Math.sin(startLatRad) * Math.cos(endLatRad) * Math.cos(endLngRad - startLngRad)
  return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360
}

const centerOnFlight = (flight) => {
  const t = getFlightProgress(flight)
  const origin = [flight.origin.lat, flight.origin.lng]
  const dest = [flight.destination.lat, flight.destination.lng]
  const pos = [
    origin[0] + (dest[0] - origin[0]) * t,
    origin[1] + (dest[1] - origin[1]) * t
  ]
  mapInstance.flyTo(pos, 8, { duration: 1.5 })
  
  // Find marker and open popup
  const marker = flightMarkers.find(m => m.customFlightInfo?.id === flight.id)
  if (marker) marker.openPopup()
}

const startFlightAnimation = () => {
  if (animationInterval) clearInterval(animationInterval)
  if (mapRefreshInterval) clearInterval(mapRefreshInterval)
  
  animationInterval = setInterval(updateMapMarkers, 30000)
  mapRefreshInterval = setInterval(fetchActiveFlights, 60000)
}

const toggleFullScreen = () => {
  if (mapCardRef.value.requestFullscreen) {
    mapCardRef.value.requestFullscreen()
  }
}

const handleFullScreenChange = () => {
  isMapFullScreen.value = !!document.fullscreenElement
  if (mapInstance) {
    setTimeout(() => mapInstance.invalidateSize(), 100)
  }
}

onMounted(() => {
  fetchActiveFlights()
  document.addEventListener('fullscreenchange', handleFullScreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullScreenChange)
  if (animationInterval) clearInterval(animationInterval)
  if (mapRefreshInterval) clearInterval(mapRefreshInterval)
  if (mapInstance) mapInstance.remove()
})
</script>

<style>
.poppins {
  font-family: 'Poppins', sans-serif;
}

/* Custom Radar Popup Styles */
.custom-radar-popup .leaflet-popup-content-wrapper {
  background: white !important;
  color: #002D1E !important;
  border-radius: 1px !important;
  padding: 0 !important;
  border: 1px solid #eee;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

.custom-radar-popup .leaflet-popup-content {
  margin: 0 !important;
}

.custom-radar-popup .leaflet-popup-tip {
  background: white !important;
}

/* Hide leaflet branding */
.leaflet-control-attribution {
  display: none !important;
}

.aircraft-icon-wrapper {
  transition: all 0.3s ease;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #eee;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #fe3787;
}
</style>
