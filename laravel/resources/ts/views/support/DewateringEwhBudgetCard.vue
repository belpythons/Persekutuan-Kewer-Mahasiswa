<script setup lang="ts">
import SupportEwhBudgetCard from './SupportEwhBudgetCard.vue'
</script>

<template>
  <SupportEwhBudgetCard
    sector="Dewatering"
    :total-units="175"
    :annual-budget-ewh="1277500.0"
    :daily-fuel-l="113085.8"
    :fr-burden-lbcm="0.0800"
    :fr-burden-pct="6.91"
    icon="bx-droplet"
    color="secondary"
  />
</template>
