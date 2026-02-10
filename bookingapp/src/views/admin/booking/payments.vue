<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-xl font-bold text-[#002D1E]">Payments</h1>
    </div>

    <!-- Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200 text-xs text-gray-600 uppercase">
          <tr>
            <th class="px-5 py-4">Payment ID</th>
            <th class="px-5 py-4">Booking</th>
            <th class="px-5 py-4">Amount</th>
            <th class="px-5 py-4">Method</th>
            <th class="px-5 py-4">Transaction</th>
            <th class="px-5 py-4">Status</th>
            <th class="px-5 py-4">Date</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200 text-sm">
          <tr
            v-for="payment in payments"
            :key="payment.id"
            class="hover:bg-gray-50 transition"
          >
            <!-- Payment ID -->
            <td class="px-5 py-4 font-semibold text-[#fe3787]">
              #{{ payment.id }}
            </td>

            <!-- Booking -->
            <td class="px-5 py-4 font-medium">
              Booking #{{ payment.booking }}
            </td>

            <!-- Amount -->
            <td class="px-5 py-4 font-semibold">
              ₱{{ payment.amount }}
            </td>

            <!-- Method -->
            <td class="px-5 py-4">
              <span
                class="px-2 py-1 text-[10px] font-bold uppercase rounded-full bg-blue-100 text-blue-700"
              >
                {{ payment.method }}
              </span>
            </td>

            <!-- Transaction -->
            <td class="px-5 py-4 text-xs text-gray-500">
              {{ payment.transaction_id || '—' }}
            </td>

            <!-- Status -->
            <td class="px-5 py-4">
              <span
                class="px-2 py-1 text-[10px] font-bold uppercase rounded-full"
                :class="statusBadge(payment.status)"
              >
                {{ payment.status }}
              </span>
            </td>

            <!-- Date -->
            <td class="px-5 py-4 text-xs text-gray-500">
              {{ formatDate(payment.payment_date) }}
            </td>
          </tr>

          <tr v-if="payments.length === 0">
            <td colspan="7" class="px-6 py-10 text-center text-gray-400 italic">
              No payments found.
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

const payments = ref([])

const fetchPayments = async () => {
  try {
    const res = await api.get("/payments/")
    payments.value = res.data
  } catch (err) {
    console.error("Failed to load payments", err)
  }
}

const formatDate = (date) =>
  new Date(date).toLocaleString()

const statusBadge = (status) => {
  switch (status) {
    case "Completed":
      return "bg-green-100 text-green-700"
    case "Pending":
      return "bg-yellow-100 text-yellow-700"
    case "Failed":
      return "bg-red-100 text-red-700"
    default:
      return "bg-gray-100 text-gray-600"
  }
}

onMounted(fetchPayments)
</script>
