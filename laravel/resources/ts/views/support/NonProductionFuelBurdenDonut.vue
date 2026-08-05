<script setup lang="ts">
import { useTheme } from 'vuetify'
import { hexToRgb } from '@core/utils/colorConverter'

const vuetifyTheme = useTheme()

const chartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors
  const variableTheme = vuetifyTheme.current.value.variables
  const primaryTextColor = `rgba(${hexToRgb(String(currentTheme['on-surface']))},${variableTheme['high-emphasis-opacity']})`

  return {
    chart: {
      type: 'donut' as const,
    },
    labels: ['Supporting (+0.2199 L/BCM)', 'Dewatering (+0.0800 L/BCM)', 'Production Fleet (+0.8577 L/BCM)'],
    colors: ['#F9AB00', '#7B61FF', '#1A73E8'],
    legend: {
      position: 'bottom' as const,
      fontSize: '12px',
      labels: { colors: primaryTextColor },
    },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            name: { show: true, fontSize: '13px' },
            value: { show: true, fontSize: '18px', fontWeight: 700 },
            total: {
              show: true,
              label: 'Non-Prod Burden',
              fontSize: '12px',
              formatter: () => '25.91% FR',
            },
          },
        },
      },
    },
    dataLabels: {
      enabled: true,
      formatter: (val: number) => `${val.toFixed(1)}%`,
    },
    tooltip: {
      y: { formatter: (v: number) => `${v.toLocaleString('id-ID')} L/hari` },
    },
  }
})

// Daily fuel liters: Supporting (200,582.4), Dewatering (113,085.8), Production (703,234.6)
const series = [200582.4, 113085.8, 703234.6]
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Zero-BCM Fuel Burden Analysis</VCardTitle>
      <VCardSubtitle>
        Beban Non-Produksi: <strong>313.668,2 L/hari</strong> (+0.2999 L/BCM / 25.91% dari Total FR)
      </VCardSubtitle>
    </VCardItem>
    <VCardText>
      <VueApexCharts
        type="donut"
        :height="320"
        :options="chartOptions"
        :series="series"
      />
    </VCardText>
  </VCard>
</template>

<style lang="scss">
@use "@core-scss/template/libs/apex-chart.scss";
</style>
