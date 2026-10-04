<script setup lang="ts">
import { useAiApi } from '@/composables/useAiApi'

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

const { fetchSyncBmkgWeather } = useAiApi()

const isLoading = ref(true)
const isError = ref(false)

const weather = ref<RealtimeWeatherData>({
  rainfall_mm: 0.0,
  temperature_c: 0.0,
  apparent_temp_c: 0.0,
  wind_speed_kmh: 0.0,
  wind_direction_deg: 0,
  humidity_pct: 0,
  weather_code: 1,
  location: 'Kideco Paser Pit, Kalimantan Timur',
  lat: -1.82,
  lon: 115.89,
  last_updated: '-',
})

// hasFetchedOnce: the first request (success or failure) has returned, so the skeleton can go away.
// hasEverSucceeded: at least one real reading has landed — only then is it safe to show `weather` as live data.
const hasFetchedOnce = ref(false)
const hasEverSucceeded = ref(false)

const weatherCodeMap: Record<number, { desc: string; icon: string }> = {
  0: { desc: 'Cerah', icon: 'bx-sun' },
  1: { desc: 'Cerah Berawan', icon: 'bx-cloud' },
  2: { desc: 'Berawan Sebagian', icon: 'bx-cloud' },
  3: { desc: 'Berawan Mendung', icon: 'bx-cloud' },
  45: { desc: 'Kabut Tipis', icon: 'bx-cloud' },
  48: { desc: 'Kabut Tebal', icon: 'bx-cloud' },
  51: { desc: 'Gerimis Ringan', icon: 'bx-cloud-drizzle' },
  53: { desc: 'Gerimis Sedang', icon: 'bx-cloud-drizzle' },
  55: { desc: 'Gerimis Lebat', icon: 'bx-cloud-drizzle' },
  61: { desc: 'Hujan Ringan', icon: 'bx-cloud-rain' },
  63: { desc: 'Hujan Sedang', icon: 'bx-cloud-rain' },
  65: { desc: 'Hujan Lebat', icon: 'bx-cloud-rain' },
  80: { desc: 'Hujan Lokal', icon: 'bx-cloud-rain' },
  81: { desc: 'Hujan Deras', icon: 'bx-cloud-lightning' },
  82: { desc: 'Hujan Ekstrem', icon: 'bx-cloud-lightning' },
  95: { desc: 'Badai Petir', icon: 'bx-cloud-lightning' },
}

