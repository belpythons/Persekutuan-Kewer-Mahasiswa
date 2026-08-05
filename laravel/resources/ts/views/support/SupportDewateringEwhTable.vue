<script setup lang="ts">
interface EwhRow {
  sector: 'SUPPORTING' | 'DEWATERING'
  equipment_model: string
  active_qty: number
  fc_rate_l_hr: number
  daily_ewh_hrs: number
  annual_budgeted_ewh: number
  annual_fuel_budget_liters: number
  daily_fuel_allocation_liters: number
  fr_burden_l_bcm: number
  fr_burden_pct: number
}

const sectorFilter = ref('ALL')

const ewhData = ref<EwhRow[]>([
  { sector: 'SUPPORTING', equipment_model: 'Dozer D375A6R', active_qty: 36, fc_rate_l_hr: 67.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 262800, annual_fuel_budget_liters: 17607600, daily_fuel_allocation_liters: 48240.0, fr_burden_l_bcm: 0.0669, fr_burden_pct: 5.78 },
  { sector: 'SUPPORTING', equipment_model: 'Dozer D155A', active_qty: 25, fc_rate_l_hr: 45.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 182500, annual_fuel_budget_liters: 8212500, daily_fuel_allocation_liters: 22500.0, fr_burden_l_bcm: 0.0312, fr_burden_pct: 2.70 },
  { sector: 'SUPPORTING', equipment_model: 'Grader GD825A', active_qty: 40, fc_rate_l_hr: 28.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 292000, annual_fuel_budget_liters: 8176000, daily_fuel_allocation_liters: 22400.0, fr_burden_l_bcm: 0.0311, fr_burden_pct: 2.68 },
  { sector: 'SUPPORTING', equipment_model: 'Compactor CS533E', active_qty: 12, fc_rate_l_hr: 22.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 87600, annual_fuel_budget_liters: 1927200, daily_fuel_allocation_liters: 5280.0, fr_burden_l_bcm: 0.0073, fr_burden_pct: 0.63 },
  { sector: 'SUPPORTING', equipment_model: 'Water Truck FM260', active_qty: 30, fc_rate_l_hr: 30.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 219000, annual_fuel_budget_liters: 6570000, daily_fuel_allocation_liters: 18000.0, fr_burden_l_bcm: 0.0250, fr_burden_pct: 2.16 },
  { sector: 'SUPPORTING', equipment_model: 'Support PC200', active_qty: 40, fc_rate_l_hr: 25.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 292000, annual_fuel_budget_liters: 7300000, daily_fuel_allocation_liters: 20000.0, fr_burden_l_bcm: 0.0278, fr_burden_pct: 2.40 },
  { sector: 'DEWATERING', equipment_model: 'Pompa EWP420', active_qty: 40, fc_rate_l_hr: 40.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 292000, annual_fuel_budget_liters: 11680000, daily_fuel_allocation_liters: 32000.0, fr_burden_l_bcm: 0.0444, fr_burden_pct: 3.84 },
  { sector: 'DEWATERING', equipment_model: 'Pompa EGS380-6', active_qty: 55, fc_rate_l_hr: 10.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 401500, annual_fuel_budget_liters: 4015000, daily_fuel_allocation_liters: 11000.0, fr_burden_l_bcm: 0.0153, fr_burden_pct: 1.32 },
  { sector: 'DEWATERING', equipment_model: 'Multiflo 420EX', active_qty: 40, fc_rate_l_hr: 38.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 292000, annual_fuel_budget_liters: 11096000, daily_fuel_allocation_liters: 30400.0, fr_burden_l_bcm: 0.0422, fr_burden_pct: 3.65 },
  { sector: 'DEWATERING', equipment_model: 'Lighting Tower/Genset', active_qty: 40, fc_rate_l_hr: 12.0, daily_ewh_hrs: 20.0, annual_budgeted_ewh: 292000, annual_fuel_budget_liters: 3504000, daily_fuel_allocation_liters: 9600.0, fr_burden_l_bcm: 0.0133, fr_burden_pct: 1.15 },
])

