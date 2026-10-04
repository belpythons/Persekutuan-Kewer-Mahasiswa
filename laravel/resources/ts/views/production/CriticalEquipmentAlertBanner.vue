<script setup lang="ts">
import type { UnitTuningComparison } from '@/composables/useAiApi'

interface Props {
  unitTuningComparison: UnitTuningComparison[] | null
}

const props = withDefaults(defineProps<Props>(), {
  unitTuningComparison: null,
})

const overConsumingUnits = computed(() => {
  if (!props.unitTuningComparison) return []
  return props.unitTuningComparison.filter(u => u.tuning_status === 'OVER_CONSUMPTION')
})

const totalExcessLiters = computed(() => {
  return overConsumingUnits.value.reduce((sum, u) => sum + Math.max(0, u.variance_liters), 0)
})
</script>

<template>
  <VAlert
    v-if="overConsumingUnits.length > 0"
    type="error"
    variant="tonal"
    border="start"
    prominent
    class="mb-0"
  >
    <template #prepend>
      <VIcon
        icon="bx-error-circle"
        size="32"
      />
    </template>
    <VAlertTitle class="text-body-1 font-weight-bold mb-1">
      {{ overConsumingUnits.length }} Unit Over-Consumption Terhadap Alokasi Tuning
    </VAlertTitle>
    <div class="text-body-2">
      Konsumsi BBM aktual melebihi alokasi tuning (OVER_CONSUMPTION) pada unit:
      <strong>{{ overConsumingUnits.map(u => u.unit_name).join(', ') }}</strong>
      <br>
      <strong class="text-tabular-nums">Total Kelebihan Solar: +{{ totalExcessLiters.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} Liter / Hari</strong>
    </div>
  </VAlert>
</template>
