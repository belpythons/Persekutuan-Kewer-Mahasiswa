<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { ForecastResponse, AnomalyDetectResponse, CapacityResponse } from '@/composables/useAiApi'
import DynamicThresholdAlertWidget from '@/views/dashboard/DynamicThresholdAlertWidget.vue'
import PyTorchSpikeSummaryWidget from '@/views/dashboard/PyTorchSpikeSummaryWidget.vue'
import TopAnomalousLeaderboard from '@/views/dashboard/TopAnomalousLeaderboard.vue'
import FrTrendLineChart from '@/views/dashboard/FrTrendLineChart.vue'
import ActivityFuelDonutChart from '@/views/dashboard/ActivityFuelDonutChart.vue'
import ActualVsForecastTable from '@/views/dashboard/ActualVsForecastTable.vue'

const { fetchForecast, fetchAnomalyDetect, fetchCalculateCapacity } = useAiApi()

const isLoading = ref(true)

// Forecast data for alert widget
const forecastData = ref<ForecastResponse | null>(null)

// Anomaly data for spike summary + leaderboard
const anomalyData = ref<AnomalyDetectResponse | null>(null)

// Capacity data for donut chart
const capacityData = ref<CapacityResponse | null>(null)

onMounted(async () => {
  const today = new Date().toISOString().slice(0, 10)

  // Run all API calls in parallel — each one independent
  const [forecastResult, anomalyResult, capacityResult] = await Promise.allSettled([
    fetchForecast({
      date: today,
      curah_hujan_mm: 12.5,
      temp_max_c: 32.0,
      kecepatan_angin_kmh: 14.2,
      haul_distance_m: 4200.0,
      daily_prod_bcm: 45000.0,
    }),
    fetchAnomalyDetect([
      { Date: today, Unit: 'HD785-7', Activity: 'HAULING', FC_Actual: 75.0, Unit_Fuel_L_Day: 1500.0, Unit_FR: 0.26, Rain_mm: 5.0 },
      { Date: today, Unit: 'EX2600-6', Activity: 'LOADING', FC_Actual: 187.0, Unit_Fuel_L_Day: 3740.0, Unit_FR: 0.20, Rain_mm: 5.0 },
    ]),
    fetchCalculateCapacity({
      date: today,
      forecast_prod_bcm: 40000.0,
      curah_hujan_mm: 12.5,
    }),
  ])

  if (forecastResult.status === 'fulfilled') forecastData.value = forecastResult.value
  if (anomalyResult.status === 'fulfilled') anomalyData.value = anomalyResult.value
  if (capacityResult.status === 'fulfilled') capacityData.value = capacityResult.value

  isLoading.value = false
})
</script>

<template>
  <VRow>
    <!-- ZONE 1: HERO SECTION - ALERT & ANOMALY ENGINE -->
    <VCol
      cols="12"
      md="4"
    >
      <DynamicThresholdAlertWidget
        :actual-fr="forecastData?.forecast_fr ?? 1.2800"
        :budget-baseline="forecastData?.budget_baseline ?? 1.1576"
        :warning-threshold="forecastData?.warning_threshold ?? 1.2503"
        :critical-threshold="forecastData?.critical_threshold ?? 1.3660"
        :excess-fuel-liters="30612"
        :is-loading="isLoading"
      />
    </VCol>

    <VCol
      cols="12"
      md="4"
    >
      <PyTorchSpikeSummaryWidget
        :total-spikes="anomalyData?.total_spikes_detected ?? 375"
        :anomalous-units-count="anomalyData?.spike_report_per_unit?.length ?? 61"
        :total-fleet-units="anomalyData?.total_records_scanned ?? 843"
        :is-loading="isLoading"
      />
    </VCol>

    <VCol
      cols="12"
      md="4"
    >
      <TopAnomalousLeaderboard
        :spike-report="anomalyData?.spike_report_per_unit ?? null"
        :is-loading="isLoading"
      />
    </VCol>

    <!-- ZONE 2: VISUAL ANALYTICS WIDGETS -->
    <VCol
      cols="12"
      lg="8"
    >
      <FrTrendLineChart />
    </VCol>

    <VCol
      cols="12"
      lg="4"
    >
      <ActivityFuelDonutChart
        :activity-breakdown="capacityData?.activity_breakdown ?? null"
        :total-fuel="capacityData?.total_combined_fuel_lday ?? null"
      />
    </VCol>

    <!-- ZONE 3: MAIN DATA TABLE -->
    <VCol cols="12">
      <ActualVsForecastTable />
    </VCol>
  </VRow>
</template>
