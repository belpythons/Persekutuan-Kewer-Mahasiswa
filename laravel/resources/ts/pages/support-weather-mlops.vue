<script setup lang="ts">
import OpenMeteoWeatherCard from '@/views/support/OpenMeteoWeatherCard.vue'
import SupportEwhBudgetCard from '@/views/support/SupportEwhBudgetCard.vue'
import DewateringEwhBudgetCard from '@/views/support/DewateringEwhBudgetCard.vue'
import NonProductionFuelBurdenDonut from '@/views/support/NonProductionFuelBurdenDonut.vue'
import SupportDewateringEwhTable from '@/views/support/SupportDewateringEwhTable.vue'
import DynamicThresholdConfigCard from '@/views/support/DynamicThresholdConfigCard.vue'
import MLOpsModelRetrainCard from '@/views/support/MLOpsModelRetrainCard.vue'
</script>

<template>
  <VRow>
    <!-- Header -->
    <VCol cols="12">
      <h4 class="text-h4 font-weight-bold">
        Support, Dewatering, Weather Risk & MLOps
      </h4>
      <p class="text-body-1 text-medium-emphasis mb-0">
        Monitoring beban solar Zero-BCM, integrasi risiko cuaca Open-Meteo, dan panel kontrol MLOps
      </p>
    </VCol>

    <!-- ZONE 1: OPEN-METEO WEATHER RISK INTEGRATION CARD -->
    <VCol cols="12">
      <OpenMeteoWeatherCard />
    </VCol>

    <!-- ZONE 2: ZERO-BCM FUEL BURDEN & EWH BUDGET -->
    <VCol
      cols="12"
      md="6"
    >
      <SupportEwhBudgetCard />
    </VCol>

    <VCol
      cols="12"
      md="6"
    >
      <DewateringEwhBudgetCard />
    </VCol>

    <!-- ZONE 3: VISUALISASI DONUT CHART BEBAN SOLAR NON-PRODUKSI -->
    <VCol cols="12">
      <NonProductionFuelBurdenDonut />
    </VCol>

    <!-- ZONE 4: TABEL EWH & KONSUMSI SOLAR SUPPORT & DEWATERING -->
    <VCol cols="12">
      <SupportDewateringEwhTable />
    </VCol>

    <!-- ZONE 5: DYNAMIC ALERT THRESHOLD & MLOPS RETRAINING CONTROL -->
    <VCol
      cols="12"
      md="6"
    >
      <DynamicThresholdConfigCard />
    </VCol>

    <VCol
      cols="12"
      md="6"
    >
      <MLOpsModelRetrainCard />
    </VCol>
  </VRow>
</template>
