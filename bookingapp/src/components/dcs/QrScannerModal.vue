<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[92vh]">

      <!-- Header -->
      <div class="bg-pink-500 px-6 py-4 flex justify-between items-center shrink-0">
        <div>
          <h3 class="text-white font-bold text-base flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 9V6a3 3 0 013-3h3M15 3h3a3 3 0 013 3v3M3 15v3a3 3 0 003 3h3M15 21h3a3 3 0 003-3v-3"/>
              <rect x="7" y="7" width="10" height="10" rx="1"/>
            </svg>
            QR Code Scanner
          </h3>
          <p class="text-pink-100 text-xs mt-0.5">Scan the passenger's E-Ticket QR code</p>
        </div>
        <button @click="handleClose" class="text-white/80 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-pink-600/50">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="p-5 overflow-y-auto flex-1 space-y-4">

        <!-- Tab Switcher: Camera / Manual -->
        <div class="flex bg-gray-100 rounded-lg p-1 gap-1">
          <button
            @click="switchToCamera"
            :class="[
              'flex-1 py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5',
              activeTab === 'camera'
                ? 'bg-white text-pink-600 shadow-sm'
                : 'text-gray-400 hover:text-gray-600'
            ]"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
            </svg>
            Camera Scan
          </button>
          <button
            @click="switchToManual"
            :class="[
              'flex-1 py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5',
              activeTab === 'manual'
                ? 'bg-white text-pink-600 shadow-sm'
                : 'text-gray-400 hover:text-gray-600'
            ]"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            Type PNR
          </button>
        </div>

        <!-- ===================== CAMERA TAB ===================== -->
        <div v-show="activeTab === 'camera'">
          <!-- Camera Viewfinder -->
          <div class="relative rounded-lg overflow-hidden bg-black aspect-[4/3]">
            <div id="qr-reader" class="w-full h-full"></div>

            <!-- Scanning Overlay -->
            <div v-if="cameraActive && !scanResult" class="absolute inset-0 pointer-events-none">
              <div class="absolute top-4 left-4 w-8 h-8 border-t-3 border-l-3 border-pink-400 rounded-tl-lg"></div>
              <div class="absolute top-4 right-4 w-8 h-8 border-t-3 border-r-3 border-pink-400 rounded-tr-lg"></div>
              <div class="absolute bottom-4 left-4 w-8 h-8 border-b-3 border-l-3 border-pink-400 rounded-bl-lg"></div>
              <div class="absolute bottom-4 right-4 w-8 h-8 border-b-3 border-r-3 border-pink-400 rounded-br-lg"></div>
              <div class="absolute inset-x-6 h-0.5 bg-gradient-to-r from-transparent via-pink-500 to-transparent animate-scan-line rounded-full"></div>
              <div class="absolute bottom-2 inset-x-0 text-center">
                <span class="bg-black/60 text-white text-[10px] font-semibold px-3 py-1 rounded-full">
                  Point camera at QR code
                </span>
              </div>
            </div>

            <!-- Camera not started placeholder -->
            <div v-if="!cameraActive && !cameraError && !scanResult" class="absolute inset-0 flex flex-col items-center justify-center bg-gray-900 text-white/60">
              <div class="w-6 h-6 border-2 border-white/40 border-t-pink-400 rounded-full animate-spin mb-3"></div>
              <span class="text-xs font-medium">Starting camera...</span>
            </div>

            <!-- Camera error -->
            <div v-if="cameraError" class="absolute inset-0 flex flex-col items-center justify-center bg-gray-900 text-white/70 px-6">
              <svg class="w-10 h-10 text-red-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>
              </svg>
              <span class="text-sm font-semibold text-center mb-1">Camera Unavailable</span>
              <span class="text-[11px] text-center text-white/50 mb-4">{{ cameraError }}</span>
              <button @click="switchToManual" class="bg-pink-500 hover:bg-pink-600 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors">
                Use Manual Entry Instead
              </button>
            </div>
          </div>

          <!-- Scan success feedback -->
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
          >
            <div v-if="scanResult" class="mt-3 bg-green-50 border border-green-200 rounded-lg px-4 py-3 flex items-center gap-3">
              <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <div class="min-w-0">
                <div class="text-xs font-bold text-green-700">QR Code Scanned!</div>
                <div class="text-xs text-green-600 font-mono truncate">Value: {{ scanResult }}</div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- ===================== MANUAL TAB ===================== -->
        <div v-show="activeTab === 'manual'">
          <div class="border-2 border-dashed border-pink-200 bg-pink-50/30 rounded-lg p-5 text-center">
            <div class="text-3xl mb-2 opacity-40">⌨️</div>
            <p class="text-xs text-gray-500 mb-4">
              Type the 6-character PNR from the passenger's<br>printed itinerary or phone screen.
            </p>
            <div class="max-w-[220px] mx-auto">
              <input
                type="text"
                v-model="manualInput"
                @keyup.enter="performManualScan"
                placeholder="e.g. YWSQEU"
                maxlength="20"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 text-lg font-mono font-bold text-center text-gray-900 tracking-[0.25em] uppercase focus:ring-2 focus:ring-pink-400 focus:border-pink-400 outline-none transition-all"
                :disabled="isLooking"
                ref="manualInputRef"
              >
            </div>
            <button
              @click="performManualScan"
              :disabled="!manualInput.trim() || isLooking"
              class="mt-3 bg-pink-500 hover:bg-pink-600 disabled:bg-gray-300 text-white text-xs font-bold px-5 py-2.5 rounded-lg transition-colors"
            >
              Look Up
            </button>
          </div>
        </div>

        <!-- ===================== LOADING ===================== -->
        <div v-if="isLooking" class="flex items-center justify-center gap-3 py-3">
          <div class="w-5 h-5 border-2 border-pink-500 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm font-semibold text-pink-600">Looking up passenger...</span>
        </div>

        <!-- ===================== ERROR ===================== -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="-translate-y-1 opacity-0"
          enter-to-class="translate-y-0 opacity-100"
        >
          <div v-if="lookupError" class="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <span class="text-red-500 text-lg shrink-0">❌</span>
            <div>
              <div class="text-sm font-bold text-red-700">Not Found</div>
              <div class="text-xs text-red-500 mt-0.5">{{ lookupError }}</div>
              <button @click="resetAndRescan" class="text-xs font-bold text-red-600 underline mt-2 hover:text-red-700">
                Scan Again
              </button>
            </div>
          </div>
        </Transition>

        <!-- ===================== RESULTS ===================== -->
        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="opacity-0 translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
        >
          <div v-if="passengers.length > 0" class="space-y-2">
            <div class="flex items-center gap-2 mb-1">
              <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span class="text-xs font-bold text-green-700">
                {{ passengers.length }} passenger{{ passengers.length > 1 ? 's' : '' }} found
              </span>
            </div>

            <div
              v-for="p in passengers"
              :key="p.booking_detail_id"
              class="border border-gray-200 rounded-lg overflow-hidden hover:border-pink-300 transition-all cursor-pointer group"
              @click="selectPassenger(p)"
            >
              <div class="px-4 py-3 flex items-center justify-between">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-9 h-9 bg-pink-100 rounded-full flex items-center justify-center text-pink-600 font-bold text-sm shrink-0">
                    {{ p.passenger_name?.charAt(0) || '?' }}
                  </div>
                  <div class="min-w-0">
                    <div class="text-sm font-bold text-gray-900 group-hover:text-pink-600 transition-colors truncate">
                      {{ p.passenger_name }}
                    </div>
                    <div class="text-[11px] text-gray-400 flex items-center gap-1.5 flex-wrap">
                      <span class="font-mono font-semibold">{{ p.pnr }}</span>
                      <span>·</span>
                      <span>Seat {{ p.seat || 'TBA' }}</span>
                      <span>·</span>
                      <span :class="isCheckedIn(p) ? 'text-green-600 font-semibold' : 'text-amber-500 font-semibold'">
                        {{ isCheckedIn(p) ? '✅ Checked-In' : '⏳ Pending' }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="shrink-0 ml-2">
                  <svg v-if="!isCheckedIn(p)" class="w-5 h-5 text-pink-400 group-hover:text-pink-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>
                  </svg>
                  <span v-else class="text-[10px] text-green-600 font-bold">Done</span>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Footer -->
      <div class="px-6 py-3 bg-gray-50 border-t border-gray-200 shrink-0 flex justify-end">
        <button @click="handleClose" class="px-4 py-2 rounded-lg text-gray-500 font-semibold hover:bg-gray-100 transition-colors text-sm">
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { Html5Qrcode } from 'html5-qrcode'
import { dcsService } from '@/services/api/dcsService'

const props = defineProps({
  scheduleId: { type: [String, Number], required: true }
})

const emit = defineEmits(['close', 'passenger-selected'])

// State
const activeTab = ref('camera')
const manualInput = ref('')
const manualInputRef = ref(null)

// Camera
const cameraActive = ref(false)
const cameraError = ref(null)
let html5QrCode = null
let scanLocked = false  // Guard flag — prevents duplicate scan callbacks

// Lookup
const scanResult = ref(null)
const isLooking = ref(false)
const lookupError = ref(null)
const passengers = ref([])

// Capture schedule ID immediately into a plain variable (not reactive)
// This avoids any potential Vue reactivity/proxy issues inside the camera callback
let capturedScheduleId = null

onMounted(() => {
  // Capture the schedule ID right away as a plain JS value
  capturedScheduleId = props.scheduleId
  console.log('[QR Scanner] Mounted with scheduleId:', capturedScheduleId)

  if (activeTab.value === 'camera') {
    startCamera()
  }
})

onBeforeUnmount(() => {
  stopCamera()
})

// ---- Camera Scanner ----
const startCamera = async () => {
  try {
    cameraError.value = null
    scanLocked = false
    await nextTick()
    await new Promise(r => setTimeout(r, 400))

    html5QrCode = new Html5Qrcode('qr-reader')

    await html5QrCode.start(
      { facingMode: 'environment' },
      {
        fps: 10,
        qrbox: { width: 200, height: 200 },
        aspectRatio: 4 / 3,
        disableFlip: false
      },
      onQrCodeSuccess,
      () => {} // silent — no QR code detected yet
    )

    cameraActive.value = true
    console.log('[QR Scanner] Camera started successfully')
  } catch (err) {
    console.error('[QR Scanner] Camera error:', err)
    cameraError.value = typeof err === 'string'
      ? err
      : err?.message || 'Could not access camera. Check browser permissions or use manual entry.'
  }
}

const stopCamera = async () => {
  if (html5QrCode) {
    try {
      const state = html5QrCode.getState()
      if (state === 2) { // SCANNING
        await html5QrCode.stop()
      }
    } catch (e) { /* ignore */ }
    html5QrCode = null
  }
  cameraActive.value = false
}

/**
 * Called by html5-qrcode when a QR code is detected.
 */
const onQrCodeSuccess = (decodedText, decodedResult) => {
  // Guard 1: Ignore if we're already locked or processing
  if (scanLocked) return
  
  // Guard 2: If the text is empty/null, ignore it entirely and let the library keep looking
  // This prevents the 'green flash' loop when the camera picks up noise
  const rawValue = decodedText || ''
  const trimmedValue = rawValue.trim()
  
  if (!trimmedValue) {
    // Only log empty scans once every few seconds to avoid console flood
    if (!window._lastEmptyScanTime || Date.now() - window._lastEmptyScanTime > 2000) {
      console.warn('[QR Scanner] ⚠️ Detected QR-like pattern but content is EMPTY. Metadata:', decodedResult);
      window._lastEmptyScanTime = Date.now()
    }
    return 
  }

  // Lock the scanner immediately
  scanLocked = true
  console.log(`[QR Scanner] ✅ SUCCESS: "${trimmedValue}" (Length: ${trimmedValue.length})`)

  // Play beep sound
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = audioCtx.createOscillator()
    const gain = audioCtx.createGain()
    osc.connect(gain)
    gain.connect(audioCtx.destination)
    osc.frequency.value = 1200
    gain.gain.value = 0.15
    osc.start()
    osc.stop(audioCtx.currentTime + 0.12)
  } catch (e) { /* silent */ }

  // Schedule async work outside the library's internal loop
  setTimeout(async () => {
    try {
      // 1. Update UI state
      scanResult.value = trimmedValue

      // 2. Stop camera
      await stopCamera()
      
      // 3. Look up PNR in backend
      await lookupQr(trimmedValue)
    } catch (err) {
      console.error('[QR Scanner] Processing failed:', err)
      lookupError.value = 'Failed to process scan. Please try manual entry.'
      scanLocked = false // Unlock so they can try again if they hit 'Rescan'
    }
  }, 0)
}

