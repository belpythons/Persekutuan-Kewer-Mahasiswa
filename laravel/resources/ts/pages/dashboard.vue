<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { ForecastResponse, AnomalyDetectResponse, CapacityResponse } from '@/composables/useAiApi'
import DynamicThresholdAlertWidget from '@/views/dashboard/DynamicThresholdAlertWidget.vue'
import PyTorchSpikeSummaryWidget from '@/views/dashboard/PyTorchSpikeSummaryWidget.vue'
import TopAnomalousLeaderboard from '@/views/dashboard/TopAnomalousLeaderboard.vue'
import ActivityFuelDonutChart from '@/views/dashboard/ActivityFuelDonutChart.vue'
import OpenMeteoWeatherCard from '@/views/support/OpenMeteoWeatherCard.vue'

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

  try {
    // 1. Fetch Forecast (Base)
    const forecastResult = await fetchForecast({ date: today })
    forecastData.value = forecastResult

    // 2. Fetch Capacity (Dependent on Forecast Production & Weather)
    const capacityResult = await fetchCalculateCapacity({
      date: today,
      forecast_prod_bcm: forecastResult.daily_prod_bcm || 40000.0,
      curah_hujan_mm: forecastResult.features_input?.Curah_Hujan_mm || 0.0,
    })
    capacityData.value = capacityResult

    // 3. Fetch Anomaly (Empty records triggers Python DB Fallback for today)
    const anomalyResult = await fetchAnomalyDetect([])
    anomalyData.value = anomalyResult

  } catch (error) {
    console.error("Failed to load AI Dashboard data:", error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div>
    <!-- SECTION HEADER -->
    <div class="d-flex flex-column flex-sm-row justify-space-between align-start align-sm-center mb-6 gap-2">
      <div>
        <h1 class="text-h4 font-weight-bold tracking-tight">
          AI Operation Dashboard
        </h1>
        <span class="text-body-2 text-medium-emphasis">
          Real-time Fuel Ratio & Fleet Anomaly Monitoring Engine
        </span>
      </div>
      <VChip
        color="success"
        size="small"
        variant="tonal"
        class="font-weight-bold"
      >
        <VIcon start icon="bx-wifi" size="16" />
        Python AI Engine Active
      </VChip>
    </div>

    <!-- MAIN GRID - 100% Dynamic API Powered -->
    <VRow class="match-height">
      <!-- ZONE 0: REAL-TIME WEATHER RADAR CARD -->
      <VCol cols="12" class="mb-1">
        <OpenMeteoWeatherCard />
      </VCol>

      <!-- TOP METRIC 1: FORECAST ALERT -->
      <VCol cols="12" sm="6" lg="4">
        <DynamicThresholdAlertWidget
          :actual-fr="forecastData?.forecast_fr ?? 1.0180"
          :budget-baseline="1.0180"
          :warning-threshold="forecastData?.warning_threshold ?? 1.0994"
          :critical-threshold="forecastData?.critical_threshold ?? 1.2012"
          :excess-fuel-liters="0"
          :is-loading="isLoading"
          class="h-100"
        />
      </VCol>

      <!-- TOP METRIC 2: PYTORCH ANOMALY SPIKES -->
      <VCol cols="12" sm="6" lg="4">
        <PyTorchSpikeSummaryWidget
          :total-spikes="anomalyData?.total_spikes_detected ?? 0"
          :anomalous-units-count="anomalyData?.spike_report_per_unit?.length ?? 0"
          :total-fleet-units="anomalyData?.total_records_scanned ?? 0"
          :is-loading="isLoading"
          class="h-100"
        />
      </VCol>

      <!-- TOP METRIC 3: ACTIVITY FUEL ALLOCATION DONUT -->
      <VCol cols="12" sm="12" lg="4">
        <ActivityFuelDonutChart
          :activity-breakdown="capacityData?.activity_breakdown ?? null"
          :total-fuel="capacityData?.total_combined_fuel_lday ?? null"
          class="h-100"
        />
      </VCol>

      <!-- LEADERBOARD TABLE -->
      <VCol cols="12" class="mt-1">
        <TopAnomalousLeaderboard
          :spike-report="anomalyData?.spike_report_per_unit ?? null"
          :is-loading="isLoading"
        />
      </VCol>
    </VRow>
  </div>
</template>

<style scoped>
.h-100 {
  height: 100%;
}
.tracking-tight {
  letter-spacing: -0.5px;
}
</style>
