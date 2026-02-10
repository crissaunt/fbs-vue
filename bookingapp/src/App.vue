<template>
  <component :is="layoutComponent">
    <router-view />
  </component>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
// Import your layouts here
import AdminLayout from '@/views/admin/adminlayout.vue';

const route = useRoute();

// Mapping the layout name from router/index.js to the imported component
const layouts = {
  AdminLayout
};

/**
 * If the route has meta: { layout: 'AdminLayout' }, it uses that component.
 * Otherwise, it defaults to a simple 'div' (no extra layout).
 */
const layoutComponent = computed(() => {
  return layouts[route.meta.layout] || 'div';
});
</script>

<style>
/* Global styles that apply to the whole application */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Unbounded:wght@400;700&display=swap');

body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

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