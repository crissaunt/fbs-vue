<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-bold text-[#002D1E]">Booking Details</h1>
    </div>

    <!-- Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-xs text-gray-600 uppercase">
          <tr>
            <th class="px-5 py-4">Passenger</th>
            <th class="px-5 py-4">Flight</th>
            <th class="px-5 py-4">Route</th>
            <th class="px-5 py-4">Seat</th>
            <th class="px-5 py-4">Class</th>
            <th class="px-5 py-4">Price</th>
            <th class="px-5 py-4">Status</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200 text-sm">
          <tr
            v-for="detail in bookingDetails"
            :key="detail.id"
            class="hover:bg-gray-50 transition"
          >
            <!-- Passenger -->
            <td class="px-5 py-4">
              <div class="font-medium text-[#002D1E]">
                {{ detail.passenger_name }}
              </div>
              <div class="text-xs text-gray-400">
                {{ detail.passenger_type }}
              </div>
            </td>

            <!-- Flight -->
            <td class="px-5 py-4">
              <div class="font-medium">{{ detail.airline_name }}</div>
              <div class="text-xs text-gray-400">
                {{ detail.flight_number }}
              </div>
            </td>

            <!-- Route -->
            <td class="px-5 py-4">
              {{ detail.route_display }}
            </td>

            <!-- Seat -->
            <td class="px-5 py-4">
              <span
                v-if="detail.seat_number"
                class="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-700"
              >
                {{ detail.seat_number }}
              </span>
              <span v-else class="text-gray-400 italic text-xs">
                Unassigned
              </span>
            </td>

            <!-- Class -->
            <td class="px-5 py-4">
              {{ detail.seat_class_name || '—' }}
            </td>

            <!-- Price -->
            <td class="px-5 py-4 font-semibold">
              ₱{{ detail.price }}
            </td>

            <!-- Status -->
            <td class="px-5 py-4">
              <span
                :class="statusBadge(detail.status)"
                class="px-2 py-1 text-[10px] font-bold uppercase rounded-full"
              >
                {{ detail.status }}
              </span>
            </td>
          </tr>

          <tr v-if="bookingDetails.length === 0">
            <td colspan="7" class="px-6 py-10 text-center text-gray-400 italic">
              No booking details found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import api from "@/services/admin/api"

const bookingDetails = ref([])

const fetchBookingDetails = async () => {
  try {
    const res = await api.get("/booking-details/")
    bookingDetails.value = res.data
  } catch (err) {
    console.error("Failed to load booking details", err)
  }
}

const statusBadge = (status) => {
  switch (status) {
    case "pending":
      return "bg-yellow-100 text-yellow-700"
    case "confirmed":
      return "bg-green-100 text-green-700"
    case "checkin":
      return "bg-blue-100 text-blue-700"
    case "boarding":
      return "bg-purple-100 text-purple-700"
    case "completed":
      return "bg-gray-200 text-gray-700"
    case "cancelled":
      return "bg-red-100 text-red-700"
    default:
      return "bg-gray-100 text-gray-500"
  }
}

onMounted(fetchBookingDetails)
</script>
