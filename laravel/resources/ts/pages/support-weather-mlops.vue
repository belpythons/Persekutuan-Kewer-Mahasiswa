<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { CapacityResponse, EwhBudgetResponse } from '@/composables/useAiApi'
import OpenMeteoWeatherCard from '@/views/support/OpenMeteoWeatherCard.vue'
import SupportEwhBudgetCard from '@/views/support/SupportEwhBudgetCard.vue'
import DewateringEwhBudgetCard from '@/views/support/DewateringEwhBudgetCard.vue'
import NonProductionFuelBurdenDonut from '@/views/support/NonProductionFuelBurdenDonut.vue'
import SupportDewateringEwhTable from '@/views/support/SupportDewateringEwhTable.vue'
import DynamicThresholdConfigCard from '@/views/support/DynamicThresholdConfigCard.vue'
import MLOpsModelRetrainCard from '@/views/support/MLOpsModelRetrainCard.vue'

const { fetchForecast, fetchCalculateCapacity, fetchEwhBudget } = useAiApi()

const isLoading = ref(true)
const capacityData = ref<CapacityResponse | null>(null)
const ewhData = ref<EwhBudgetResponse | null>(null)

const supportSector = computed(() => ewhData.value?.sectors.find(s => s.sector === 'SUPPORT') ?? null)
const dewateringSector = computed(() => ewhData.value?.sectors.find(s => s.sector === 'DEWATERING') ?? null)

async function loadData() {
  isLoading.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    const forecast = await fetchForecast({ date: today }).catch(() => null)
    const prodBcm = forecast?.daily_prod_bcm ?? 40000.0
    const rainMm = forecast?.features_input?.Curah_Hujan_mm ?? 0.0

    const [capacityResult, ewhResult] = await Promise.allSettled([
      fetchCalculateCapacity({ date: today, forecast_prod_bcm: prodBcm, curah_hujan_mm: rainMm }),
      fetchEwhBudget(prodBcm),
    ])

    capacityData.value = capacityResult.status === 'fulfilled' ? capacityResult.value : null
    ewhData.value = ewhResult.status === 'fulfilled' ? ewhResult.value : null
  } finally {
    isLoading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-h4 font-weight-bold tracking-tight">
        Support, Dewatering, Weather Risk & MLOps Config
      </h1>
      <p class="text-body-2 text-medium-emphasis mb-0">
        Monitoring EWH & beban solar non-produksi, risiko cuaca, dan kontrol retraining AI model
      </p>
    </div>

    <VRow class="match-height gy-6">
      <!-- ZONE 1: WEATHER RISK -->
      <VCol cols="12">
        <OpenMeteoWeatherCard />
      </VCol>

      <!-- ZONE 2: EWH BUDGET CARDS -->
      <VCol cols="12" md="6">
        <SupportEwhBudgetCard :sector="supportSector" :is-loading="isLoading" />
      </VCol>
      <VCol cols="12" md="6">
        <DewateringEwhBudgetCard :sector="dewateringSector" :is-loading="isLoading" />
      </VCol>

      <!-- ZONE 3: NON-PRODUCTION FUEL BURDEN DONUT -->
      <VCol cols="12">
        <NonProductionFuelBurdenDonut
          :activity-breakdown="capacityData?.activity_breakdown ?? null"
          :is-loading="isLoading"
        />
      </VCol>

      <!-- ZONE 4: EWH DETAIL TABLE -->
      <VCol cols="12">
        <SupportDewateringEwhTable :sectors="ewhData?.sectors ?? null" :is-loading="isLoading" />
      </VCol>

      <!-- ZONE 5: THRESHOLD CONFIG & MLOPS RETRAIN -->
      <VCol cols="12" md="6">
        <DynamicThresholdConfigCard />
      </VCol>
      <VCol cols="12" md="6">
        <MLOpsModelRetrainCard />
      </VCol>
    </VRow>
  </div>
</template>

<style scoped>
.tracking-tight {
  letter-spacing: -0.5px;
}
</style>
