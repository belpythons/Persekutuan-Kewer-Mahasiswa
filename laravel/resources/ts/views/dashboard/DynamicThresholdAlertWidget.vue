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
</script>

<template>
  <VCard class="border">
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
            <span class="text-caption text-medium-emphasis">Current FR</span>
            <h3
              class="text-h3 font-weight-bold"
              :class="`text-${statusConfig.color}`"
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

        <VDivider class="mb-3" />

        <div class="d-flex justify-space-between text-caption flex-wrap gap-2">
          <div>
            <span class="text-medium-emphasis">Budget Baseline:</span>
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
