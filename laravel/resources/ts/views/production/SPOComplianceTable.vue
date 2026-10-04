<script setup lang="ts">
import type { UnitTuningComparison } from '@/composables/useAiApi'

interface Props {
  unitTuningComparison: UnitTuningComparison[] | null
  isLoading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  unitTuningComparison: null,
  isLoading: false,
})

const activityFilter = ref('ALL')

const activities = computed(() => {
  if (!props.unitTuningComparison) return ['ALL']
  const unique = [...new Set(props.unitTuningComparison.map(u => u.activity))]
  return ['ALL', ...unique]
})

const filteredData = computed(() => {
  if (!props.unitTuningComparison) return []
  if (activityFilter.value === 'ALL') return props.unitTuningComparison
  return props.unitTuningComparison.filter(r => r.activity === activityFilter.value)
})

const headers = [
  { title: 'Activity', key: 'activity' },
  { title: 'Unit', key: 'unit_name' },
  { title: 'Fleet Qty', key: 'fleet_qty', align: 'end' as const },
  { title: 'Std FC (L/hr)', key: 'std_fc_lhr', align: 'end' as const },
  { title: 'Alokasi Tuning (L/hari)', key: 'tuned_fuel_allocation_lday', align: 'end' as const },
  { title: 'Aktual (L/hari)', key: 'actual_fuel_consumed_lday', align: 'end' as const },
  { title: 'Variansi %', key: 'variance_pct', align: 'end' as const },
  { title: 'Spikes', key: 'spike_anomaly_count', align: 'center' as const },
  { title: 'Compliance', key: 'tuning_status', align: 'center' as const },
]

const activityColor = (a: string) => a.toUpperCase() === 'LOADING' ? 'primary' : a.toUpperCase() === 'HAULING' ? 'info' : 'warning'

// SPO (Standar Prosedur Operasional) compliance is derived from the fuel-tuning variance the
// AI engine already computes — a unit tracking its tuned allocation is compliant; one burning
// meaningfully more than allocated is not. No separate "SPO compliance" ground truth exists
// in the schema, so this reuses the real tuning_status rather than inventing a new metric.
const complianceConfig = (status: UnitTuningComparison['tuning_status']) => {
  switch (status) {
    case 'EFFICIENT': return { label: 'Compliant', color: 'success' }
    case 'WARNING': return { label: 'Partial', color: 'warning' }
    case 'OVER_CONSUMPTION': return { label: 'Non-Compliant', color: 'error' }
    default: return { label: status, color: 'default' }
  }
}
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>SPO Compliance — Variansi Alokasi Tuning per Unit</VCardTitle>
      <VCardSubtitle>Kepatuhan konsumsi solar terhadap alokasi tuning kapasitas (AI Engine)</VCardSubtitle>
    </VCardItem>
    <VCardText>
      <VRow class="mb-4">
        <VCol cols="12" sm="4">
          <VSelect
            v-model="activityFilter"
            :items="activities"
            label="Filter Activity"
            density="compact"
          />
        </VCol>
      </VRow>

      <VDataTable
        :headers="headers"
        :items="filteredData"
        :loading="isLoading"
        :items-per-page="10"
        density="compact"
        class="text-no-wrap"
        no-data-text="Belum ada data tuning kapasitas."
      >
        <template #item.activity="{ item }">
          <VChip :color="activityColor(item.activity)" size="small" variant="tonal">
            {{ item.activity }}
          </VChip>
        </template>
        <template #item.unit_name="{ item }">
          <code>{{ item.unit_name }}</code>
        </template>
        <template #item.std_fc_lhr="{ item }">
          <span class="text-medium-emphasis text-tabular-nums">{{ item.std_fc_lhr.toFixed(1) }}</span>
        </template>
        <template #item.tuned_fuel_allocation_lday="{ item }">
          <span class="text-tabular-nums">{{ item.tuned_fuel_allocation_lday.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }}</span>
        </template>
        <template #item.actual_fuel_consumed_lday="{ item }">
          <span
            class="text-tabular-nums"
            :class="item.tuning_status === 'OVER_CONSUMPTION' ? 'text-error font-weight-bold' : ''"
          >
            {{ item.actual_fuel_consumed_lday.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }}
          </span>
        </template>
        <template #item.variance_pct="{ item }">
          <span
            class="text-tabular-nums"
            :class="item.variance_pct > 0 ? 'text-error' : 'text-success'"
          >
            {{ item.variance_pct > 0 ? '+' : '' }}{{ item.variance_pct.toFixed(1) }}%
          </span>
        </template>
        <template #item.spike_anomaly_count="{ item }">
          <VChip
            :color="item.spike_anomaly_count > 0 ? 'error' : 'default'"
            size="small"
            :variant="item.spike_anomaly_count > 0 ? 'flat' : 'outlined'"
          >
            {{ item.spike_anomaly_count }}
          </VChip>
        </template>
        <template #item.tuning_status="{ item }">
          <VChip
            :color="complianceConfig(item.tuning_status).color"
            size="small"
            variant="flat"
          >
            {{ complianceConfig(item.tuning_status).label }}
          </VChip>
        </template>
      </VDataTable>
    </VCardText>
  </VCard>
</template>
