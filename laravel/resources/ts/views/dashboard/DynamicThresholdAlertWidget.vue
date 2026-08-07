<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  actualFr: number
  budgetBaseline: number
  warningThreshold: number
  criticalThreshold: number
  excessFuelLiters: number
  isLoading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  actualFr: 1.2800,
  budgetBaseline: 1.1576,
  warningThreshold: 1.2503,
  criticalThreshold: 1.3660,
  excessFuelLiters: 0,
  isLoading: false,
})

const status = computed(() => {
  if (props.actualFr >= props.criticalThreshold) return 'CRITICAL'
  if (props.actualFr >= props.warningThreshold) return 'WARNING'
  return 'NORMAL'
})

const statusConfig = computed(() => {
  switch (status.value) {
    case 'CRITICAL':
      return { color: 'error', icon: 'bx-error-circle', label: 'CRITICAL (+18%)' }
    case 'WARNING':
      return { color: 'warning', icon: 'bx-error', label: 'WARNING (+8%)' }
    default:
      return { color: 'success', icon: 'bx-check-circle', label: 'NORMAL' }
  }
})

const deviationPct = computed(() => {
  return (((props.actualFr - props.budgetBaseline) / props.budgetBaseline) * 100).toFixed(1)
})

// Progress bar percentage (0.90 to 1.35 range mapped to 0-100%)
const progressPct = computed(() => {
  const min = 0.90
  const max = 1.35
  const clamped = Math.max(min, Math.min(max, props.actualFr))
  return Math.round(((clamped - min) / (max - min)) * 100)
})

const progressColor = computed(() => {
  if (props.actualFr >= props.criticalThreshold) return '#E53935'
  if (props.actualFr >= props.warningThreshold) return '#FFB400'
  return '#56CA00'
})

const isCriticalState = computed(() => status.value === 'CRITICAL')
</script>

<template>
  <VCard
    class="alert-card"
    :class="{ 'critical-tint': isCriticalState }"
  >
    <VCardItem>
      <template #prepend>
        <VAvatar
          :color="statusConfig.color"
          variant="tonal"
          size="44"
          rounded
        >
          <VIcon
            :icon="statusConfig.icon"
            size="24"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-bold">
        Fuel Ratio Status Hari Ini
      </VCardTitle>
      <VCardSubtitle class="text-caption">Dynamic Threshold Alert</VCardSubtitle>
    </VCardItem>

    <VCardText>
      <div v-if="isLoading" class="d-flex justify-center my-4">
        <VProgressCircular indeterminate color="primary" />
      </div>
      <template v-else>
        <div class="d-flex align-center gap-4 mb-3">
          <div>
            <span class="text-caption text-medium-emphasis">Forecast FR (H+1)</span>
            <h3
              class="text-h5 font-weight-bold"
              style="color: #E53935;"
            >
              {{ props.actualFr.toFixed(4) }}
            </h3>
            <span class="text-caption text-medium-emphasis">L/BCM</span>
          </div>
          <VSpacer />
          <VChip
            :color="statusConfig.color"
            variant="tonal"
            size="large"
            class="font-weight-bold"
          >
            <VIcon
              start
              :icon="statusConfig.icon"
            />
            {{ statusConfig.label }}
          </VChip>
        </div>

        <!-- Progress Linear Ratio Indicator -->
        <VProgressLinear
          :model-value="progressPct"
          :color="progressColor"
          height="6"
          rounded
          class="mb-3"
        />

        <VDivider class="mb-3" />

        <div class="d-flex justify-space-between text-caption flex-wrap gap-2">
          <div>
            <span class="text-medium-emphasis">Budget SPO:</span>
            <strong class="ms-1 text-high-emphasis">{{ props.budgetBaseline.toFixed(4) }} L/BCM</strong>
          </div>
          <div>
            <span class="text-medium-emphasis">Deviasi:</span>
            <strong
              class="ms-1"
              :class="`text-${statusConfig.color}`"
            >{{ Number(deviationPct) > 0 ? '+' : '' }}{{ deviationPct }}%</strong>
          </div>
          <div>
            <span class="text-medium-emphasis">Excess Fuel:</span>
            <strong class="ms-1 text-error">+{{ props.excessFuelLiters.toLocaleString('id-ID') }} L</strong>
          </div>
        </div>
      </template>
    </VCardText>
  </VCard>
</template>

<style scoped>
.alert-card {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  transition: border-color 0.3s ease, background-color 0.3s ease;
}

.alert-card.critical-tint {
  background-color: rgba(229, 57, 53, 0.06);
  border-left: 4px solid #E53935;
}
</style>
