<template>
  <div class="booking-progress-container">
    <div class="container">
      <div class="progress-steps">
        <div v-for="(step, index) in steps" :key="index" class="step-wrapper" :class="{ 'active': currentStepIndex === index, 'completed': currentStepIndex > index }">
          <div class="step-content">
            <div class="step-icon">
              <span v-if="currentStepIndex > index">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span class="step-label">{{ step.label }}</span>
          </div>
          <div v-if="index < steps.length - 1" class="step-connector"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const steps = [
  { label: 'Selection', routes: ['SearchResults'] },
  { label: 'Details', routes: ['PassengerDetails'] },
  { label: 'Extras', routes: ['Addons', 'SeatSelection'] },
  { label: 'Review', routes: ['ReviewBooking'] },
  { label: 'Payment', routes: ['Payment'] }
];

const currentStepIndex = computed(() => {
  return steps.findIndex(step => step.routes.includes(route.name));
});
</script>

<style scoped>
.booking-progress-container {
  background: white;
  padding: 20px 0;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 30px;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.step-wrapper {
  display: flex;
  align-items: center;
  flex: 1;
}

.step-wrapper:last-child {
  flex: none;
}

.step-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 2;
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.step-connector {
  flex: 1;
  height: 2px;
  background: #f1f5f9;
  margin: -24px 15px 0;
  transition: all 0.3s ease;
}

/* Active State */
.step-wrapper.active .step-icon {
  background: #003870;
  color: white;
  box-shadow: 0 0 0 4px rgba(0, 56, 112, 0.1);
}

.step-wrapper.active .step-label {
  color: #003870;
}

/* Completed State */
.step-wrapper.completed .step-icon {
  background: #10b981;
  color: white;
}

.step-wrapper.completed .step-label {
  color: #10b981;
}

.step-wrapper.completed .step-connector {
  background: #10b981;
}

@media (max-width: 640px) {
  .step-label {
    display: none;
  }
  
  .booking-progress-container {
    padding: 15px 0;
  }
  
  .step-connector {
    margin: 0 10px;
  }
}
</style>
