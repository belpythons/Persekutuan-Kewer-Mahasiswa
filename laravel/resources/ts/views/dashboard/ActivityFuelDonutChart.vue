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
    colors: ['#1A73E8', '#34A853', '#F9AB00', '#7B61FF'],
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
            name: { show: true, fontSize: '12px' },
            value: { show: true, fontSize: '18px', fontWeight: 700 },
            total: {
              show: true,
              label: 'Total Fuel',
              fontSize: '12px',
              formatter: () => `${totalFuelDisplay.value} L`,
            },
          },
        },
      },
    },
    dataLabels: {
      enabled: false,
    },
    tooltip: {
      y: { formatter: (v: number) => `${v.toLocaleString('id-ID')} L/hari` },
    },
  }
})
</script>

<template>
  <VCard class="border d-flex flex-column h-100">
    <VCardItem>
      <template #prepend>
        <VAvatar
          color="info"
          variant="tonal"
          size="44"
          rounded
        >
          <VIcon
            icon="bx-pie-chart-alt-2"
            size="24"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-bold">
        Distribusi Solar per Aktivitas
      </VCardTitle>
      <VCardSubtitle class="text-caption d-flex align-center gap-1">
        <span>Alokasi BBM Harian {{ totalFuelDisplay }} Liter</span>
        <VChip
          v-if="activityBreakdown"
          color="success"
          size="x-small"
          variant="tonal"
          class="font-weight-bold"
        >
          Live
        </VChip>
      </VCardSubtitle>
    </VCardItem>

    <VCardText class="flex-grow-1 d-flex flex-column justify-center pa-2">
      <div v-if="chartSeries.length === 0" class="d-flex flex-column align-center justify-center py-6 text-medium-emphasis">
        <VIcon icon="bx-pie-chart-alt-2" size="36" class="mb-2 opacity-50" />
        <span class="text-caption">Tidak ada data alokasi BBM aktivitas</span>
      </div>
      <VueApexCharts
        v-else
        type="donut"
        height="220"
        :options="chartOptions"
        :series="chartSeries"
      />
    </VCardText>
  </VCard>
</template>