// ---- Manual Entry ----
const performManualScan = () => {
  const val = manualInput.value.trim()
  if (!val) return
  scanResult.value = val
  lookupQr(val)
}

// ---- Lookup ----
const lookupQr = async (qrValue) => {
  // Use the captured schedule ID (plain JS, not Vue reactive proxy)
  const schedId = capturedScheduleId || props.scheduleId

  console.log('[QR Scanner] Looking up:', qrValue, 'on schedule:', schedId)

  if (!qrValue || !schedId) {
    lookupError.value = `Invalid scan data. QR="${qrValue}", Schedule="${schedId}". Please try again.`
    return
  }

  isLooking.value = true
  lookupError.value = null
  passengers.value = []

  try {
    const response = await dcsService.scanQr(qrValue, schedId)
    passengers.value = response.data.passengers || []
    console.log('[QR Scanner] Found', passengers.value.length, 'passenger(s)')
  } catch (err) {
    lookupError.value = err.response?.data?.error || 'No passenger found for this QR code on this flight.'
    console.error('[QR Scanner] Lookup error:', err.response?.data || err.message)
  } finally {
    isLooking.value = false
  }
}

const resetAndRescan = async () => {
  scanResult.value = null
  lookupError.value = null
  passengers.value = []
  manualInput.value = ''
  scanLocked = false

  if (activeTab.value === 'camera') {
    await startCamera()
  } else {
    nextTick(() => manualInputRef.value?.focus())
  }
}

