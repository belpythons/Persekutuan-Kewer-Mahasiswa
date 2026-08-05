<script setup lang="ts">
import type { ActivityBreakdown } from '@/composables/useAiApi'
import LoadingFleetSummaryCard from './LoadingFleetSummaryCard.vue'

interface Props {
  activityData: ActivityBreakdown | null
  isLoading?: boolean
}

defineProps<Props>()
</script>

<template>
  <LoadingFleetSummaryCard
    fleet-type="Hauling"
    :activity-data="activityData"
    :is-loading="isLoading"
  />
</template>
