<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'
import type { CapacityResponse } from '@/composables/useAiApi'
import LoadingFleetSummaryCard from '@/views/production/LoadingFleetSummaryCard.vue'
import HaulingFleetSummaryCard from '@/views/production/HaulingFleetSummaryCard.vue'
import CriticalEquipmentAlertBanner from '@/views/production/CriticalEquipmentAlertBanner.vue'
import FleetCapacityOptimizerGrid from '@/views/production/FleetCapacityOptimizerGrid.vue'
import SPOComplianceTable from '@/views/production/SPOComplianceTable.vue'
import HourlyFleetCapacityMatrix from '@/views/production/HourlyFleetCapacityMatrix.vue'

const { fetchCalculateCapacity } = useAiApi()

const selectedShift = ref('Shift 1 (Day)')
const shifts = ['Shift 1 (Day)', 'Shift 2 (Night)']

const isLoading = ref(true)
const capacityData = ref<CapacityResponse | null>(null)

const syncData = async () => {
  isLoading.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    capacityData.value = await fetchCalculateCapacity({
      date: today,
      forecast_prod_bcm: 250072,
      curah_hujan_mm: 12.5,
    })
  } catch {
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
  <VRow>
    <!-- Header Controls -->
    <VCol cols="12" class="d-flex justify-space-between align-center flex-wrap gap-4">
      <div>
        <h4 class="text-h4 font-weight-bold">
          Aktivitas Produksi & Kapasitas Fleet
        </h4>
        <p class="text-body-1 text-medium-emphasis mb-0">
          Monitoring armada produktif, SPO compliance, dan optimasi kapasitas berbasis AI
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
          Sync FMS
        </VBtn>
      </div>
    </VCol>

    <!-- ZONE 1: REKAPITULASI FLEET PRODUKSI -->
    <VCol
      cols="12"
      md="6"
    >
      <LoadingFleetSummaryCard />
    </VCol>

    <VCol
      cols="12"
      md="6"
    >
      <HaulingFleetSummaryCard />
    </VCol>

    <!-- ZONE 2: CRITICAL EQUIPMENT DETECTOR & SPO COMPLIANCE RADAR -->
    <VCol cols="12">
      <CriticalEquipmentAlertBanner />
    </VCol>

    <!-- ZONE 3: COMBINED FLEET CAPACITY & FUEL ALLOCATION OPTIMIZER -->
    <VCol cols="12">
      <FleetCapacityOptimizerGrid
        :activity-breakdown="capacityData?.activity_breakdown ?? null"
        :total-fuel="capacityData?.total_combined_fuel_lday ?? null"
      />
    </VCol>

    <!-- ZONE 4: TABEL AUDIT SPO COMPLIANCE -->
    <VCol cols="12">
      <SPOComplianceTable />
    </VCol>

    <!-- ZONE 5: HOURLY FLEET CAPACITY MATRIX TABLE -->
    <VCol cols="12">
      <HourlyFleetCapacityMatrix
        :unit-breakdown="capacityData?.unit_breakdown ?? null"
      />
    </VCol>
  </VRow>
</template>
