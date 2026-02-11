<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Instructor Header -->
    <header class="bg-indigo-700 text-white px-6 py-4 flex justify-between items-center">
      <h1 class="text-lg font-semibold">Instructor Panel</h1>

      <router-link
        to="/"
        class="text-sm hover:underline"
      >
        Back to Booking
      </router-link>
    </header>

    <!-- Page content -->
    <main class="p-6">
      <router-view />
    </main>
  </div>
</template>
