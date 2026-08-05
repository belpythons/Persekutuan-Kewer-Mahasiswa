<script setup lang="ts">
import type { SpikeReportPerUnit } from '@/composables/useAiApi'

interface Props {
  spikeReport: SpikeReportPerUnit[] | null
  isLoading: boolean
}

const props = withDefaults(defineProps<Props>(), {
  spikeReport: null,
  isLoading: false,
})

interface AnomalousUnit {
  rank: number
  unitCode: string
  activity: string
  spikeCount: number
  fcNormal: number
  fcSpike: number
  maxFr: number | null
}

// Default data (fallback)
const defaultUnits: AnomalousUnit[] = [
  { rank: 1, unitCode: 'HD785-7', activity: 'Hauling', spikeCount: 366, fcNormal: 77.0, fcSpike: 80.78, maxFr: 182.24 },
  { rank: 2, unitCode: 'EX2600-6', activity: 'Loading', spikeCount: 366, fcNormal: 187.0, fcSpike: 192.28, maxFr: null },
  { rank: 3, unitCode: 'PC2000-11R', activity: 'Loading', spikeCount: 9, fcNormal: 100.0, fcSpike: 185.53, maxFr: null },
  { rank: 4, unitCode: 'EGS380-6', activity: 'Dewatering', spikeCount: 9, fcNormal: 10.0, fcSpike: 10.70, maxFr: null },
  { rank: 5, unitCode: 'D375A6R', activity: 'Supporting', spikeCount: 5, fcNormal: 67.0, fcSpike: 72.10, maxFr: null },
]

const topUnits = computed<AnomalousUnit[]>(() => {
  if (!props.spikeReport) return []
  if (props.spikeReport.length === 0) return []

  return props.spikeReport
    .sort((a, b) => b.total_spikes - a.total_spikes)
    .slice(0, 5)
    .map((item, idx) => ({
      rank: idx + 1,
      unitCode: item.unit,
      activity: item.activity.charAt(0).toUpperCase() + item.activity.slice(1).toLowerCase(),
      spikeCount: item.total_spikes,
      fcNormal: item.avg_fc_normal,
      fcSpike: item.avg_fc_spike,
      maxFr: item.max_fr_recorded > 0 ? item.max_fr_recorded : null,
    }))
})

const activityColor = (activity: string) => {
  switch (activity) {
    case 'Hauling': return 'info'
    case 'Loading': return 'primary'
    case 'Supporting': return 'warning'
    case 'Dewatering': return 'secondary'
    default: return 'default'
  }
}

const fcDeviation = (normal: number, spike: number) => {
  if (normal === 0) return '0.0'
  return (((spike - normal) / normal) * 100).toFixed(1)
}
</script>

<template>
  <VCard>
    <VCardItem>
      <template #prepend>
        <VAvatar
          color="warning"
          variant="tonal"
          size="48"
          rounded
        >
          <VIcon
            icon="bx-trophy"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        Top Anomalous Units
      </VCardTitle>
      <VCardSubtitle>Leaderboard Spike Tertinggi</VCardSubtitle>
    </VCardItem>

    <VCardText class="pb-1">
      <VTable
        density="compact"
        class="text-no-wrap"
      >
        <thead>
          <tr>
            <th>#</th>
            <th>Unit</th>
            <th>Activity</th>
            <th class="text-end">
              Spikes
            </th>
            <th class="text-end">
              FC Normal
            </th>
            <th class="text-end">
              FC Spike
            </th>
            <th class="text-end">
              Deviasi
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="topUnits.length === 0">
            <td colspan="7" class="text-center py-6 text-medium-emphasis">
              <VIcon icon="bx-check-shield" size="32" class="mb-1 text-success d-block mx-auto" />
              Tidak ada anomali spike unit terdeteksi hari ini.
            </td>
          </tr>
          <tr
            v-for="unit in topUnits"
            :key="unit.rank"
            v-else
          >
            <td>
              <VAvatar
                :color="unit.rank <= 3 ? 'error' : 'default'"
                :variant="unit.rank <= 3 ? 'tonal' : 'outlined'"
                size="28"
                rounded
              >
                <span class="text-caption font-weight-bold">{{ unit.rank }}</span>
              </VAvatar>
            </td>
            <td>
              <span class="font-weight-bold" style="font-family: monospace;">{{ unit.unitCode }}</span>
            </td>
            <td>
              <VChip
                :color="activityColor(unit.activity)"
                size="small"
                variant="tonal"
              >
                {{ unit.activity }}
              </VChip>
            </td>
            <td class="text-end">
              <VChip
                color="error"
                size="small"
                variant="flat"
              >
                {{ unit.spikeCount }}
              </VChip>
            </td>
            <td class="text-end text-medium-emphasis">
              {{ unit.fcNormal }} L/hr
            </td>
            <td class="text-end font-weight-bold text-error">
              {{ unit.fcSpike }} L/hr
            </td>
            <td class="text-end">
              <span class="text-error font-weight-medium">+{{ fcDeviation(unit.fcNormal, unit.fcSpike) }}%</span>
            </td>
          </tr>
        </tbody>
      </VTable>
    </VCardText>
  </VCard>
</template>