const weatherInfo = computed(() => {
  return weatherCodeMap[weather.value.weather_code] || { desc: 'Cerah Berawan', icon: 'bx-cloud' }
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

// Professional Corporate Mining Color Scheme (Clean, High Contrast, Non-Slop)
const rainStatus = computed(() => {
  const r = weather.value.rainfall_mm
  if (r === 0) return { label: 'DRY (OPERATIONAL)', color: 'success', icon: 'bx-sun', desc: 'Kondisi pit kering — Tidak ada derating hujan, jarak angkut standar 3.900m' }
  if (r <= 5) return { label: 'LIGHT RAIN', color: 'info', icon: 'bx-cloud-rain', desc: `Derating: -${rainDeratingPct.value}% | Pengawasan operasional jalan pit` }
  if (r <= 20) return { label: 'MODERATE RAIN', color: 'warning', icon: 'bx-cloud-lightning', desc: `Derating: -${rainDeratingPct.value}% | Risiko jalan licin, penurunan kecepatan` }
  return { label: 'HEAVY RAIN (CRITICAL)', color: 'error', icon: 'bx-cloud-heavy-rain', desc: `Derating: -${rainDeratingPct.value}% | Risiko slip tinggi, potensi pit stop` }
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
      weather.value.temperature_c = Number((c.temperature_2m ?? 28.3).toFixed(1))
      weather.value.apparent_temp_c = Number((c.apparent_temperature ?? 32.4).toFixed(1))
      weather.value.wind_speed_kmh = Number((c.wind_speed_10m ?? 8.2).toFixed(1))
      weather.value.wind_direction_deg = c.wind_direction_10m ?? 137
      weather.value.humidity_pct = c.relative_humidity_2m ?? 71
      weather.value.weather_code = c.weather_code ?? 1

      const now = new Date()
      weather.value.last_updated = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA'
      hasEverSucceeded.value = true
    }

    fetchSyncBmkgWeather().catch(() => null)
  } catch (err) {
    console.error('Failed to fetch real-time weather from Open-Meteo:', err)
    isError.value = true
    if (hasEverSucceeded.value) {
      weather.value.last_updated = 'Offline (' + new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WITA)'
    }
  } finally {
    isLoading.value = false
    hasFetchedOnce.value = true
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
  <VCard class="weather-card">
    <VCardItem class="pb-3">
      <template #prepend>
        <div class="header-icon-box me-3">
          <VIcon :icon="weatherInfo.icon" size="24" class="text-primary" />
        </div>
      </template>

      <VCardTitle class="d-flex align-center flex-wrap gap-2 text-h6 font-weight-bold tracking-tight">
        <span>Real-Time Weather & Rain Derating Radar</span>
        <VChip
          color="primary"
          size="x-small"
          variant="tonal"
          class="font-weight-medium ms-1"
        >
          BMKG / Open-Meteo
        </VChip>
      </VCardTitle>

      <VCardSubtitle class="d-flex align-center gap-1 text-caption text-medium-emphasis">
        <VIcon icon="bx-map-pin" size="14" class="text-primary" />
        <span>{{ weather.location }} (Lat: {{ weather.lat }}, Lon: {{ weather.lon }})</span>
        <span class="ms-2">• Sync: {{ weather.last_updated }}</span>
      </VCardSubtitle>

      <template #append>
        <div class="d-flex align-center gap-2">
          <VChip
            :color="rainStatus.color"
            variant="tonal"
            class="font-weight-bold px-3"
          >
            <VIcon :icon="rainStatus.icon" start size="16" />
            {{ rainStatus.label }}
          </VChip>
          <VBtn
            icon="bx-refresh"
            variant="tonal"
            size="small"
            color="secondary"
            :loading="isLoading"
            @click="fetchRealtimeWeather"
          />
        </div>
      </template>
    </VCardItem>

    <VCardText class="pt-1">
      <!-- LOADING STATE: first request still in flight -->
      <VRow v-if="isLoading && !hasFetchedOnce" density="comfortable">
        <VCol v-for="n in 4" :key="n" cols="12" sm="6" md="3">
          <VSkeletonLoader type="article" class="rounded-lg" />
        </VCol>
      </VRow>

      <!-- ERROR STATE: never got a single successful reading -->
      <div v-else-if="!hasEverSucceeded" class="d-flex flex-column align-center justify-center text-center py-8">
        <VIcon icon="bx-error-circle" size="48" class="text-error mb-3" />
        <p class="text-body-2 text-medium-emphasis mb-3">Gagal mengambil data cuaca real-time dari Open-Meteo</p>
        <VBtn variant="tonal" color="primary" size="small" :loading="isLoading" @click="fetchRealtimeWeather">
          Coba Lagi
        </VBtn>
      </div>

      <!-- LIVE STATE (optionally stale if the latest refresh failed) -->
      <template v-else>
        <VAlert
          v-if="isError"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-3"
        >
          Gagal memperbarui data terbaru — menampilkan data terakhir yang tersedia.
          <template #append>
            <VBtn size="x-small" variant="text" @click="fetchRealtimeWeather">Coba Lagi</VBtn>
          </template>
        </VAlert>

        <!-- CLEAN COMPACT STATS GRID -->
        <VRow density="comfortable">
          <!-- 1. CURAH HUJAN -->
          <VCol cols="12" sm="6" md="3">
            <div class="stat-item border rounded-lg p-3">
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-caption text-medium-emphasis font-weight-medium">Curah Hujan</span>
                <VIcon icon="bx-water" size="18" class="text-secondary" />
              </div>
              <div class="text-h5 font-weight-bold text-high-emphasis text-tabular-nums">
                {{ weather.rainfall_mm.toFixed(2) }} <span class="text-caption text-medium-emphasis">mm/h</span>
              </div>
              <div class="text-caption text-secondary font-weight-medium">
                {{ weatherInfo.desc }}
              </div>
            </div>
          </VCol>

          <!-- 2. SUHU PIT -->
          <VCol cols="12" sm="6" md="3">
            <div class="stat-item border rounded-lg p-3">
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-caption text-medium-emphasis font-weight-medium">Suhu Pit</span>
                <VIcon icon="bx-thermometer" size="18" class="text-warning" />
              </div>
              <div class="text-h5 font-weight-bold text-high-emphasis text-tabular-nums">
                {{ weather.temperature_c }}°C
              </div>
              <div class="text-caption text-medium-emphasis">
                Sensasi: {{ weather.apparent_temp_c }}°C
              </div>
            </div>
          </VCol>

          <!-- 3. KECEPATAN ANGIN & KELEMBAPAN -->
          <VCol cols="12" sm="6" md="3">
            <div class="stat-item border rounded-lg p-3">
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-caption text-medium-emphasis font-weight-medium">Angin & Lembap</span>
                <VIcon icon="bx-wind" size="18" class="text-primary" />
              </div>
              <div class="text-h5 font-weight-bold text-high-emphasis text-tabular-nums">
                {{ weather.wind_speed_kmh }} <span class="text-caption text-medium-emphasis">km/h</span>
              </div>
              <div class="text-caption text-medium-emphasis">
                {{ windCompass }} ({{ weather.humidity_pct }}% Humid)
              </div>
            </div>
          </VCol>

          <!-- 4. IMPACT HAUL DISTANCE (MINING HAUL TRUCK) -->
          <VCol cols="12" sm="6" md="3">
            <div class="stat-item border rounded-lg p-3">
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-caption text-medium-emphasis font-weight-medium">Impact Haul Distance</span>
                <VIcon icon="bx-car" size="18" class="text-primary" />
              </div>
              <div class="text-h5 font-weight-bold text-primary text-tabular-nums">
                {{ haulDistanceM.toLocaleString('id-ID') }} <span class="text-caption text-medium-emphasis">m</span>
              </div>
              <div class="text-caption font-weight-medium" :class="`text-${rainStatus.color}`">
                Rain Derating: -{{ rainDeratingPct }}%
              </div>
            </div>
          </VCol>
        </VRow>

        <VDivider class="my-3" />

        <!-- FOOTER SUMMARY BAR -->
        <div class="d-flex align-center justify-space-between flex-wrap gap-2 text-caption">
          <div class="d-flex align-center gap-2">
            <VIcon
              icon="bx-info-circle"
              size="16"
              :color="rainStatus.color"
            />
            <span class="font-weight-medium text-high-emphasis">{{ rainStatus.desc }}</span>
          </div>
          <div class="d-flex align-center gap-2">
            <span class="text-medium-emphasis">Faktor Derating: <strong class="text-high-emphasis">{{ rainDeratingFactor.toFixed(4) }}x</strong></span>
            <span class="text-medium-emphasis">• Formula Non-Linear Solusi #9</span>
          </div>
        </div>
      </template>
    </VCardText>
  </VCard>
</template>

<style scoped>
.weather-card {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.header-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: rgba(var(--v-theme-primary), 0.08);
}

.stat-item {
  background-color: rgba(var(--v-theme-surface), 0.5);
  border-color: rgba(var(--v-border-color), var(--v-border-opacity)) !important;
  transition: border-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
}

.stat-item:hover {
  border-color: rgba(var(--v-theme-primary), 0.3) !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(var(--v-theme-primary), 0.08);
}

.tracking-tight {
  letter-spacing: -0.3px;
}
</style>
