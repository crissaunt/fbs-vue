<template>
  <BaseModal 
    :is-open="modalStore.isOpen" 
    @close="modalStore.close(false)"
    :compact="modalStore.type !== 'custom'"
  >
    <ConfirmationModal v-if="modalStore.type === 'confirm' || modalStore.type === 'alert'" />
    
    <!-- Placeholder for other custom modals if needed -->
    <div v-else-if="modalStore.type === 'custom'" class="p-6">
      <slot name="custom"></slot>
    </div>
  </BaseModal>
</template>

<script setup>
import { useModalStore } from '@/stores/modal';
import BaseModal from './BaseModal.vue';
import ConfirmationModal from './ConfirmationModal.vue';

const modalStore = useModalStore();
</script>
