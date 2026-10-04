<script setup lang="ts">
import ScenarioSimulatorControls from '@/views/forecasting/ScenarioSimulatorControls.vue'
import ModelMetricsCard from '@/views/forecasting/ModelMetricsCard.vue'
import TimeSeriesForecastChart from '@/views/forecasting/TimeSeriesForecastChart.vue'
import MiningFuelChatbotWidget from '@/views/forecasting/MiningFuelChatbotWidget.vue'
import ActualVsForecastTable from '@/views/dashboard/ActualVsForecastTable.vue'
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-h4 font-weight-bold tracking-tight">
        Forecasting Analytics & Mining Fuel AI
      </h1>
      <p class="text-body-2 text-medium-emphasis mb-0">
        Simulasi skenario prediktif, analisis grafik deret waktu, dan interaksi cerdas dengan Mining Fuel AI Assistant
      </p>
    </div>

    <!-- MAIN BALANCED GRID -->
    <VRow class="match-height gy-6">
      <!-- ZONE 1: SCENARIO SIMULATOR & MODEL METRICS -->
      <VCol cols="12" lg="7">
        <ScenarioSimulatorControls class="h-100" />
      </VCol>

      <VCol cols="12" lg="5">
        <ModelMetricsCard class="h-100" />
      </VCol>

      <!-- ZONE 2 & ZONE 3: TIME-SERIES CHART + CHATBOT ASSISTANT -->
      <VCol cols="12" lg="7">
        <TimeSeriesForecastChart class="h-100" />
      </VCol>

      <VCol cols="12" lg="5">
        <MiningFuelChatbotWidget class="h-100" />
      </VCol>

      <!-- ZONE 4: DETAIL AUDIT TABLE -->
      <VCol cols="12">
        <ActualVsForecastTable />
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
