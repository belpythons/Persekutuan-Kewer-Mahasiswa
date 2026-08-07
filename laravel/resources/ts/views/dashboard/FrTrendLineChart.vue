<script setup lang="ts">
import { useTheme } from 'vuetify'
import { hexToRgb } from '@core/utils/colorConverter'

const vuetifyTheme = useTheme()

// Static data sesuai PRD — 30-day trend
const dates = Array.from({ length: 30 }, (_, i) => {
  const d = new Date(2026, 6, i + 1) // Juli 2026
  return `${d.getDate()}/${d.getMonth() + 1}`
})

const actualFrData = [
  1.148, 1.155, 1.162, 1.170, 1.158, 1.145, 1.180, 1.195, 1.210, 1.235,
  1.250, 1.245, 1.220, 1.198, 1.175, 1.160, 1.155, 1.170, 1.190, 1.225,
  1.260, 1.280, 1.275, 1.255, 1.230, 1.210, 1.195, 1.185, 1.175, 1.165,
]

const forecastFrData = [
  1.150, 1.158, 1.165, 1.168, 1.160, 1.148, 1.178, 1.192, 1.208, 1.230,
  1.248, 1.242, 1.218, 1.195, 1.172, 1.158, 1.152, 1.168, 1.188, 1.222,
  1.258, 1.278, 1.272, 1.252, 1.228, 1.208, 1.192, 1.182, 1.172, 1.162,
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
      zoom: { enabled: true },
    },
    stroke: {
      curve: 'smooth' as const,
      width: [4, 2],
      dashArray: [0, 5],
    },
    colors: ['#1E88E5', '#E53935'],
    xaxis: {
      categories: dates,
      labels: {
        style: { fontSize: '11px', colors: disabledTextColor },
        rotate: -45,
        rotateAlways: true,
      },
      tickAmount: 15,
    },
    yaxis: {
      min: 1.10,
      max: 1.40,
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
          borderColor: '#56CA00',
          strokeDashArray: 6,
          label: {
            text: `Budget ${budgetBaseline} L/BCM`,
            style: { color: '#fff', background: '#56CA00', fontSize: '11px', fontWeight: 600 },
          },
        },
        {
          y: warningThreshold,
          y2: criticalThreshold,
          fillColor: '#FEF7E0',
          opacity: 0.3,
          label: {
            text: `Warning +8% (${warningThreshold})`,
            style: { color: '#fff', background: '#FFB400', fontSize: '11px', fontWeight: 600 },
          },
        },
        {
          y: criticalThreshold,
          y2: 1.40,
          fillColor: '#FCE8E6',
          opacity: 0.3,
          label: {
            text: `Critical +18% (${criticalThreshold})`,
            style: { color: '#fff', background: '#E53935', fontSize: '11px', fontWeight: 600 },
          },
        },
      ],
    },
    tooltip: {
      y: { formatter: (v: number) => `${v.toFixed(4)} L/BCM` },
    },
  }
})

const series = [
  { name: 'Actual FR', data: actualFrData },
  { name: 'XGBoost Forecast FR', data: forecastFrData },
]
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>FR Trend 30-Day — Actual vs Forecast</VCardTitle>
      <VCardSubtitle>XGBoost Forecast dengan Dynamic Warning & Critical Threshold</VCardSubtitle>
    </VCardItem>
    <VCardText>
      <VueApexCharts
        type="line"
        :height="380"
        :options="chartOptions"
        :series="series"
      />
    </VCardText>
  </VCard>
</template>

<style lang="scss">
@use "@core-scss/template/libs/apex-chart.scss";
</style>
