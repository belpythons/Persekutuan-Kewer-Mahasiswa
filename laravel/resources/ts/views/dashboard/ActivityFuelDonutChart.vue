<script setup lang="ts">
import { useTheme } from 'vuetify'
import { hexToRgb } from '@core/utils/colorConverter'
import type { ActivityBreakdown } from '@/composables/useAiApi'

interface Props {
  activityBreakdown: ActivityBreakdown[] | null
  totalFuel: number | null
}

const props = withDefaults(defineProps<Props>(), {
  activityBreakdown: null,
  totalFuel: null,
})

const vuetifyTheme = useTheme()

const chartLabels = computed(() => {
  if (!props.activityBreakdown || props.activityBreakdown.length === 0) return []
  return props.activityBreakdown.map(a => a.activity.charAt(0).toUpperCase() + a.activity.slice(1).toLowerCase())
})

const chartSeries = computed(() => {
  if (!props.activityBreakdown || props.activityBreakdown.length === 0) return []
  return props.activityBreakdown.map(a => Math.round(a.combined_fuel_lday))
})

const totalFuelDisplay = computed(() => {
  const total = props.totalFuel ?? 0
  return total.toLocaleString('id-ID')
})

const chartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors
  const variableTheme = vuetifyTheme.current.value.variables
  const primaryTextColor = `rgba(${hexToRgb(String(currentTheme['on-surface']))},${variableTheme['high-emphasis-opacity']})`

  return {
    chart: {
      type: 'donut' as const,
    },
    labels: chartLabels.value,
    colors: ['#1A73E8', '#F9AB00', '#34A853', '#7B61FF'],
    legend: {
      position: 'bottom' as const,
      fontSize: '13px',
      labels: { colors: primaryTextColor },
    },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            name: { show: true, fontSize: '14px' },
            value: { show: true, fontSize: '20px', fontWeight: 700 },
            total: {
              show: true,
              label: 'Total Fuel',
              fontSize: '14px',
              formatter: () => `${totalFuelDisplay.value} L`,
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
</script>

<template>
  <VCard>
    <VCardItem>
      <VCardTitle>Distribusi Konsumsi Solar per Aktivitas</VCardTitle>
      <VCardSubtitle>
        Alokasi BBM Harian {{ totalFuelDisplay }} Liter
        <VChip
          v-if="activityBreakdown"
          color="success"
          size="x-small"
          variant="tonal"
          class="ms-2"
        >
          Live
        </VChip>
      </VCardSubtitle>
    </VCardItem>
    <VCardText>
      <div v-if="chartSeries.length === 0" class="d-flex flex-column align-center justify-center py-8 text-medium-emphasis">
        <VIcon icon="bx-pie-chart-alt-2" size="40" class="mb-2 opacity-50" />
        <span>Tidak ada data alokasi BBM aktivitas</span>
      </div>
      <VueApexCharts
        v-else
        type="donut"
        :height="340"
        :options="chartOptions"
        :series="chartSeries"
      />
    </VCardText>
  </VCard>
</template>

<style lang="scss">
@use "@core-scss/template/libs/apex-chart.scss";
</style>
