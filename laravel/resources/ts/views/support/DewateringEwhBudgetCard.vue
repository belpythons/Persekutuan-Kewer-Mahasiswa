<script setup lang="ts">
import SupportEwhBudgetCard from './SupportEwhBudgetCard.vue'
import type { EwhSector } from '@/composables/useAiApi'

interface Props {
  sector: EwhSector | null
  isLoading?: boolean
}

withDefaults(defineProps<Props>(), {
  sector: null,
  isLoading: false,
})
</script>

<template>
  <SupportEwhBudgetCard
    :sector="sector"
    :is-loading="isLoading"
    label="Dewatering"
    icon="bx-droplet"
    color="secondary"
  />
</template>
