<script lang="ts" setup>
import VerticalNavSectionTitle from '@/@layouts/components/VerticalNavSectionTitle.vue'
import VerticalNavLink from '@layouts/components/VerticalNavLink.vue'
</script>

<template>
  <!-- 👉 Monitoring Dashboard -->
  <VerticalNavSectionTitle
    :item="{
      heading: 'Monitoring',
    }"
  />
  <VerticalNavLink
    :item="{
      title: 'Dashboard',
      icon: 'bx-tachometer',
      to: '/dashboard',
    }"
  />
  <VerticalNavLink
    :item="{
      title: 'Produksi & Kapasitas',
      icon: 'bx-hard-hat',
      to: '/production-capacity',
    }"
  />
  <VerticalNavLink
    :item="{
      title: 'Global Capacity',
      icon: 'bx-slider-alt',
      to: '/global-capacity',
    }"
  />
  <VerticalNavLink
    :item="{
      title: 'Forecasting & AI',
      icon: 'bx-brain',
      to: '/forecasting-ai',
    }"
  />
</template>
