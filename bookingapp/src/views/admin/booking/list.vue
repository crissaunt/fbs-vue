<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-xl font-bold text-[#002D1E]">Bookings</h1>
    </div>

    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-xs text-gray-600 uppercase">
          <tr>
            <th class="px-5 py-4">Booking ID</th>
            <th class="px-5 py-4">User</th>
            <th class="px-5 py-4">Trip Type</th>
            <th class="px-5 py-4">Total Amount</th>
            <th class="px-5 py-4">Status</th>
            <th class="px-5 py-4">Created</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200 text-sm">
          <tr
            v-for="booking in bookings"
            :key="booking.id"
            class="hover:bg-gray-50 transition"
          >
            <td class="px-5 py-4 font-semibold text-[#fe3787]">
              #{{ booking.id }}
            </td>

            <td class="px-5 py-4">
              <div class="font-medium">
                {{ booking.user_name || '—' }}
              </div>
            </td>

            <td class="px-5 py-4 capitalize">
              {{ booking.trip_type.replace('_', ' ') }}
            </td>

            <td class="px-5 py-4 font-semibold">
              ₱{{ booking.total_amount }}
            </td>

            <td class="px-5 py-4">
              <span
                class="px-2 py-1 text-[10px] font-bold uppercase rounded-full"
                :class="statusBadge(booking.status)"
              >
                {{ booking.status }}
              </span>
            </td>

            <td class="px-5 py-4 text-gray-500 text-xs">
              {{ formatDate(booking.created_at) }}
            </td>
          </tr>

          <tr v-if="bookings.length === 0">
            <td colspan="6" class="px-6 py-10 text-center text-gray-400 italic">
              No bookings found.
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

const bookings = ref([])

const fetchBookings = async () => {
  const res = await api.get("/bookings/")
  bookings.value = res.data
}

const formatDate = (date) =>
  new Date(date).toLocaleString()

const statusBadge = (status) => {
  switch (status.toLowerCase()) {
    case "pending":
      return "bg-yellow-100 text-yellow-700"
    case "confirmed":
      return "bg-green-100 text-green-700"
    case "cancelled":
      return "bg-red-100 text-red-700"
    default:
      return "bg-gray-100 text-gray-600"
  }
}

onMounted(fetchBookings)
</script>
