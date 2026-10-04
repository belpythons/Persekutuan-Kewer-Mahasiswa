/**
 * useAiApi.ts — Composable untuk integrasi API AI Microservice
 *
 * Semua panggilan ke backend Laravel (/api/v1/*) yang meneruskan
 * request ke python-ai-service.
 */

// ============================================================
// Type Definitions (sesuai API response schema)
// ============================================================

export interface ForecastPayload {
  date: string
  curah_hujan_mm?: number
  temp_max_c?: number
  kecepatan_angin_kmh?: number
  haul_distance_m?: number
  daily_prod_bcm?: number
}

export interface ForecastResponse {
  log_date: string
  forecast_fr: number
  status: 'NORMAL' | 'WARNING' | 'CRITICAL'
  warning_threshold: number
  critical_threshold: number
  daily_prod_bcm: number
  haul_distance_m: number
  features_input?: Record<string, number>
  fallback?: boolean
  error?: string
}

export interface Forecast7DaysResponse {
  start_date: string
  end_date: string
  forecast_horizon_days: number
  summary: {
    avg_forecast_fr: number
    max_forecast_fr: number
    min_forecast_fr: number
    warning_alert_days: number
    critical_alert_days: number
  }
  daily_forecasts: ForecastResponse[]
}

export interface ForecastHistoryItem {
  log_date: string
  actual_fr: number
  forecast_fr: number
  status: string
  daily_prod_bcm: number
  haul_distance_m: number
}

export interface ForecastHistoryResponse {
  total: number
  historical_logs: ForecastHistoryItem[]
}

export interface AnomalyRecord {
  Date: string
  Unit: string
  Activity: string
  FC_Actual: number
  Unit_Fuel_L_Day: number
  Unit_FR: number
  Rain_mm: number
}

export interface AnomalySpikeItem {
  date: string
  unit: string
  activity: string
  fc_actual: number
  unit_fuel_l_day: number
  unit_fr: number
  rain_mm: number
  reconstruction_error: number
  threshold_used: number
  is_spike: number
}

export interface SpikeReportPerUnit {
  unit: string
  activity: string
  total_spikes: number
  avg_fc_normal: number
  avg_fc_spike: number
  max_fr_recorded: number
}

export interface DetailReportPerActivity {
  activity: string
  total_unit_types: number
  total_spike_events: number
  avg_unit_fr: number
  total_fuel_cons_l: number
}

export interface AnomalyDetectResponse {
  total_records_scanned: number
  total_spikes_detected: number
  spikes: AnomalySpikeItem[]
  spike_report_per_unit: SpikeReportPerUnit[]
  detail_report_per_activity: DetailReportPerActivity[]
  fallback?: boolean
  error?: string
}

export interface CapacityPayload {
  date: string
  forecast_prod_bcm: number
  curah_hujan_mm: number
  nn_spike_count_by_unit?: Record<string, number> | null
}

export interface ActivityBreakdown {
  activity: string
  unit_types_count: number
  total_fleet_qty: number
  operating_units: number
  prod_bcm_hr_total: number
  prod_bcm_day_effective: number
  fuel_l_hr_total: number
  combined_fuel_lday: number
}

export interface UnitBreakdown {
  unit_name: string
  activity: string
  total_qty: number
  operating_units: number
  prod_bcm_hr_unit: number
  prod_bcm_hr_total: number
  prod_bcm_day_total: number
  fuel_l_hr_unit: number
  fuel_l_hr_total: number
  fuel_l_day_total: number
  unit_fr: number
  spike_count_nn: number
}

export interface CapacityResponse {
  log_date: string
  forecast_prod_bcm: number
  curah_hujan_mm: number
  rain_derating_factor: number
  installed_prod_bcmhr: number
  effective_prod_bcmday: number
  utilization_pct: number
  total_fleet_qty: number
  operating_units: number
  total_combined_fuel_lday: number
  activity_breakdown: ActivityBreakdown[]
  unit_breakdown: UnitBreakdown[]
  fallback?: boolean
  error?: string
}

export interface UnitTuningComparison {
  unit_name: string
  activity: string
  fleet_qty: number
  std_fc_lhr: number
  tuned_fuel_allocation_lday: number
  actual_fuel_consumed_lday: number
  variance_liters: number
  variance_pct: number
  spike_anomaly_count: number
  tuning_status: 'EFFICIENT' | 'WARNING' | 'OVER_CONSUMPTION'
}

export interface GlobalCapacityTuningResponse {
  log_date: string
  tuning_parameters: {
    forecast_prod_bcm: number
    curah_hujan_mm: number
    rain_derating_factor: number
    operating_hours_per_day: number
  }
  global_capacity_summary: {
    installed_cap_bcmhr: number
    effective_cap_bcmday: number
    fleet_utilization_pct: number
    total_fleet_units: number
    required_operating_units: number
    standby_units: number
  }
  global_fuel_tuning_summary: {
    tuned_combined_fuel_lday: number
    actual_total_fuel_lday: number
    net_fuel_variance_lday: number
    overall_variance_pct: number
    global_tuning_status: 'OPTIMAL' | 'WARNING' | 'CRITICAL'
  }
  unit_tuning_comparison: UnitTuningComparison[]
  fallback?: boolean
}

export interface BmkgWeatherSyncItem {
  date: string
  curah_hujan_mm: number
  temp_max_c: number
  kecepatan_angin_kmh: number
  source: string
}

