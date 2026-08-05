<script setup lang="ts">
interface RealtimeWeatherData {
  rainfall_mm: number
  temperature_c: number
  apparent_temp_c: number
  wind_speed_kmh: number
  wind_direction_deg: number
  humidity_pct: number
  weather_code: number
  location: string
  lat: number
  lon: number
  last_updated: string
}

const isLoading = ref(true)
const isError = ref(false)

const weather = ref<RealtimeWeatherData>({
  rainfall_mm: 0.0,
  temperature_c: 29.6,
  apparent_temp_c: 33.3,
  wind_speed_kmh: 9.2,
  wind_direction_deg: 137,
  humidity_pct: 64,
  weather_code: 1,
  location: 'Kideco Paser Pit / East Kalimantan',
  lat: -1.82,
  lon: 115.89,
  last_updated: '-',
})

const weatherCodeMap: Record<number, { desc: string; icon: string }> = {
  0: { desc: 'Cerah', icon: 'bx-sun' },
  1: { desc: 'Cerah Berawan', icon: 'bx-cloud-sun' },
  2: { desc: 'Berawan Sebagian', icon: 'bx-cloud-sun' },
  3: { desc: 'Berawan Mendung', icon: 'bx-cloud' },
  45: { desc: 'Kabut Tipis', icon: 'bx-cloud' },
  48: { desc: 'Kabut Tebal', icon: 'bx-cloud' },
  51: { desc: 'Gerimis Ringan', icon: 'bx-cloud-drizzle' },
  53: { desc: 'Gerimis Sedang', icon: 'bx-cloud-drizzle' },
  55: { desc: 'Gerimis Lebat', icon: 'bx-cloud-drizzle' },
  61: { desc: 'Hujan Ringan', icon: 'bx-cloud-rain' },
  63: { desc: 'Hujan Sedang', icon: 'bx-cloud-rain' },
  65: { desc: 'Hujan Lebat', icon: 'bx-cloud-heavy-rain' },
  80: { desc: 'Hujan Lokal', icon: 'bx-cloud-rain' },
  81: { desc: 'Hujan Deras', icon: 'bx-cloud-lightning' },
  82: { desc: 'Hujan Ekstrem', icon: 'bx-cloud-lightning' },
  95: { desc: 'Badai Petir', icon: 'bx-cloud-lightning' },
}

const weatherInfo = computed(() => {
  return weatherCodeMap[weather.value.weather_code] || { desc: 'Cerah Berawan', icon: 'bx-cloud-sun' }
})

// Non-linear Derating Formula (Solusi Celah #9 Dokumen Bisnis)
const rainDeratingFactor = computed(() => {
  const r = weather.value.rainfall_mm
  if (r <= 5.0) return 1.0
  if (r <= 20.0) return Number((1.0 - 0.01 * Math.pow(r - 5.0, 1.3)).toFixed(4))
  if (r <= 50.0) return Number(Math.max(0.65, 0.82 - 0.005 * Math.pow(r - 20.0, 1.1)).toFixed(4))
  return 0.60
})

const rainDeratingPct = computed(() => {
  const loss = (1.0 - rainDeratingFactor.value) * 100
  return loss.toFixed(1)
})

const haulDistanceM = computed(() => Math.round(3900 + (weather.value.rainfall_mm * 8)))

// KIDECO BRAND COLORS: Focus strictly on Red & Blue Theme
const rainStatus = computed(() => {
  const r = weather.value.rainfall_mm
  if (r === 0) return { label: 'DRY (NORMAL)', color: 'primary', accentColor: '#1565C0', bgColor: '#E3F2FD', icon: 'bx-sun', desc: 'Kondisi kering — Tidak ada derating hujan, jarak angkut 3.900m' }
  if (r <= 5) return { label: 'LIGHT RAIN', color: 'primary', accentColor: '#1976D2', bgColor: '#E8F0FE', icon: 'bx-cloud-rain', desc: `Derating: -${rainDeratingPct.value}% | Pengawasan operasional jalan pit` }
  if (r <= 20) return { label: 'MODERATE RAIN', color: 'error', accentColor: '#E53935', bgColor: '#FFEBEE', icon: 'bx-cloud-lightning', desc: `Derating: -${rainDeratingPct.value}% | Risiko jalan licin, penurunan kecepatan` }
  return { label: 'HEAVY RAIN (CRITICAL)', color: 'error', accentColor: '#C5221F', bgColor: '#FCE8E6', icon: 'bx-cloud-heavy-rain', desc: `Derating: -${rainDeratingPct.value}% | Risiko slip tinggi, potensi pit stop` }
})

