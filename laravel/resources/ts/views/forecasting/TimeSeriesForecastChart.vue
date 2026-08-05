<script setup lang="ts">
import { useTheme } from 'vuetify'
import { hexToRgb } from '@core/utils/colorConverter'

const vuetifyTheme = useTheme()

// 30 days historical + 7 days forecast
const categories = [
  '01/07', '02/07', '03/07', '04/07', '05/07', '06/07', '07/07', '08/07', '09/07', '10/07',
  '11/07', '12/07', '13/07', '14/07', '15/07', '16/07', '17/07', '18/07', '19/07', '20/07',
  '21/07', '22/07', '23/07', '24/07', '25/07', '26/07', '27/07', '28/07', '29/07', '30/07',
  '01/08 (FC)', '02/08 (FC)', '03/08 (FC)', '04/08 (FC)', '05/08 (FC)', '06/08 (FC)', '07/08 (FC)',
]

// Actual FR ends on day 30, null for forecast days
const actualFr = [
  1.148, 1.155, 1.162, 1.170, 1.158, 1.145, 1.180, 1.195, 1.210, 1.235,
  1.250, 1.245, 1.220, 1.198, 1.175, 1.160, 1.155, 1.170, 1.190, 1.225,
  1.260, 1.280, 1.275, 1.255, 1.230, 1.210, 1.195, 1.185, 1.175, 1.165,
  null, null, null, null, null, null, null,
]

// Forecast FR overlaps and continues for 7 days
const forecastFr = [
  null, null, null, null, null, null, null, null, null, null,
  null, null, null, null, null, null, null, null, null, null,
  null, null, null, null, null, null, null, null, null, 1.165,
  1.172, 1.185, 1.210, 1.285, 1.340, 1.295, 1.220,
]

const budgetBaseline = 1.1576
const warningThreshold = 1.2503
const criticalThreshold = 1.3660

const chartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors
  const variableTheme = vuetifyTheme.current.value.variables
  const disabledTextColor = `rgba(${hexToRgb(String(currentTheme['on-surface']))},${variableTheme['disabled-opacity']})`
  const borderColor = `rgba(${hexToRgb(String(variableTheme['border-color']))},${variableTheme['border-opacity']})`

  return {
    chart: {
      type: 'line' as const,
      parentHeightOffset: 0,
      toolbar: { show: true },
    },
    stroke: {
      curve: 'smooth' as const,
      width: [3, 3],
      dashArray: [0, 6],
    },
    colors: ['#1A73E8', '#00897B'],
    xaxis: {
      categories,
      labels: {
        style: { fontSize: '11px', colors: disabledTextColor },
        rotate: -45,
        rotateAlways: true,
      },
      tickAmount: 18,
    },
    yaxis: {
      min: 1.10,
      max: 1.45,
      labels: {
        style: { fontSize: '12px', colors: disabledTextColor },
        formatter: (v: number) => v.toFixed(3),
      },
    },
    grid: {
      strokeDashArray: 4,
      borderColor,
    },
    legend: {
      position: 'top' as const,
      horizontalAlign: 'left' as const,
      fontSize: '13px',
      labels: { colors: currentTheme.secondary },
    },
    annotations: {
      yaxis: [
        {
          y: budgetBaseline,
          borderColor: '#5F6368',
          strokeDashArray: 4,
          label: {
            text: `Budget Baseline: ${budgetBaseline} L/BCM`,
            style: { color: '#5F6368', background: 'transparent', fontSize: '11px' },
          },
        },
        {
          y: warningThreshold,
          y2: criticalThreshold,
          fillColor: '#FEF7E0',
          opacity: 0.35,
          label: {
            text: `Warning Zone (+8% ~ ${warningThreshold})`,
            style: { color: '#fff', background: '#f97316', fontSize: '11px' },
          },
        },
        {
          y: criticalThreshold,
          y2: 1.45,
          fillColor: '#FCE8E6',
          opacity: 0.35,
          label: {
            text: `Critical Zone (+18% ~ ${criticalThreshold})`,
            style: { color: '#fff', background: '#ef4444', fontSize: '11px' },
          },
        },
      ],
      xaxis: [
        {
          x: '01/08 (FC)',
          borderColor: '#00897B',
          strokeDashArray: 4,
          label: {
            text: 'Forecast Projection (7 Days)',
            orientation: 'vertical',
            style: { color: '#fff', background: '#00897B', fontSize: '11px' },
          },
        },
      ],
    },
    tooltip: {
      y: {
        formatter: (v: number | null) => (v ? `${v.toFixed(4)} L/BCM` : 'N/A'),
      },
    },
  }
})

const series = [
  { name: 'Actual Fuel Ratio (FMS)', data: actualFr },
  { name: 'XGBoost 7-Day Forecast', data: forecastFr },
]
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Time-Series Forecast & Dynamic Threshold Zones</VCardTitle>
      <VCardSubtitle>Visualisasi 30 hari data historis + 7 hari proyeksi prediksi XGBoost</VCardSubtitle>
    </VCardItem>

    <VCardText>
      <VueApexCharts
        type="line"
        :height="400"
        :options="chartOptions"
        :series="series"
      />
    </VCardText>
  </VCard>
</template>

<style lang="scss">
@use "@core-scss/template/libs/apex-chart.scss";
</style>
