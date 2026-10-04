<script setup lang="ts">
import type { EwhSector } from '@/composables/useAiApi'

interface Props {
  sectors: EwhSector[] | null
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  sectors: null,
  isLoading: false,
})

interface EwhRow {
  sector: string
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

const allRows = computed<EwhRow[]>(() => {
  if (!props.sectors) return []
  return props.sectors.flatMap(s => s.equipment.map(eq => ({
    sector: s.sector,
    ...eq,
  })))
})

const filteredData = computed(() => {
  if (sectorFilter.value === 'ALL') return allRows.value
  return allRows.value.filter(r => r.sector === sectorFilter.value)
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

const sectorColor = (s: string) => s === 'SUPPORT' ? 'warning' : 'secondary'
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
        <VCol cols="12" sm="4">
          <VSelect
            v-model="sectorFilter"
            :items="['ALL', 'SUPPORT', 'DEWATERING']"
            label="Filter Sector"
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
        no-data-text="Belum ada data EWH & baseline PA/UA di database."
      >
        <template #item.sector="{ item }">
          <VChip :color="sectorColor(item.sector)" size="small" variant="tonal">
            {{ item.sector }}
          </VChip>
        </template>
        <template #item.equipment_model="{ item }">
          <strong style="font-family: monospace;">{{ item.equipment_model }}</strong>
        </template>
        <template #item.active_qty="{ item }">
          <VChip size="small" variant="outlined">
            {{ item.active_qty }} Unit
          </VChip>
        </template>
        <template #item.daily_ewh_hrs="{ item }">
          <span class="text-medium-emphasis text-tabular-nums">{{ item.daily_ewh_hrs.toFixed(1) }} h/d</span>
        </template>
        <template #item.annual_budgeted_ewh="{ item }">
          <span class="text-tabular-nums">{{ formatNum(item.annual_budgeted_ewh) }} h/yr</span>
        </template>
        <template #item.annual_fuel_budget_liters="{ item }">
          <span class="text-tabular-nums">{{ formatNum(item.annual_fuel_budget_liters) }} L</span>
        </template>
        <template #item.daily_fuel_allocation_liters="{ item }">
          <strong class="text-primary text-tabular-nums">{{ formatNum(item.daily_fuel_allocation_liters) }} L</strong>
        </template>
        <template #item.fr_burden_l_bcm="{ item }">
          <span class="text-warning font-weight-bold text-tabular-nums">+{{ item.fr_burden_l_bcm.toFixed(4) }}</span>
        </template>
        <template #item.fr_burden_pct="{ item }">
          <VChip color="warning" size="small" variant="tonal">
            {{ item.fr_burden_pct.toFixed(2) }}%
          </VChip>
        </template>
      </VDataTable>
    </VCardText>
  </VCard>
</template>
