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

// Default data (fallback)
const defaultMatrixData: CapacityRow[] = [
  { activity: 'LOADING', unit_model: 'EX2600-6', qty_units: 3, fuel_cons_l_per_hour: 187.0, prod_capacity_bcm_per_hour: 920.0, fleet_total_prod_bcm_per_hour: 2760.0, fleet_total_fuel_l_per_hour: 561.0 },
  { activity: 'LOADING', unit_model: 'PC1250', qty_units: 30, fuel_cons_l_per_hour: 65.0, prod_capacity_bcm_per_hour: 350.0, fleet_total_prod_bcm_per_hour: 10500.0, fleet_total_fuel_l_per_hour: 1950.0 },
  { activity: 'LOADING', unit_model: 'PC2000', qty_units: 34, fuel_cons_l_per_hour: 100.0, prod_capacity_bcm_per_hour: 700.0, fleet_total_prod_bcm_per_hour: 23800.0, fleet_total_fuel_l_per_hour: 3400.0 },
  { activity: 'LOADING', unit_model: 'PC3400', qty_units: 3, fuel_cons_l_per_hour: 160.0, prod_capacity_bcm_per_hour: 200.0, fleet_total_prod_bcm_per_hour: 600.0, fleet_total_fuel_l_per_hour: 480.0 },
  { activity: 'HAULING', unit_model: 'HD785-7', qty_units: 400, fuel_cons_l_per_hour: 77.0, prod_capacity_bcm_per_hour: 483.57, fleet_total_prod_bcm_per_hour: 43369.57, fleet_total_fuel_l_per_hour: 30800.0 },
  { activity: 'HAULING', unit_model: 'HD785-8', qty_units: 15, fuel_cons_l_per_hour: 85.0, prod_capacity_bcm_per_hour: 520.0, fleet_total_prod_bcm_per_hour: 2100.0, fleet_total_fuel_l_per_hour: 1155.0 },
  { activity: 'SUPPORTING', unit_model: 'D375A6R', qty_units: 36, fuel_cons_l_per_hour: 67.0, prod_capacity_bcm_per_hour: 0, fleet_total_prod_bcm_per_hour: 0, fleet_total_fuel_l_per_hour: 2412.0 },
  { activity: 'SUPPORTING', unit_model: 'D155A', qty_units: 25, fuel_cons_l_per_hour: 45.0, prod_capacity_bcm_per_hour: 0, fleet_total_prod_bcm_per_hour: 0, fleet_total_fuel_l_per_hour: 1125.0 },
  { activity: 'SUPPORTING', unit_model: 'GD825A', qty_units: 40, fuel_cons_l_per_hour: 28.0, prod_capacity_bcm_per_hour: 0, fleet_total_prod_bcm_per_hour: 0, fleet_total_fuel_l_per_hour: 1120.0 },
  { activity: 'DEWATERING', unit_model: 'EWP420', qty_units: 40, fuel_cons_l_per_hour: 40.0, prod_capacity_bcm_per_hour: 0, fleet_total_prod_bcm_per_hour: 0, fleet_total_fuel_l_per_hour: 1600.0 },
  { activity: 'DEWATERING', unit_model: 'EGS380-6', qty_units: 55, fuel_cons_l_per_hour: 10.0, prod_capacity_bcm_per_hour: 0, fleet_total_prod_bcm_per_hour: 0, fleet_total_fuel_l_per_hour: 550.0 },
]

const matrixData = computed<CapacityRow[]>(() => {
  if (!props.unitBreakdown || props.unitBreakdown.length === 0) return defaultMatrixData

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
    case 'HAULING': return 'info'
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
