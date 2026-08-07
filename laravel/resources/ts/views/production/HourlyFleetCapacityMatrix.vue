<script setup lang="ts">
import type { UnitBreakdown } from '@/composables/useAiApi'

interface Props {
  unitBreakdown: UnitBreakdown[] | null
}

const props = withDefaults(defineProps<Props>(), {
  unitBreakdown: null,
})

interface CapacityRow {
  activity: string
  unit_model: string
  qty_units: number
  fuel_cons_l_per_hour: number
  prod_capacity_bcm_per_hour: number
  fleet_total_prod_bcm_per_hour: number
  fleet_total_fuel_l_per_hour: number
}

const activityFilter = ref('ALL')

const matrixData = computed<CapacityRow[]>(() => {
  if (!props.unitBreakdown || props.unitBreakdown.length === 0) return []

  return props.unitBreakdown.map(item => ({
    activity: item.activity.toUpperCase(),
    unit_model: item.unit_name,
    qty_units: item.operating_units,
    fuel_cons_l_per_hour: item.fuel_l_hr_unit,
    prod_capacity_bcm_per_hour: item.prod_bcm_hr_unit,
    fleet_total_prod_bcm_per_hour: item.prod_bcm_hr_total,
    fleet_total_fuel_l_per_hour: item.fuel_l_hr_total,
  }))
})

const filteredData = computed(() => {
  if (activityFilter.value === 'ALL') return matrixData.value
  return matrixData.value.filter(r => r.activity === activityFilter.value)
})

const totalBcm = computed(() => filteredData.value.reduce((s, r) => s + r.fleet_total_prod_bcm_per_hour, 0))
const totalFuel = computed(() => filteredData.value.reduce((s, r) => s + r.fleet_total_fuel_l_per_hour, 0))

const headers = [
  { title: 'Activity', key: 'activity' },
  { title: 'Model', key: 'unit_model' },
  { title: 'Qty', key: 'qty_units', align: 'end' as const },
  { title: 'FC (L/hr)', key: 'fuel_cons_l_per_hour', align: 'end' as const },
  { title: 'BCM/hr', key: 'prod_capacity_bcm_per_hour', align: 'end' as const },
  { title: 'Fleet BCM/hr', key: 'fleet_total_prod_bcm_per_hour', align: 'end' as const },
  { title: 'Fleet Fuel L/hr', key: 'fleet_total_fuel_l_per_hour', align: 'end' as const },
]

const activityColor = (a: string) => {
  switch (a) {
    case 'LOADING': return 'primary'
    case 'HAULING': return 'secondary'
    case 'SUPPORTING': return 'warning'
    case 'DEWATERING': return 'secondary'
    default: return 'default'
  }
}
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Hourly Fleet Capacity Matrix</VCardTitle>
      <VCardSubtitle>
        Total Output: <strong>{{ totalBcm.toLocaleString('id-ID', { minimumFractionDigits: 2 }) }} BCM/hr</strong> |
        Total Fuel: <strong>{{ totalFuel.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }} L/hr</strong>
        <VChip
          v-if="unitBreakdown"
          color="success"
          size="x-small"
          variant="tonal"
          class="ms-2"
        >
          Live AI
        </VChip>
      </VCardSubtitle>
    </VCardItem>
    <VCardText>
      <VRow class="mb-4">
        <VCol
          cols="12"
          sm="4"
        >
          <VSelect
            v-model="activityFilter"
            :items="['ALL', 'LOADING', 'HAULING', 'SUPPORTING', 'DEWATERING']"
            label="Filter Activity"
            density="compact"
          />
        </VCol>
      </VRow>

      <VDataTable
        :headers="headers"
        :items="filteredData"
        :items-per-page="15"
        density="compact"
        class="text-no-wrap"
      >
        <template #item.activity="{ item }">
          <VChip
            :color="activityColor(item.activity)"
            size="small"
            variant="tonal"
          >
            {{ item.activity }}
          </VChip>
        </template>
        <template #item.unit_model="{ item }">
          <strong style="font-family: monospace;">{{ item.unit_model }}</strong>
        </template>
        <template #item.qty_units="{ item }">
          <VChip
            size="small"
            variant="outlined"
          >
            {{ item.qty_units }}
          </VChip>
        </template>
        <template #item.prod_capacity_bcm_per_hour="{ item }">
          <span :class="item.prod_capacity_bcm_per_hour === 0 ? 'text-medium-emphasis' : 'font-weight-bold'">
            {{ item.prod_capacity_bcm_per_hour === 0 ? 'N/A (Zero-BCM)' : item.prod_capacity_bcm_per_hour.toFixed(2) }}
          </span>
        </template>
        <template #item.fleet_total_prod_bcm_per_hour="{ item }">
          <span :class="item.fleet_total_prod_bcm_per_hour === 0 ? 'text-medium-emphasis' : 'font-weight-bold'">
            {{ item.fleet_total_prod_bcm_per_hour === 0 ? '—' : item.fleet_total_prod_bcm_per_hour.toLocaleString('id-ID', { minimumFractionDigits: 2 }) }}
          </span>
        </template>
        <template #item.fleet_total_fuel_l_per_hour="{ item }">
          <strong class="text-primary">{{ item.fleet_total_fuel_l_per_hour.toLocaleString('id-ID', { minimumFractionDigits: 1 }) }}</strong>
        </template>
      </VDataTable>
    </VCardText>
  </VCard>
</template>
