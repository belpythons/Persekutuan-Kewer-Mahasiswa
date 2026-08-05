<script setup lang="ts">
import ScenarioSimulatorControls from '@/views/forecasting/ScenarioSimulatorControls.vue'
import ModelMetricsCard from '@/views/forecasting/ModelMetricsCard.vue'
import TimeSeriesForecastChart from '@/views/forecasting/TimeSeriesForecastChart.vue'
import MiningFuelChatbotWidget from '@/views/forecasting/MiningFuelChatbotWidget.vue'
</script>

<template>
  <VRow>
    <!-- Header -->
    <VCol cols="12">
      <h4 class="text-h4 font-weight-bold">
        Forecasting Analytics & Mining Fuel AI
      </h4>
      <p class="text-body-1 text-medium-emphasis mb-0">
        Simulasi skenario prediktif, analisis grafik deret waktu, dan interaksi cerdas dengan Mining Fuel AI Assistant
      </p>
    </VCol>

    <!-- ZONE 1: SCENARIO SIMULATOR & MODEL METRICS -->
    <VCol
      cols="12"
      lg="7"
    >
      <ScenarioSimulatorControls />
    </VCol>

    <VCol
      cols="12"
      lg="5"
    >
      <ModelMetricsCard />
    </VCol>

    <!-- ZONE 2 & ZONE 3: TIME-SERIES CHART + CHATBOT ASSISTANT -->
    <VCol
      cols="12"
      lg="7"
    >
      <TimeSeriesForecastChart />
    </VCol>

    <VCol
      cols="12"
      lg="5"
    >
      <MiningFuelChatbotWidget />
    </VCol>
  </VRow>
</template>
