<script setup lang="ts">
interface WeatherData {
  rainfall_mm: number
  temperature_c: number
  wind_speed_kmh: number
  humidity_pct: number
  location: string
  lat: number
  lon: number
}

const weather = ref<WeatherData>({
  rainfall_mm: 0.0,
  temperature_c: 31.5,
  wind_speed_kmh: 12.0,
  humidity_pct: 78,
  location: 'Bontang / East Kalimantan Pit',
  lat: -0.13,
  lon: 117.45,
})

// Formulas from PRD:
// Haul Distance = 3900m + (Rainfall mm * 8m)
// Rain Derating Factor = min(0.50, Rainfall mm * 0.015)
const haulDistanceM = computed(() => 3900 + (weather.value.rainfall_mm * 8))
const rainDeratingFactor = computed(() => Math.min(0.50, weather.value.rainfall_mm * 0.015))
const rainDeratingPct = computed(() => (rainDeratingFactor.value * 100).toFixed(1))

const rainStatus = computed(() => {
  if (weather.value.rainfall_mm === 0) return { label: 'DRY', color: 'success', icon: 'bx-sun', desc: 'No Fleet Derating — Standard Haul Distance 3,900m' }
  if (weather.value.rainfall_mm < 10) return { label: 'LIGHT RAIN', color: 'info', icon: 'bx-cloud-rain', desc: `Derating: -${rainDeratingPct.value}% | Slippery road risk` }
  if (weather.value.rainfall_mm < 30) return { label: 'MODERATE RAIN', color: 'warning', icon: 'bx-cloud-lightning', desc: `Derating: -${rainDeratingPct.value}% | Significant speed reduction` }
  return { label: 'HEAVY RAIN (CRITICAL)', color: 'error', icon: 'bx-cloud-heavy-rain', desc: `Derating: -${rainDeratingPct.value}% | High slippage, potential stop` }
})
</script>

<template>
  <VCard>
    <VCardItem>
      <template #prepend>
        <VAvatar
          :color="rainStatus.color"
          variant="tonal"
          size="48"
          rounded
        >
          <VIcon
            :icon="rainStatus.icon"
            size="28"
          />
        </VAvatar>
      </template>
      <VCardTitle class="text-body-1 font-weight-medium">
        Open-Meteo Weather Risk & Rain Derating Radar
      </VCardTitle>
      <VCardSubtitle>
        {{ weather.location }} (Lat: {{ weather.lat }}, Lon: {{ weather.lon }})
      </VCardSubtitle>
      <template #append>
        <VChip
          :color="rainStatus.color"
          variant="flat"
          class="font-weight-bold"
        >
          {{ rainStatus.label }}
        </VChip>
      </template>
    </VCardItem>

    <VCardText>
      <VRow>
        <VCol
          cols="6"
          sm="3"
        >
          <div class="d-flex align-center gap-2">
            <VAvatar
              color="info"
              variant="tonal"
              size="38"
              rounded
            >
              <VIcon
                icon="bx-cloud-rain"
                size="20"
              />
            </VAvatar>
            <div>
              <span class="text-caption text-medium-emphasis">Curah Hujan</span>
              <h5 class="text-h5 font-weight-bold">
                {{ weather.rainfall_mm.toFixed(2) }} mm/h
              </h5>
            </div>
          </div>
        </VCol>

        <VCol
          cols="6"
          sm="3"
        >
          <div class="d-flex align-center gap-2">
            <VAvatar
              color="warning"
              variant="tonal"
              size="38"
              rounded
            >
              <VIcon
                icon="bx-sun"
                size="20"
              />
            </VAvatar>
            <div>
              <span class="text-caption text-medium-emphasis">Suhu Pit</span>
              <h5 class="text-h5 font-weight-bold">
                {{ weather.temperature_c }}°C
              </h5>
            </div>
          </div>
        </VCol>

        <VCol
          cols="6"
          sm="3"
        >
          <div class="d-flex align-center gap-2">
            <VAvatar
              color="secondary"
              variant="tonal"
              size="38"
              rounded
            >
              <VIcon
                icon="bx-wind"
                size="20"
              />
            </VAvatar>
            <div>
              <span class="text-caption text-medium-emphasis">Kecepatan Angin</span>
              <h5 class="text-h5 font-weight-bold">
                {{ weather.wind_speed_kmh }} km/h
              </h5>
            </div>
          </div>
        </VCol>

        <VCol
          cols="6"
          sm="3"
        >
          <div class="d-flex align-center gap-2">
            <VAvatar
              color="primary"
              variant="tonal"
              size="38"
              rounded
            >
              <VIcon
                icon="bx-navigation"
                size="20"
              />
            </VAvatar>
            <div>
              <span class="text-caption text-medium-emphasis">Impact Haul Dist</span>
              <h5 class="text-h5 font-weight-bold">
                {{ haulDistanceM.toLocaleString('id-ID') }} m
              </h5>
            </div>
          </div>
        </VCol>
      </VRow>

      <VDivider class="my-3" />

      <div class="d-flex align-center justify-space-between text-body-2">
        <div class="d-flex align-center gap-2">
          <VIcon
            icon="bx-info-circle"
            size="18"
            :color="rainStatus.color"
          />
          <span>{{ rainStatus.desc }}</span>
        </div>
        <div>
          <span class="text-medium-emphasis">Derating Factor: </span>
          <strong :class="`text-${rainStatus.color}`">{{ rainDeratingPct }}%</strong>
        </div>
      </div>
    </VCardText>
  </VCard>
</template>
