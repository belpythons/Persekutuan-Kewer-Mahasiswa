<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { CapacityResponse } from '@/composables/useAiApi'
import LoadingFleetSummaryCard from '@/views/production/LoadingFleetSummaryCard.vue'
import HaulingFleetSummaryCard from '@/views/production/HaulingFleetSummaryCard.vue'
import FleetCapacityOptimizerGrid from '@/views/production/FleetCapacityOptimizerGrid.vue'
import HourlyFleetCapacityMatrix from '@/views/production/HourlyFleetCapacityMatrix.vue'

const { fetchForecast, fetchCalculateCapacity } = useAiApi()

const selectedShift = ref('Shift 1 (Day)')
const shifts = ['Shift 1 (Day)', 'Shift 2 (Night)']

const isLoading = ref(true)
const capacityData = ref<CapacityResponse | null>(null)

const loadingActivity = computed(() => {
  if (!capacityData.value?.activity_breakdown) return null
  return capacityData.value.activity_breakdown.find(a => a.activity.toUpperCase() === 'LOADING') ?? null
})

const haulingActivity = computed(() => {
  if (!capacityData.value?.activity_breakdown) return null
  return capacityData.value.activity_breakdown.find(a => a.activity.toUpperCase() === 'HAULING') ?? null
})

const syncData = async () => {
  isLoading.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    const forecast = await fetchForecast({ date: today }).catch(() => null)

    const prodBcm = forecast?.daily_prod_bcm ?? 40000.0
    const rainMm = forecast?.features_input?.Curah_Hujan_mm ?? 0.0

    capacityData.value = await fetchCalculateCapacity({
      date: today,
      forecast_prod_bcm: prodBcm,
      curah_hujan_mm: rainMm,
    })
  } catch (error) {
    console.error('Sync AI Engine failed:', error)
    capacityData.value = null
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  syncData()
})
</script>

<template>
  <div>
    <!-- Header Controls -->
    <div class="d-flex justify-space-between align-center flex-wrap mb-6 gap-4">
      <div>
        <h1 class="text-h4 font-weight-bold tracking-tight">
          Aktivitas Produksi & Kapasitas Fleet
        </h1>
        <p class="text-body-2 text-medium-emphasis mb-0">
          Monitoring armada produktif & penentuan alokasi kapasitas berbasis AI Engine
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
          @click="syncData"
        >
          Sync AI Engine
        </VBtn>
      </div>
    </div>

    <!-- MAIN GRID - 100% Dynamic API Powered -->
    <VRow>
      <!-- ZONE 1: REKAPITULASI FLEET PRODUKSI -->
      <VCol cols="12" md="6">
        <LoadingFleetSummaryCard
          :activity-data="loadingActivity"
          :is-loading="isLoading"
        />
      </VCol>

      <VCol cols="12" md="6">
        <HaulingFleetSummaryCard
          :activity-data="haulingActivity"
          :is-loading="isLoading"
        />
      </VCol>

      <!-- ZONE 2: COMBINED FLEET CAPACITY & FUEL ALLOCATION OPTIMIZER -->
      <VCol cols="12" class="mt-2">
        <FleetCapacityOptimizerGrid
          :activity-breakdown="capacityData?.activity_breakdown ?? null"
          :total-fuel="capacityData?.total_combined_fuel_lday ?? null"
        />
      </VCol>

      <!-- ZONE 3: HOURLY FLEET CAPACITY MATRIX TABLE -->
      <VCol cols="12" class="mt-2">
        <HourlyFleetCapacityMatrix
          :unit-breakdown="capacityData?.unit_breakdown ?? null"
        />
      </VCol>
    </VRow>
  </div>
</template>

<style scoped>
.tracking-tight {
  letter-spacing: -0.5px;
}
</style>