const windCompass = computed(() => {
  const deg = weather.value.wind_direction_deg
  const directions = ['Utara', 'Timur Laut', 'Timur', 'Tenggara', 'Selatan', 'Barat Daya', 'Barat', 'Barat Laut']
  const index = Math.round(deg / 45) % 8
  return directions[index]
})

const fetchRealtimeWeather = async () => {
  isLoading.value = true
  isError.value = false
  try {
    const url = 'https://api.open-meteo.com/v1/forecast?latitude=-1.82&longitude=115.89&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m&timezone=Asia%2FMakassar'
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP Error: ${res.status}`)

    const data = await res.json()
    if (data.current) {
      const c = data.current
      weather.value.rainfall_mm = Number((c.precipitation ?? c.rain ?? 0.0).toFixed(2))
      weather.value.temperature_c = Number((c.temperature_2m ?? 30.0).toFixed(1))
      weather.value.apparent_temp_c = Number((c.apparent_temperature ?? 33.0).toFixed(1))
      weather.value.wind_speed_kmh = Number((c.wind_speed_10m ?? 10.0).toFixed(1))
      weather.value.wind_direction_deg = c.wind_direction_10m ?? 0
      weather.value.humidity_pct = c.relative_humidity_2m ?? 65
      weather.value.weather_code = c.weather_code ?? 1

      const now = new Date()
      weather.value.last_updated = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA'
    }
  } catch (err) {
    console.error('Failed to fetch real-time weather from Open-Meteo:', err)
    isError.value = true
    weather.value.last_updated = 'Offline (' + new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA)'
  } finally {
    isLoading.value = false
  }
}

let refreshTimer: any = null

onMounted(() => {
  fetchRealtimeWeather()
  refreshTimer = setInterval(fetchRealtimeWeather, 180000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <VCard
    class="weather-card overflow-hidden"
    :style="{ borderLeft: `6px solid ${rainStatus.accentColor}` }"
  >
    <VCardItem class="pb-2">
      <template #prepend>
        <VAvatar
          :color="rainStatus.color"
          variant="tonal"
          size="48"
          rounded
        >
          <VIcon
            :icon="weatherInfo.icon"
            size="28"
          />
        </VAvatar>
      </template>

      <VCardTitle class="d-flex align-center flex-wrap gap-2 text-body-1 font-weight-bold">
        <span>Real-Time Weather Radar & Rain Derating</span>
        <VChip
          color="primary"
          size="x-small"
          variant="tonal"
          class="font-weight-bold"
        >
          <VIcon start icon="bx-wifi" size="14" />
          LIVE BMKG / Open-Meteo
        </VChip>
      </VCardTitle>

      <VCardSubtitle class="d-flex align-center gap-1">
        <VIcon icon="bx-map-pin" size="14" class="text-primary" />
        <span>{{ weather.location }} (Lat: {{ weather.lat }}, Lon: {{ weather.lon }})</span>
        <span class="text-caption text-medium-emphasis ms-2">• Sync: {{ weather.last_updated }}</span>
      </VCardSubtitle>

      <template #append>
        <div class="d-flex align-center gap-2">
          <VChip
            :color="rainStatus.color"
            variant="elevated"
            size="large"
            class="font-weight-bold"
          >
            <VIcon :icon="rainStatus.icon" start size="18" />
            {{ rainStatus.label }}
          </VChip>
          <VBtn
            icon="bx-refresh"
            variant="tonal"
            size="small"
            color="primary"
            :loading="isLoading"
            @click="fetchRealtimeWeather"
          />
        </div>
      </template>
    </VCardItem>

    <VCardText class="pt-2">
      <!-- 4 METRIC PANELS — STRICTLY KIDECO RED & BLUE THEME -->
      <VRow>
        <!-- 1. CURAH HUJAN (KIDECO BLUE) -->
        <VCol cols="12" sm="6" md="3">
          <VSheet
            rounded="lg"
            class="p-3 border d-flex align-center gap-3 metric-sheet"
            elevation="0"
          >
            <VAvatar
              color="primary"
              variant="tonal"
              size="42"
              rounded
            >
              <VIcon icon="bx-cloud-rain" size="22" />
            </VAvatar>
            <div>
              <span class="text-caption text-medium-emphasis">Curah Hujan</span>
              <h4 class="text-h4 font-weight-bold text-primary">
                {{ weather.rainfall_mm.toFixed(2) }} <span class="text-caption text-medium-emphasis">mm/h</span>
              </h4>
              <span class="text-caption text-primary font-weight-medium">
                {{ weatherInfo.desc }}
              </span>
            </div>
          </VSheet>
        </VCol>

        <!-- 2. SUHU PIT (KIDECO RED) -->
        <VCol cols="12" sm="6" md="3">
          <VSheet
            rounded="lg"
            class="p-3 border d-flex align-center gap-3 metric-sheet"
            elevation="0"
          >
            <VAvatar
              color="error"
              variant="tonal"
              size="42"
              rounded
            >
              <VIcon icon="bx-sun" size="22" />
            </VAvatar>
            <div>
              <span class="text-caption text-medium-emphasis">Suhu Pit</span>
              <h4 class="text-h4 font-weight-bold text-error">
                {{ weather.temperature_c }}°C
              </h4>
              <span class="text-caption text-medium-emphasis">
                Sensasi: {{ weather.apparent_temp_c }}°C
              </span>
            </div>
          </VSheet>
        </VCol>

        <!-- 3. KECEPATAN ANGIN & HUMIDITY (KIDECO BLUE) -->
        <VCol cols="12" sm="6" md="3">
          <VSheet
            rounded="lg"
            class="p-3 border d-flex align-center gap-3 metric-sheet"
            elevation="0"
          >
            <VAvatar
              color="primary"
              variant="tonal"
              size="42"
              rounded
            >
              <VIcon icon="bx-wind" size="22" />
            </VAvatar>
            <div>
              <span class="text-caption text-medium-emphasis">Angin & Lembap</span>
              <h4 class="text-h4 font-weight-bold text-primary">
                {{ weather.wind_speed_kmh }} <span class="text-caption text-medium-emphasis">km/h</span>
              </h4>
              <span class="text-caption text-medium-emphasis">
                {{ windCompass }} ({{ weather.humidity_pct }}%)
              </span>
            </div>
          </VSheet>
        </VCol>

        <!-- 4. IMPACT HAUL DISTANCE & DERATING (KIDECO RED) -->
        <VCol cols="12" sm="6" md="3">
          <VSheet
            rounded="lg"
            class="p-3 border d-flex align-center gap-3 metric-sheet"
            elevation="0"
          >
            <VAvatar
              color="error"
              variant="tonal"
              size="42"
              rounded
            >
              <VIcon icon="bx-navigation" size="22" />
            </VAvatar>
            <div>
              <span class="text-caption text-medium-emphasis">Impact Haul Dist</span>
              <h4 class="text-h4 font-weight-bold text-error">
                {{ haulDistanceM.toLocaleString('id-ID') }} <span class="text-caption text-medium-emphasis">m</span>
              </h4>
              <span class="text-caption font-weight-bold text-error">
                Derating: -{{ rainDeratingPct }}%
              </span>
            </div>
          </VSheet>
        </VCol>
      </VRow>

      <VDivider class="my-3" />

      <!-- FOOTER SUMMARY BAR — KIDECO RED & BLUE ACCENTS -->
      <div class="d-flex align-center justify-space-between flex-wrap gap-2 text-body-2">
        <div class="d-flex align-center gap-2">
          <VIcon
            icon="bx-info-circle"
            size="18"
            :color="rainStatus.color"
          />
          <span class="font-weight-medium">{{ rainStatus.desc }}</span>
        </div>
        <div class="d-flex align-center gap-2">
          <span class="text-caption text-medium-emphasis">Faktor Derating: <strong>{{ rainDeratingFactor.toFixed(4) }}x</strong></span>
          <VChip size="x-small" color="primary" variant="tonal" class="font-weight-medium">
            Formula Non-Linear Solusi Celah #9
          </VChip>
        </div>
      </div>
    </VCardText>
  </VCard>
</template>

<style scoped>
.weather-card {
  transition: all 0.25s ease-in-out;
}

.metric-sheet {
  background-color: rgba(var(--v-theme-surface), 0.6);
  border-color: rgba(var(--v-border-color), var(--v-border-opacity)) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-sheet:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}
</style>
