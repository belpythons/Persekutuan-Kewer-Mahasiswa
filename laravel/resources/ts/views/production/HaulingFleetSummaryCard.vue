<script setup lang="ts">
// Re-export LoadingFleetSummaryCard with Hauling defaults
import LoadingFleetSummaryCard from './LoadingFleetSummaryCard.vue'
</script>

<template>
  <LoadingFleetSummaryCard
    fleet-type="Hauling"
    :total-units="415"
    :active-units="94"
    :utilisation="22.46"
    :fleet-bcm-hr="45469.57"
    :fleet-fuel-hr="31955"
    :daily-fuel-allocation="652282.4"
    models="HD785-7: 400, HD785-8: 15"
  />
</template>