const filteredData = computed(() => {
  if (sectorFilter.value === 'ALL') return ewhData.value
  return ewhData.value.filter(r => r.sector === sectorFilter.value)
})

const headers = [
  { title: 'Sector', key: 'sector' },
  { title: 'Model Equipment', key: 'equipment_model' },
  { title: 'Active Qty', key: 'active_qty', align: 'end' as const },
  { title: 'FC (L/hr)', key: 'fc_rate_l_hr', align: 'end' as const },
  { title: 'Daily EWH', key: 'daily_ewh_hrs', align: 'end' as const },
  { title: 'Annual EWH', key: 'annual_budgeted_ewh', align: 'end' as const },
  { title: 'Annual Budget (L)', key: 'annual_fuel_budget_liters', align: 'end' as const },
  { title: 'Daily Fuel (L)', key: 'daily_fuel_allocation_liters', align: 'end' as const },
  { title: 'FR Burden (L/BCM)', key: 'fr_burden_l_bcm', align: 'end' as const },
  { title: 'Burden %', key: 'fr_burden_pct', align: 'end' as const },
]

const sectorColor = (s: string) => s === 'SUPPORTING' ? 'warning' : 'secondary'
const formatNum = (v: number) => v.toLocaleString('id-ID')
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Tabel EWH & Konsumsi Solar Support & Dewatering Fleet</VCardTitle>
      <VCardSubtitle>Rincian kuota jam kerja dan beban Fuel Ratio sektor non-produksi</VCardSubtitle>
    </VCardItem>
    <VCardText>
      <VRow class="mb-4">
        <VCol
          cols="12"
          sm="4"
        >
          <VSelect
            v-model="sectorFilter"
            :items="['ALL', 'SUPPORTING', 'DEWATERING']"
            label="Filter Sector"
            density="compact"
          />
        </VCol>
      </VRow>

      <VDataTable
        :headers="headers"
        :items="filteredData"
        :items-per-page="10"
        density="compact"
        class="text-no-wrap"
      >
        <template #item.sector="{ item }">
          <VChip
            :color="sectorColor(item.sector)"
            size="small"
            variant="tonal"
          >
            {{ item.sector }}
          </VChip>
        </template>
        <template #item.equipment_model="{ item }">
          <strong style="font-family: monospace;">{{ item.equipment_model }}</strong>
        </template>
        <template #item.active_qty="{ item }">
          <VChip
            size="small"
            variant="outlined"
          >
            {{ item.active_qty }} Unit
          </VChip>
        </template>
        <template #item.daily_ewh_hrs="{ item }">
          <span class="text-medium-emphasis">{{ item.daily_ewh_hrs.toFixed(1) }} h/d</span>
        </template>
        <template #item.annual_budgeted_ewh="{ item }">
          <span>{{ formatNum(item.annual_budgeted_ewh) }} h/yr</span>
        </template>
        <template #item.annual_fuel_budget_liters="{ item }">
          <span>{{ formatNum(item.annual_fuel_budget_liters) }} L</span>
        </template>
        <template #item.daily_fuel_allocation_liters="{ item }">
          <strong class="text-primary">{{ formatNum(item.daily_fuel_allocation_liters) }} L</strong>
        </template>
        <template #item.fr_burden_l_bcm="{ item }">
          <span class="text-warning font-weight-bold">+{{ item.fr_burden_l_bcm.toFixed(4) }}</span>
        </template>
        <template #item.fr_burden_pct="{ item }">
          <VChip
            color="warning"
            size="small"
            variant="tonal"
          >
            {{ item.fr_burden_pct.toFixed(2) }}%
          </VChip>
        </template>
      </VDataTable>
    </VCardText>
  </VCard>
</template>
