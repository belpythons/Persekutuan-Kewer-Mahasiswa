<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { CapacityResponse, GlobalCapacityTuningResponse } from '@/composables/useAiApi'
import GlobalCapacityTuningCard from '@/views/production/GlobalCapacityTuningCard.vue'
import FleetCapacityOptimizerGrid from '@/views/production/FleetCapacityOptimizerGrid.vue'
import HourlyFleetCapacityMatrix from '@/views/production/HourlyFleetCapacityMatrix.vue'

const { fetchForecast, fetchCalculateCapacity, fetchGlobalCapacityTuning } = useAiApi()

const selectedShift = ref('Shift 1 (Day)')
const shifts = ['Shift 1 (Day)', 'Shift 2 (Night)']

const isLoading = ref(true)
const capacityData = ref<CapacityResponse | null>(null)
const tuningData = ref<GlobalCapacityTuningResponse | null>(null)

const syncGlobalCapacity = async () => {
  isLoading.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    const forecast = await fetchForecast({ date: today }).catch(() => null)

    const prodBcm = forecast?.daily_prod_bcm ?? 40000.0
    const rainMm = forecast?.features_input?.Curah_Hujan_mm ?? 5.0

    tuningData.value = await fetchGlobalCapacityTuning({
      date: today,
      forecast_prod_bcm: prodBcm,
      curah_hujan_mm: rainMm,
    })

    capacityData.value = await fetchCalculateCapacity({
      date: today,
      forecast_prod_bcm: prodBcm,
      curah_hujan_mm: rainMm,
    }).catch(() => null)
  } catch (error) {
    console.error('Fetch Global Capacity Tuning failed:', error)
    tuningData.value = null
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  syncGlobalCapacity()
})
</script>

<template>
  <div>
    <!-- Header Controls -->
    <div class="d-flex justify-space-between align-center flex-wrap mb-6 gap-4">
      <div>
        <h1 class="text-h4 font-weight-bold tracking-tight">
          Global Fleet Capacity Tuning
        </h1>
        <p class="text-body-2 text-medium-emphasis mb-0">
          Tuning alokasi kapasitas terpasang vs efektif (324 unit) & analisis variansi BBM harian
        </p>
      </div>

      <div class="d-flex align-center gap-3">
        <VSelect
          v-model="selectedShift"
          :items="shifts"
          density="compact"
          prepend-inner-icon="bx-time-five"
          style="min-width: 180px;"
        />
        <VBtn
          color="primary"
          prepend-icon="bx-refresh"
          variant="tonal"
          :loading="isLoading"
          @click="syncGlobalCapacity"
        >
          Sync Global Capacity API
        </VBtn>
      </div>
    </div>

    <!-- MAIN GRID - Global Capacity Tuning Powered -->
    <VRow>
      <!-- ZONE 1: GLOBAL FLEET CAPACITY TUNING CARD -->
      <VCol cols="12">
        <GlobalCapacityTuningCard
          :tuning-data="tuningData"
          :is-loading="isLoading"
        />
      </VCol>

      <!-- ZONE 2: COMBINED FLEET CAPACITY & FUEL ALLOCATION OPTIMIZER -->
    </VRow>
  </div>
</template>

<style scoped>
.tracking-tight {
  letter-spacing: -0.5px;
}
</style>
