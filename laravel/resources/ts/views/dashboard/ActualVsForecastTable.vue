<script setup lang="ts">
import { useAiApi, AiApiError } from '@/composables/useAiApi'
import type { ForecastHistoryItem } from '@/composables/useAiApi'

const { fetchForecastHistory } = useAiApi()

interface ForecastRow extends ForecastHistoryItem {
  actual_fuel_l: number
  forecast_fuel_l: number
  variance_fr: number
}

const isLoading = ref(true)
const errorMsg = ref('')
const historyLogs = ref<ForecastHistoryItem[]>([])

const statusFilter = ref('ALL')
const searchDate = ref('')

// Fuel liters aren't logged directly — they're derived the same way the rest of the app
// computes them: Total_Fuel_L = Fuel_Ratio (L/BCM) x Production (BCM).
const tableData = computed<ForecastRow[]>(() => historyLogs.value.map(log => ({
  ...log,
  actual_fuel_l: log.actual_fr * log.daily_prod_bcm,
  forecast_fuel_l: log.forecast_fr * log.daily_prod_bcm,
  variance_fr: Number((log.actual_fr - log.forecast_fr).toFixed(4)),
})))

const filteredData = computed(() => {
  let data = tableData.value
  if (statusFilter.value !== 'ALL')
    data = data.filter(r => r.status === statusFilter.value)
  if (searchDate.value)
    data = data.filter(r => r.log_date.includes(searchDate.value))
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
  { title: 'Tanggal', key: 'log_date', sortable: true },
  { title: 'Produksi (BCM)', key: 'daily_prod_bcm', align: 'end' as const },
  { title: 'Jarak (m)', key: 'haul_distance_m', align: 'end' as const },
  { title: 'Actual Fuel (L)', key: 'actual_fuel_l', align: 'end' as const },
  { title: 'Actual FR', key: 'actual_fr', align: 'end' as const },
  { title: 'Forecast Fuel (L)', key: 'forecast_fuel_l', align: 'end' as const },
  { title: 'Forecast FR', key: 'forecast_fr', align: 'end' as const },
  { title: 'Variance', key: 'variance_fr', align: 'end' as const },
  { title: 'Status', key: 'status', align: 'center' as const },
]

const formatNum = (v: number) => v.toLocaleString('id-ID', { maximumFractionDigits: 0 })

async function loadHistory() {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const result = await fetchForecastHistory(30)
    historyLogs.value = result.historical_logs || []
  } catch (e: unknown) {
    historyLogs.value = []
    errorMsg.value = e instanceof AiApiError ? e.message : 'Gagal memuat log historis forecast'
  } finally {
    isLoading.value = false
  }
}

function exportCsv() {
  const rows = filteredData.value
  if (rows.length === 0) return

  const cols: (keyof ForecastRow)[] = ['log_date', 'daily_prod_bcm', 'haul_distance_m', 'actual_fuel_l', 'actual_fr', 'forecast_fuel_l', 'forecast_fr', 'variance_fr', 'status']
  const csvLines = [
    cols.join(','),
    ...rows.map(r => cols.map(c => r[c]).join(',')),
  ]
  const blob = new Blob([csvLines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `actual-vs-forecast-${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(loadHistory)
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Actual vs XGBoost Forecast — Side by Side</VCardTitle>
      <VCardSubtitle>Log historis 30 hari terakhir dari database, dengan filter status threshold</VCardSubtitle>
    </VCardItem>
    <VCardText>
      <!-- Filter Bar -->
      <VRow class="mb-4">
        <VCol cols="12" sm="4">
          <VTextField
            v-model="searchDate"
            label="Cari Tanggal"
            placeholder="YYYY-MM-DD"
            density="compact"
            prepend-inner-icon="bx-search"
            clearable
          />
        </VCol>
        <VCol cols="12" sm="4">
          <VSelect
            v-model="statusFilter"
            :items="['ALL', 'NORMAL', 'WARNING', 'CRITICAL']"
            label="Filter Status"
            density="compact"
          />
        </VCol>
        <VCol cols="12" sm="4" class="d-flex align-center">
          <VBtn
            variant="outlined"
            color="primary"
            prepend-icon="bx-download"
            size="small"
            :disabled="filteredData.length === 0"
            @click="exportCsv"
          >
            Export CSV
          </VBtn>
        </VCol>
      </VRow>

      <div v-if="errorMsg && historyLogs.length === 0" class="d-flex flex-column align-center justify-center text-center py-8">
        <VIcon icon="bx-error-circle" size="40" class="text-error mb-3" />
        <p class="text-body-2 text-medium-emphasis mb-3">{{ errorMsg }}</p>
        <VBtn variant="tonal" color="primary" size="small" :loading="isLoading" @click="loadHistory">
          Coba Lagi
        </VBtn>
      </div>

      <VDataTable
        v-else
        :headers="headers"
        :items="filteredData"
        :loading="isLoading"
        :items-per-page="10"
        density="compact"
        class="text-no-wrap"
        no-data-text="Belum ada log forecast di database untuk rentang ini."
      >
        <template #item.daily_prod_bcm="{ item }">
          {{ formatNum(item.daily_prod_bcm) }}
        </template>
        <template #item.haul_distance_m="{ item }">
          {{ formatNum(item.haul_distance_m) }}
        </template>
        <template #item.actual_fuel_l="{ item }">
          {{ formatNum(item.actual_fuel_l) }}
        </template>
        <template #item.actual_fr="{ item }">
          <span class="font-weight-bold text-tabular-nums">{{ item.actual_fr.toFixed(4) }}</span>
        </template>
        <template #item.forecast_fuel_l="{ item }">
          {{ formatNum(item.forecast_fuel_l) }}
        </template>
        <template #item.forecast_fr="{ item }">
          <span class="font-weight-bold text-info text-tabular-nums">{{ item.forecast_fr.toFixed(4) }}</span>
        </template>
        <template #item.variance_fr="{ item }">
          <span class="text-tabular-nums" :class="item.variance_fr > 0 ? 'text-error' : 'text-success'">
            {{ item.variance_fr > 0 ? '+' : '' }}{{ item.variance_fr.toFixed(4) }}
          </span>
        </template>
        <template #item.status="{ item }">
          <VChip :color="statusColor(item.status)" size="small" variant="flat">
            {{ item.status }}
          </VChip>
        </template>
      </VDataTable>
    </VCardText>
  </VCard>
</template>
