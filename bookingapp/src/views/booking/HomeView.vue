<template>
  <div class=" bg-gray-50">
    <section class="hero relative flex items-center justify-center text-white py-35 ">
      <div class="container mx-auto px-4 space-y-4 relative z-10">
        <h1 class="text-5xl   font-black  tracking-tight drop-shadow-lg">
          Welcome Home, Mabuhay!
        </h1>
        <p class="text-base mb-8  opacity-90 max-w-2xl font-medium">
          Book your next adventure across the Philippines and beyond.
        </p>
        
        <div class="text-slate-900">
          <FlightSearch />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import FlightSearch from '@/components/booking/FlightSearch.vue';
</script>

<style scoped>
.hero {
  /* Using #FF579A at 0.8 (80%) opacity per your request */
  background: 
              url('@/assets/image/bg-cthm.svg');
  background-size: cover;
  background-position: center;
}
</style>