export interface BmkgWeatherSyncResponse {
  status: string
  source: string
  location: string
  records_synced: number
  data: BmkgWeatherSyncItem[]
  fallback?: boolean
}

export interface ChatbotQueryResponse {
  query: string
  response: string
  source: string
  db_context?: Record<string, any>
  fallback?: boolean
  error?: string
}

export interface WarmupDetails {
  status: string
  warmup_duration_ms?: number
  xgboost_warmed_up: boolean
  xgboost_warmup_ms?: number
  pytorch_autoencoder_warmed_up: boolean
  pytorch_warmup_ms?: number
  database_status: string
}

export interface ReadyResponse {
  status: string
  warmup_details: WarmupDetails
  error?: string
}

export interface HealthResponse {
  status: string
  environment?: string
  database?: {
    status: string
    dialects: string
  }
  error?: string
}

// ============================================================
// API Helper
// ============================================================

/**
 * Thrown by apiRequest() whenever Laravel answers with a non-2xx status (including its
 * `fallback: true` / 503 responses). `body` still carries whatever Laravel sent — including
 * the fallback payload — for callers that want to tell "AI service down" apart from a hard
 * network failure, but nothing reaches a caller labeled as live data unless the request
 * actually succeeded.
 */
export class AiApiError extends Error {
  constructor(message: string, public status: number, public body: any) {
    super(message)
    this.name = 'AiApiError'
  }
}

async function apiRequest<T>(method: string, url: string, body?: unknown): Promise<T> {
  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  }

  if (body && method !== 'GET') {
    options.body = JSON.stringify(body)
  }

  let response: Response
  try {
    response = await fetch(url, options)
  } catch (networkError) {
    throw new AiApiError('Tidak dapat menghubungi server', 0, null)
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new AiApiError(data?.error || `HTTP ${response.status}`, response.status, data)
  }

  return data as T
}

// ============================================================
// Composable
// ============================================================

export function useAiApi() {
  /**
   * POST /api/v1/forecast — Prediksi Fuel Ratio (XGBoost)
   */
  async function fetchForecast(payload: ForecastPayload): Promise<ForecastResponse> {
    return apiRequest<ForecastResponse>('POST', '/api/v1/forecast', payload)
  }

  /**
   * POST /api/v1/forecast-7days — Prediksi Horizon 7-Hari Fuel Ratio (XGBoost)
   */
  async function fetchForecast7Days(startDate?: string): Promise<Forecast7DaysResponse> {
    return apiRequest<Forecast7DaysResponse>('POST', '/api/v1/forecast-7days', {
      start_date: startDate || new Date().toISOString().slice(0, 10),
    })
  }

  /**
   * GET /api/v1/forecast-history — Log historis Fuel Ratio harian dari DB
   */
  async function fetchForecastHistory(days = 30): Promise<ForecastHistoryResponse> {
    return apiRequest<ForecastHistoryResponse>('GET', `/api/v1/forecast-history?days=${days}`)
  }

  /**
   * POST /api/v1/anomaly-detect — Deteksi spike BBM (PyTorch Autoencoder)
   */
  async function fetchAnomalyDetect(records: AnomalyRecord[]): Promise<AnomalyDetectResponse> {
    return apiRequest<AnomalyDetectResponse>('POST', '/api/v1/anomaly-detect', { records })
  }

  /**
   * POST /api/v1/calculate-capacity — Kalkulasi kapasitas armada & alokasi solar
   */
  async function fetchCalculateCapacity(payload: CapacityPayload): Promise<CapacityResponse> {
    return apiRequest<CapacityResponse>('POST', '/api/v1/calculate-capacity', payload)
  }

  /**
   * POST /api/v1/global-capacity-tuning — Global Fleet Capacity Tuning & Variance Analysis (324 units)
   */
  async function fetchGlobalCapacityTuning(payload?: { date?: string; forecast_prod_bcm?: number; curah_hujan_mm?: number }): Promise<GlobalCapacityTuningResponse> {
    return apiRequest<GlobalCapacityTuningResponse>('POST', '/api/v1/global-capacity-tuning', payload || {})
  }

  /**
   * POST /api/v1/weather/sync-bmkg — Synchronize BMKG real-time weather
   */
  async function fetchSyncBmkgWeather(): Promise<BmkgWeatherSyncResponse> {
    return apiRequest<BmkgWeatherSyncResponse>('POST', '/api/v1/weather/sync-bmkg')
  }

  /**
   * POST /api/v1/chatbot/query — Mining Fuel AI Chatbot Assistant query
   */
  async function fetchChatbotQuery(query: string, history?: any[]): Promise<ChatbotQueryResponse> {
    return apiRequest<ChatbotQueryResponse>('POST', '/api/v1/chatbot/query', { query, history: history || [] })
  }

  /**
   * GET /api/v1/ai-health — Health check microservice
   */
  async function fetchAiHealth(): Promise<HealthResponse> {
    return apiRequest<HealthResponse>('GET', '/api/v1/ai-health')
  }

  /**
   * GET /api/v1/ai-ready — Readiness probe microservice
   */
  async function fetchAiReady(): Promise<ReadyResponse> {
    return apiRequest<ReadyResponse>('GET', '/api/v1/ai-ready')
  }

  return {
    fetchForecast,
    fetchForecast7Days,
    fetchForecastHistory,
    fetchAnomalyDetect,
    fetchCalculateCapacity,
    fetchGlobalCapacityTuning,
    fetchSyncBmkgWeather,
    fetchChatbotQuery,
    fetchAiHealth,
    fetchAiReady,
  }
}