const isCheckedIn = (p) => p.status === 'checkin' || p.status === 'boarding'

const selectPassenger = (passenger) => {
  if (isCheckedIn(passenger)) return
  emit('passenger-selected', passenger)
}

const switchToCamera = async () => {
  if (activeTab.value === 'camera') return
  activeTab.value = 'camera'
  if (!scanResult.value) {
    await startCamera()
  }
}

const switchToManual = async () => {
  activeTab.value = 'manual'
  await stopCamera()
  nextTick(() => manualInputRef.value?.focus())
}

const handleClose = async () => {
  await stopCamera()
  emit('close')
}
</script>

<style scoped>
@keyframes scan-line {
  0%, 100% { top: 12%; }
  50% { top: 85%; }
}
.animate-scan-line {
  animation: scan-line 2s ease-in-out infinite;
}

/* Override html5-qrcode default styles */
:deep(#qr-reader) {
  border: none !important;
  width: 100% !important;
}
:deep(#qr-reader video) {
  border-radius: 0 !important;
  object-fit: cover !important;
}
:deep(#qr-reader__scan_region) {
  min-height: auto !important;
}
:deep(#qr-reader__dashboard),
:deep(#qr-reader__dashboard_section_csr),
:deep(#qr-reader__dashboard_section_swaplink),
:deep(#qr-reader__header_message),
:deep(#qr-reader img[alt="Info icon"]),
:deep(#qr-reader__scan_region br) {
  display: none !important;
}

.border-t-3 { border-top-width: 3px; }
.border-b-3 { border-bottom-width: 3px; }
.border-l-3 { border-left-width: 3px; }
.border-r-3 { border-right-width: 3px; }
</style>
