<template>
  <!-- Dynamically wrap pages with the selected layout -->
  <component :is="layoutComponent">
    <router-view />
  </component>
  
  <!-- Global Components -->
  <GlobalToast />
  <GlobalModalManager />
</template>

<script setup>
import { computed, defineAsyncComponent } from 'vue'
import { useRoute } from 'vue-router'

// Import layouts dynamically for code-splitting
const AdminLayout = defineAsyncComponent(() => import('@/views/admin/adminlayout.vue'))
const InstructorLayout = defineAsyncComponent(() => import('@/views/Instructor/InstructorLayout.vue'))
const StudentLayout = defineAsyncComponent(() => import('@/views/Student/StudentLayout.vue'))
const BookingLayout = defineAsyncComponent(() => import('@/views/booking/layout/BookingLayout.vue'))
import GlobalToast from '@/components/common/GlobalToast.vue'
import GlobalModalManager from '@/components/common/GlobalModalManager.vue'

const route = useRoute()

/**
 * Map layout names (from route.meta.layout)
 * to actual Vue components
 */
const layouts = {
  AdminLayout,
  InstructorLayout,
  StudentLayout,
  BookingLayout
}

/**
 * Choose layout:
 * - Uses meta.layout if defined
 * - Falls back to a plain <div> if not
 */
const layoutComponent = computed(() => {
  return layouts[route.meta.layout] || 'div'
})
</script>

<style>
/* Global styles */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Unbounded:wght@400;700&display=swap');

body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Poppins', sans-serif;
}

/* Shared button style */
.btn-cancel {
  margin-left: 20px;
  background: transparent;
  border: 1px solid #d11241;
  color: #d11241;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #d11241;
  color: white;
}
</style>

