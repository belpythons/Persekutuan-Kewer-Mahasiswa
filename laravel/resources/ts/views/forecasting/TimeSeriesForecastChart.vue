<script setup lang="ts">
import { useTheme } from 'vuetify'
import { hexToRgb } from '@core/utils/colorConverter'
import { useAiApi } from '@/composables/useAiApi'
import type { Forecast7DaysResponse, ForecastHistoryItem } from '@/composables/useAiApi'

const vuetifyTheme = useTheme()
const { fetchForecast7Days, fetchForecastHistory } = useAiApi()

const isLoading = ref(true)
const forecast7DaysData = ref<Forecast7DaysResponse | null>(null)
const historyLogs = ref<ForecastHistoryItem[]>([])

// Format date string YYYY-MM-DD to DD/MM
const formatDateLabel = (dateStr: string, isForecast = false) => {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length < 3) return dateStr
  const label = `${parts[2]}/${parts[1]}`
  return isForecast ? `${label} (FC)` : label
}

// 1. Dynamic Categories from DB History + XGBoost 7-Day Forecast API
const categories = computed(() => {
  const histCats = historyLogs.value.map(h => formatDateLabel(h.log_date, false))
  const fcCats = (forecast7DaysData.value?.daily_forecasts || []).map(f => formatDateLabel(f.log_date, true))
  return [...histCats, ...fcCats]
})

// 2. Dynamic Actual FR Series from Database Logs
const actualFrSeries = computed(() => {
  const histActuals = historyLogs.value.map(h => h.actual_fr)
  const fcCount = forecast7DaysData.value?.daily_forecasts?.length ?? 0
  return [...histActuals, ...Array(fcCount).fill(null)]
})

// 3. Dynamic Forecast FR Series from XGBoost Engine API Output JSON
const forecastFrSeries = computed(() => {
  const histCount = historyLogs.value.length
  const lastHistVal = histCount > 0 ? historyLogs.value[histCount - 1].actual_fr : null
  const nulls = Array(Math.max(0, histCount - 1)).fill(null)

  const fcValues = (forecast7DaysData.value?.daily_forecasts || []).map(d => d.forecast_fr)
  if (lastHistVal !== null) {
    return [...nulls, lastHistVal, ...fcValues]
  }
  return [...nulls, ...fcValues]
})

const budgetBaseline = computed(() => {
  return forecast7DaysData.value?.daily_forecasts?.[0]?.budget_baseline ?? 1.018
})

const warningThreshold = computed(() => {
  return forecast7DaysData.value?.daily_forecasts?.[0]?.warning_threshold ?? 1.0994
})

const criticalThreshold = computed(() => {
  return forecast7DaysData.value?.daily_forecasts?.[0]?.critical_threshold ?? 1.2012
})

const loadChartData = async () => {
  isLoading.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    const [histRes, fcRes] = await Promise.all([
      fetchForecastHistory(30).catch(() => ({ total: 0, historical_logs: [] })),
      fetchForecast7Days(today).catch(() => null)
    ])
    historyLogs.value = histRes.historical_logs || []
    forecast7DaysData.value = fcRes
  } catch (error) {
    console.error('Failed to load real AI chart data from database/API:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadChartData()
})

const chartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors
  const variableTheme = vuetifyTheme.current.value.variables
  const disabledTextColor = `rgba(${hexToRgb(String(currentTheme['on-surface']))},${variableTheme['disabled-opacity']})`
  const borderColor = `rgba(${hexToRgb(String(variableTheme['border-color']))},${variableTheme['border-opacity']})`

  const bBase = budgetBaseline.value
  const wThresh = warningThreshold.value
  const cThresh = criticalThreshold.value
  const firstFcLabel = categories.value[historyLogs.value.length] || 'FC'

  return {
    chart: {
      type: 'line' as const,
      parentHeightOffset: 0,
      toolbar: { show: true },
    },
    stroke: {
      curve: 'smooth' as const,
      width: [4, 3],
      dashArray: [0, 6],
    },
    colors: ['#1E88E5', '#E53935'],
    xaxis: {
      categories: categories.value,
      labels: {
        style: { fontSize: '11px', colors: disabledTextColor },
        rotate: -45,
        rotateAlways: true,
      },
      tickAmount: 18,
    },
    yaxis: {
      min: 0.40,
      max: 1.45,
      labels: {
        style: { fontSize: '12px', colors: disabledTextColor },
        formatter: (v: number) => (v ? v.toFixed(3) : '0.000'),
      },
    },
    grid: {
      strokeDashArray: 4,
      borderColor,
    },
    legend: {
      position: 'top' as const,
      horizontalAlign: 'left' as const,
      fontSize: '13px',
      labels: { colors: currentTheme.secondary },
    },
    annotations: {
      yaxis: [
        {
          y: bBase,
          borderColor: '#56CA00',
          strokeDashArray: 4,
          label: {
            text: `Budget Baseline: ${bBase} L/BCM`,
            style: { color: '#fff', background: '#56CA00', fontSize: '11px', fontWeight: 600 },
          },
        },
        {
          y: wThresh,
          y2: cThresh,
          fillColor: '#FEF7E0',
          opacity: 0.35,
          label: {
            text: `Warning Zone (+8% ~ ${wThresh})`,
            style: { color: '#fff', background: '#FFB400', fontSize: '11px', fontWeight: 600 },
          },
        },
        {
          y: cThresh,
          y2: 1.45,
          fillColor: '#FCE8E6',
          opacity: 0.35,
          label: {
            text: `Critical Zone (+18% ~ ${cThresh})`,
            style: { color: '#fff', background: '#E53935', fontSize: '11px', fontWeight: 600 },
          },
        },
      ],
      xaxis: firstFcLabel ? [
        {
          x: firstFcLabel,
          borderColor: '#1E88E5',
          strokeDashArray: 4,
          label: {
            text: 'Forecast Projection (7 Days)',
            orientation: 'vertical',
            style: { color: '#fff', background: '#1E88E5', fontSize: '11px', fontWeight: 600 },
          },
        },
      ] : [],
    },
    tooltip: {
      y: {
        formatter: (v: number | null) => (v !== null && v !== undefined ? `${v.toFixed(4)} L/BCM` : 'N/A'),
      },
    },
  }
})

const series = computed(() => [
  { name: 'Actual Fuel Ratio (FMS DB)', data: actualFrSeries.value },
  { name: 'XGBoost 7-Day Forecast', data: forecastFrSeries.value },
])
</script>

<template>
  <VCard>
    <VCardItem>
      <template #append>
        <VBtn
          size="small"
          variant="tonal"
          color="primary"
          prepend-icon="bx-refresh"
          :loading="isLoading"
          @click="loadChartData"
        >
          Refresh AI Chart
        </VBtn>
      </template>
      <VCardTitle>Time-Series Forecast & Dynamic Threshold Zones</VCardTitle>
      <VCardSubtitle>Visualisasi 30 hari data historis DB + 7 hari proyeksi prediksi XGBoost</VCardSubtitle>
    </VCardItem>

    <VCardText class="pa-4">
      <VueApexCharts
        type="line"
        :height="420"
        :options="chartOptions"
        :series="series"
      />
    </VCardText>
  </VCard>
</template>

<style lang="scss">
@use "@core-scss/template/libs/apex-chart.scss";
</style>
