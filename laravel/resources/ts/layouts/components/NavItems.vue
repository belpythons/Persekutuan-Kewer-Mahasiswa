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
      title: 'Support & Weather',
      icon: 'bx-cloud',
      to: '/support-weather-mlops',
    }"
  />
  <VerticalNavLink
    :item="{
      title: 'Forecasting & AI',
      icon: 'bx-brain',
      to: '/forecasting-ai',
    }"
  />

  <!-- 👉 Pengaturan -->
  <VerticalNavSectionTitle
    :item="{
      heading: 'Pengaturan',
    }"
  />
  <VerticalNavLink
    :item="{
      title: 'Account Settings',
      icon: 'bx-user',
      to: '/account-settings',
    }"
  />
</template>
