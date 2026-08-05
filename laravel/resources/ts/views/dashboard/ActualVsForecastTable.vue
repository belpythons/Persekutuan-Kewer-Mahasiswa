<script setup lang="ts">
interface ForecastRow {
  date: string
  rainfall_mm: number
  haul_distance_m: number
  actual_bcm: number
  actual_fuel_l: number
  actual_fr: number
  forecast_bcm: number
  forecast_fuel_l: number
  forecast_fr: number
  variance_fr: number
  status: 'NORMAL' | 'WARNING' | 'CRITICAL'
}

const statusFilter = ref('ALL')
const searchDate = ref('')

const tableData = ref<ForecastRow[]>([
  { date: '01/07/2026', rainfall_mm: 0.0, haul_distance_m: 3900, actual_bcm: 250120, actual_fuel_l: 289240, actual_fr: 1.1564, forecast_bcm: 250072, forecast_fuel_l: 289083, forecast_fr: 1.1560, variance_fr: 0.0004, status: 'NORMAL' },
  { date: '02/07/2026', rainfall_mm: 2.4, haul_distance_m: 3919, actual_bcm: 248500, actual_fuel_l: 290100, actual_fr: 1.1674, forecast_bcm: 249200, forecast_fuel_l: 289800, forecast_fr: 1.1630, variance_fr: 0.0044, status: 'NORMAL' },
  { date: '03/07/2026', rainfall_mm: 15.0, haul_distance_m: 4020, actual_bcm: 235800, actual_fuel_l: 295400, actual_fr: 1.2527, forecast_bcm: 237100, forecast_fuel_l: 294800, forecast_fr: 1.2434, variance_fr: 0.0093, status: 'WARNING' },
  { date: '04/07/2026', rainfall_mm: 28.5, haul_distance_m: 4128, actual_bcm: 220400, actual_fuel_l: 310200, actual_fr: 1.4074, forecast_bcm: 222800, forecast_fuel_l: 308500, forecast_fr: 1.3845, variance_fr: 0.0229, status: 'CRITICAL' },
  { date: '05/07/2026', rainfall_mm: 5.2, haul_distance_m: 3942, actual_bcm: 245600, actual_fuel_l: 292100, actual_fr: 1.1893, forecast_bcm: 246300, forecast_fuel_l: 291500, forecast_fr: 1.1835, variance_fr: 0.0058, status: 'NORMAL' },
  { date: '06/07/2026', rainfall_mm: 0.0, haul_distance_m: 3900, actual_bcm: 251200, actual_fuel_l: 288900, actual_fr: 1.1501, forecast_bcm: 250800, forecast_fuel_l: 289200, forecast_fr: 1.1532, variance_fr: -0.0031, status: 'NORMAL' },
  { date: '07/07/2026', rainfall_mm: 35.2, haul_distance_m: 4182, actual_bcm: 210500, actual_fuel_l: 320800, actual_fr: 1.5239, forecast_bcm: 215200, forecast_fuel_l: 315600, forecast_fr: 1.4665, variance_fr: 0.0574, status: 'CRITICAL' },
])

const filteredData = computed(() => {
  let data = tableData.value
  if (statusFilter.value !== 'ALL') {
    data = data.filter(r => r.status === statusFilter.value)
  }
  if (searchDate.value) {
    data = data.filter(r => r.date.includes(searchDate.value))
  }
  return data
})

const statusColor = (status: string) => {
  switch (status) {
    case 'CRITICAL': return 'error'
    case 'WARNING': return 'warning'
    default: return 'success'
  }
}

const headers = [
  { title: 'Tanggal', key: 'date', sortable: true },
  { title: 'Hujan (mm)', key: 'rainfall_mm', align: 'end' as const },
  { title: 'Jarak (m)', key: 'haul_distance_m', align: 'end' as const },
  { title: 'Actual BCM', key: 'actual_bcm', align: 'end' as const },
  { title: 'Actual Fuel (L)', key: 'actual_fuel_l', align: 'end' as const },
  { title: 'Actual FR', key: 'actual_fr', align: 'end' as const },
  { title: 'Forecast BCM', key: 'forecast_bcm', align: 'end' as const },
  { title: 'Forecast Fuel (L)', key: 'forecast_fuel_l', align: 'end' as const },
  { title: 'Forecast FR', key: 'forecast_fr', align: 'end' as const },
  { title: 'Variance', key: 'variance_fr', align: 'end' as const },
  { title: 'Status', key: 'status', align: 'center' as const },
]

const formatNum = (v: number) => v.toLocaleString('id-ID')
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Actual vs XGBoost Forecast — Side by Side</VCardTitle>
      <VCardSubtitle>Data harian dengan filter status threshold</VCardSubtitle>
    </VCardItem>
    <VCardText>
      <!-- Filter Bar -->
      <VRow class="mb-4">
        <VCol
          cols="12"
          sm="4"
        >
          <VTextField
            v-model="searchDate"
            label="Cari Tanggal"
            placeholder="DD/MM/YYYY"
            density="compact"
            prepend-inner-icon="bx-search"
            clearable
          />
        </VCol>
        <VCol
          cols="12"
          sm="4"
        >
          <VSelect
            v-model="statusFilter"
            :items="['ALL', 'NORMAL', 'WARNING', 'CRITICAL']"
            label="Filter Status"
            density="compact"
          />
        </VCol>
        <VCol
          cols="12"
          sm="4"
          class="d-flex align-center"
        >
          <VBtn
            variant="outlined"
            color="primary"
            prepend-icon="bx-download"
            size="small"
          >
            Export CSV
          </VBtn>
        </VCol>
      </VRow>

      <!-- Data Table -->
      <VDataTable
        :headers="headers"
        :items="filteredData"
        :items-per-page="10"
        density="compact"
        class="text-no-wrap"
      >
        <template #item.actual_bcm="{ item }">
          {{ formatNum(item.actual_bcm) }}
        </template>
        <template #item.actual_fuel_l="{ item }">
          {{ formatNum(item.actual_fuel_l) }}
        </template>
        <template #item.actual_fr="{ item }">
          <span class="font-weight-bold">{{ item.actual_fr.toFixed(4) }}</span>
        </template>
        <template #item.forecast_bcm="{ item }">
          {{ formatNum(item.forecast_bcm) }}
        </template>
        <template #item.forecast_fuel_l="{ item }">
          {{ formatNum(item.forecast_fuel_l) }}
        </template>
        <template #item.forecast_fr="{ item }">
          <span class="font-weight-bold text-info">{{ item.forecast_fr.toFixed(4) }}</span>
        </template>
        <template #item.variance_fr="{ item }">
          <span :class="item.variance_fr > 0 ? 'text-error' : 'text-success'">
            {{ item.variance_fr > 0 ? '+' : '' }}{{ item.variance_fr.toFixed(4) }}
          </span>
        </template>
        <template #item.status="{ item }">
          <VChip
            :color="statusColor(item.status)"
            size="small"
            variant="flat"
          >
            {{ item.status }}
          </VChip>
        </template>
      </VDataTable>
    </VCardText>
  </VCard>
</template>
