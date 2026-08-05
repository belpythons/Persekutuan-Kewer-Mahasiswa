"""
Dashboard Web UI Routes — Tampilan sederhana untuk start microservice & melihat kalkulasi.
Slug Routes:
  /dashboard          → Halaman utama status & navigasi
  /dashboard/forecast → Form & hasil prediksi Fuel Ratio (Single Day & 7-Day Horizon)
  /dashboard/anomaly  → Form & hasil deteksi anomali unit
  /dashboard/capacity → Form & hasil kalkulasi kapasitas 24 jam
"""
import os
import sys
import json
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter(prefix="/dashboard", tags=["Dashboard UI"])

# ─── Shared CSS & Layout ───────────────────────────────────────────────
COMMON_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Inter',sans-serif; background:#0F172A; color:#E2E8F0; min-height:100vh; }
  .navbar { background:linear-gradient(135deg,#1E293B,#0F172A); border-bottom:1px solid #334155; padding:14px 32px; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:100; }
  .navbar .logo { font-size:18px; font-weight:700; color:#38BDF8; letter-spacing:-0.5px; }
  .navbar .logo span { color:#94A3B8; font-weight:400; font-size:13px; margin-left:8px; }
  .nav-links { display:flex; gap:6px; }
  .nav-links a { color:#94A3B8; text-decoration:none; padding:8px 16px; border-radius:8px; font-size:13px; font-weight:500; transition:all .2s; }
  .nav-links a:hover, .nav-links a.active { background:#1E293B; color:#38BDF8; }
  .container { max-width:1100px; margin:0 auto; padding:28px 24px; }
  h1 { font-size:26px; font-weight:700; color:#F1F5F9; margin-bottom:6px; }
  .subtitle { color:#64748B; font-size:14px; margin-bottom:24px; }
  .card { background:#1E293B; border:1px solid #334155; border-radius:12px; padding:24px; margin-bottom:20px; transition:border-color .2s; }
  .card:hover { border-color:#38BDF8; }
  .card h2 { font-size:16px; font-weight:600; color:#F1F5F9; margin-bottom:12px; }
  .card p { color:#94A3B8; font-size:13px; line-height:1.6; }
  .grid-3 { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px; }
  .badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
  .badge-green { background:#064E3B; color:#34D399; }
  .badge-yellow { background:#78350F; color:#FBBF24; }
  .badge-red { background:#7F1D1D; color:#F87171; }
  .badge-blue { background:#1E3A5F; color:#38BDF8; }
  .stat-value { font-size:32px; font-weight:700; color:#38BDF8; }
  .stat-label { font-size:12px; color:#64748B; margin-top:2px; }
  form { display:flex; flex-direction:column; gap:12px; }
  label { font-size:13px; font-weight:500; color:#CBD5E1; }
  input, select { background:#0F172A; border:1px solid #334155; color:#E2E8F0; padding:10px 14px; border-radius:8px; font-size:14px; font-family:inherit; }
  input:focus { outline:none; border-color:#38BDF8; box-shadow:0 0 0 3px rgba(56,189,248,.15); }
  button { background:linear-gradient(135deg,#0284C7,#0369A1); color:#fff; border:none; padding:12px 24px; border-radius:8px; font-size:14px; font-weight:600; cursor:pointer; transition:all .2s; }
  button:hover { transform:translateY(-1px); box-shadow:0 4px 12px rgba(2,132,199,.4); }
  button.secondary { background:linear-gradient(135deg,#475569,#334155); }
  button.secondary:hover { box-shadow:0 4px 12px rgba(71,85,105,.4); }
  .btn-group { display:flex; gap:12px; }
  .result-box { background:#0F172A; border:1px solid #334155; border-radius:8px; padding:16px; margin-top:16px; }
  .result-box pre { color:#94A3B8; font-size:12px; line-height:1.5; white-space:pre-wrap; word-break:break-all; font-family:'Courier New',monospace; }
  table { width:100%; border-collapse:collapse; margin-top:12px; }
  th { background:#334155; color:#CBD5E1; padding:10px 12px; text-align:left; font-size:12px; font-weight:600; }
  td { padding:10px 12px; border-bottom:1px solid #1E293B; font-size:13px; color:#94A3B8; }
  tr:hover td { background:#1E293B; color:#E2E8F0; }
  .form-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .loading { display:none; color:#38BDF8; font-size:13px; margin-top:8px; }
  .loading.show { display:block; }
  .icon { font-size:28px; margin-bottom:8px; }
  a.card-link { text-decoration:none; color:inherit; display:block; }
  .info-box { background:#1E3A5F; border:1px solid #0284C7; border-radius:8px; padding:12px 16px; font-size:12px; color:#BAE6FD; margin-bottom:16px; }
  .footer { text-align:center; color:#475569; font-size:11px; padding:24px; border-top:1px solid #1E293B; margin-top:32px; }
</style>
"""

def _layout(title: str, slug: str, body: str) -> str:
    nav_items = [
        ("/dashboard", "🏠 Dashboard", ""),
        ("/dashboard/forecast", "📈 Forecast", "forecast"),
        ("/dashboard/anomaly", "🔍 Anomaly", "anomaly"),
        ("/dashboard/capacity", "⚙️ Capacity", "capacity"),
    ]
    nav_html = ""
    for href, label, key in nav_items:
        active = "active" if slug == key or (slug == "" and key == "") else ""
        nav_html += f'<a href="{href}" class="{active}">{label}</a>'

    return f"""<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} — KIDECO AI Service</title>{COMMON_CSS}</head><body>
<nav class="navbar">
  <div class="logo">KIDECO AI Engine <span>v1.0.0</span></div>
  <div class="nav-links">{nav_html}</div>
</nav>
<div class="container">{body}</div>
<div class="footer">© 2026 PT Kideco Jaya Agung — Fuel Ratio Optimization AI Microservice</div>
<script>
const BASE = window.location.origin;
async function postAPI(endpoint, payload, resultId) {{
  const el = document.getElementById(resultId);
  const loading = document.getElementById(resultId + '_loading');
  if(loading) loading.classList.add('show');
  try {{
    const res = await fetch(BASE + endpoint, {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}});
    const data = await res.json();
    el.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
  }} catch(e) {{ el.innerHTML = '<pre style="color:#F87171;">Error: ' + e.message + '</pre>'; }}
  if(loading) loading.classList.remove('show');
}}
</script></body></html>"""


# ─── SLUG: /dashboard ──────────────────────────────────────────────────
@router.get("/", response_class=HTMLResponse)
async def dashboard_home():
    now = datetime.now().strftime("%d %B %Y, %H:%M WITA")
    body = f"""
    <h1>🖥️ Dashboard Microservice AI</h1>
    <p class="subtitle">Sistem Optimasi Fuel Ratio KIDECO — {now}</p>
    <div class="grid-3">
      <a href="/dashboard/forecast" class="card-link"><div class="card">
        <div class="icon">📈</div>
        <h2>Prediksi Fuel Ratio</h2>
        <p>Prediksi Fuel Ratio 1-Hari atau Horizon 7-Hari beruntun menggunakan XGBoost Regressor Model & Autoregressive Lags.</p>
        <br><span class="badge badge-blue">POST /api/v1/forecast-7days</span>
      </div></a>
      <a href="/dashboard/anomaly" class="card-link"><div class="card">
        <div class="icon">🔍</div>
        <h2>Deteksi Anomali Unit</h2>
        <p>Scan log konsumsi BBM unit alat berat menggunakan PyTorch Deep Autoencoder untuk mengisolasi spike anomali.</p>
        <br><span class="badge badge-yellow">POST /api/v1/anomaly-detect</span>
      </div></a>
      <a href="/dashboard/capacity" class="card-link"><div class="card">
        <div class="icon">⚙️</div>
        <h2>Kalkulasi Kapasitas 24 Jam</h2>
        <p>Kalkulasi alokasi kapasitas efektif per-unit, per-jam, dan per-shift dengan derating hujan non-linear.</p>
        <br><span class="badge badge-green">POST /api/v1/calculate-capacity</span>
      </div></a>
    </div>
    <div class="card">
      <h2>🔗 Quick Links</h2>
      <p>
        <a href="/health" style="color:#38BDF8;">Health Check</a> &nbsp;|&nbsp;
        <a href="/ready" style="color:#38BDF8;">Readiness Probe</a> &nbsp;|&nbsp;
        <a href="/docs" style="color:#38BDF8;">Swagger API Docs (OpenAPI)</a>
      </p>
    </div>
    """
    return _layout("Dashboard", "", body)


# ─── SLUG: /dashboard/forecast ─────────────────────────────────────────
@router.get("/forecast", response_class=HTMLResponse)
async def dashboard_forecast():
    body = """
    <h1>📈 Prediksi Fuel Ratio Harian & Horizon 7-Hari</h1>
    <p class="subtitle">XGBoost Regressor Model — TimeSeriesSplit 5-Fold CV & Autoregressive Horizon</p>
    <div class="info-box">
      <b>💡 Fitur Horizon 7-Hari Beruntun:</b><br/>
      • <b>Mode 7-Day Horizon:</b> Tekan tombol <b>📅 Horizon 7 Hari</b> untuk langsung memprediksi tren Fuel Ratio 7 hari ke depan dari tanggal awal yang dipilih.<br/>
      • <b>Mode Otomatis DB:</b> Jika parameter dikosongkan, sistem mengambil data cuaca & produksi dari Supabase Cloud.
    </div>
    <div class="card">
      <h2>Input Parameter Operasional</h2>
      <form onsubmit="event.preventDefault(); submitForecast();">
        <div class="form-row">
          <div><label>Tanggal Awal (YYYY-MM-DD)</label><input type="date" id="f_date" value="2026-08-05" onchange="autoFetchWeather()"></div>
          <div><label>Curah Hujan (mm) <small style="color:#64748B;">(Kosongkan untuk Otomatis DB)</small></label><input type="number" id="f_rain" placeholder="Otomatis dari DB" step="0.1" min="0"></div>
        </div>
        <div class="form-row">
          <div><label>Temperatur Maks (°C)</label><input type="number" id="f_temp" placeholder="Otomatis dari DB" step="0.1"></div>
          <div><label>Kecepatan Angin (km/h)</label><input type="number" id="f_wind" placeholder="Otomatis dari DB" step="0.1"></div>
        </div>
        <div class="form-row">
          <div><label>Jarak Angkut (m)</label><input type="number" id="f_haul" placeholder="Otomatis dari DB" step="10"></div>
          <div><label>Target Produksi (BCM)</label><input type="number" id="f_prod" placeholder="Otomatis dari DB" step="100"></div>
        </div>
        <div class="btn-group">
          <button type="submit">🚀 Prediksi 1 Hari</button>
          <button type="button" class="secondary" onclick="submitForecast7Days()">📅 Horizon Forecast 7 Hari</button>
        </div>
      </form>
      <div class="loading" id="forecast_result_loading">⏳ Memproses prediksi...</div>
      <div class="result-box" id="forecast_result"><pre style="color:#475569;">Hasil prediksi akan muncul di sini setelah menekan tombol.</pre></div>
    </div>
    <script>
    async function autoFetchWeather() {
      const dateVal = document.getElementById('f_date').value;
      if (!dateVal) return;
      try {
        const res = await fetch(BASE + '/api/v1/weather-by-date/' + dateVal);
        const data = await res.json();
        if (data.found_in_db) {
          document.getElementById('f_rain').value = data.curah_hujan_mm;
          document.getElementById('f_temp').value = data.temp_max_c;
          document.getElementById('f_wind').value = data.kecepatan_angin_kmh;
          document.getElementById('f_haul').value = data.haul_distance_m;
          document.getElementById('f_prod').value = data.daily_prod_bcm;
        }
      } catch(e) {}
    }
    function submitForecast() {
      const rainVal = document.getElementById('f_rain').value;
      const tempVal = document.getElementById('f_temp').value;
      const windVal = document.getElementById('f_wind').value;
      const haulVal = document.getElementById('f_haul').value;
      const prodVal = document.getElementById('f_prod').value;

      const payload = {
        date: document.getElementById('f_date').value,
        curah_hujan_mm: rainVal !== "" ? parseFloat(rainVal) : null,
        temp_max_c: tempVal !== "" ? parseFloat(tempVal) : null,
        kecepatan_angin_kmh: windVal !== "" ? parseFloat(windVal) : null,
        haul_distance_m: haulVal !== "" ? parseFloat(haulVal) : null,
        daily_prod_bcm: prodVal !== "" ? parseFloat(prodVal) : null
      };
      postAPI('/api/v1/forecast', payload, 'forecast_result');
    }

    function submitForecast7Days() {
      const startDate = document.getElementById('f_date').value;
      const payload = { start_date: startDate };
      postAPI('/api/v1/forecast-7days', payload, 'forecast_result');
    }
    // Initial fetch on page load
    autoFetchWeather();
    </script>
    """
    return _layout("Prediksi Fuel Ratio", "forecast", body)


# ─── SLUG: /dashboard/anomaly ──────────────────────────────────────────
@router.get("/anomaly", response_class=HTMLResponse)
async def dashboard_anomaly():
    body = """
    <h1>🔍 Deteksi Anomali Lonjakan BBM Unit</h1>
    <p class="subtitle">PyTorch Deep Autoencoder Neural Network — Adaptive MAD Threshold</p>
    <div class="card">
      <h2>Input Log Konsumsi BBM Unit</h2>
      <form onsubmit="event.preventDefault(); submitAnomaly();">
        <div class="form-row">
          <div><label>Tanggal</label><input type="date" id="a_date" value="2026-08-05"></div>
          <div><label>Nama Unit</label><input type="text" id="a_unit" value="HD785-7" placeholder="HD785-7"></div>
        </div>
        <div class="form-row">
          <div><label>Aktivitas</label>
            <select id="a_activity"><option>HAULING</option><option>LOADING</option><option>SUPPORT</option><option>DEWATERING</option></select>
          </div>
          <div><label>FC Aktual (L/hr)</label><input type="number" id="a_fc" value="75.0" step="0.1"></div>
        </div>
        <div class="form-row">
          <div><label>Total BBM Harian (L/day)</label><input type="number" id="a_fuel" value="1500.0" step="10"></div>
          <div><label>Unit Fuel Ratio (L/BCM)</label><input type="number" id="a_fr" value="0.26" step="0.01"></div>
        </div>
        <div><label>Curah Hujan (mm)</label><input type="number" id="a_rain" value="5.0" step="0.1" min="0"></div>
        <button type="submit">🔬 Scan Anomali</button>
      </form>
      <div class="loading" id="anomaly_result_loading">⏳ Memindai anomali...</div>
      <div class="result-box" id="anomaly_result"><pre style="color:#475569;">Hasil pemindaian anomali akan muncul di sini.</pre></div>
    </div>
    <script>
    function submitAnomaly() {
      const payload = {
        records: [{
          Date: document.getElementById('a_date').value,
          Unit: document.getElementById('a_unit').value,
          Activity: document.getElementById('a_activity').value,
          FC_Actual: parseFloat(document.getElementById('a_fc').value),
          Unit_Fuel_L_Day: parseFloat(document.getElementById('a_fuel').value),
          Unit_FR: parseFloat(document.getElementById('a_fr').value),
          Rain_mm: parseFloat(document.getElementById('a_rain').value)
        }]
      };
      postAPI('/api/v1/anomaly-detect', payload, 'anomaly_result');
    }
    </script>
    """
    return _layout("Deteksi Anomali", "anomaly", body)


# ─── SLUG: /dashboard/capacity ─────────────────────────────────────────
@router.get("/capacity", response_class=HTMLResponse)
async def dashboard_capacity():
    body = """
    <h1>⚙️ Kalkulasi Kapasitas Armada & Timeline 24 Jam</h1>
    <p class="subtitle">Combined Capacity Engine — Non-Linear Rain Derating & Per-Unit Per-Hour Parsing</p>
    <div class="card">
      <h2>Input Parameter Kapasitas</h2>
      <form onsubmit="event.preventDefault(); submitCapacity();">
        <div class="form-row">
          <div><label>Tanggal Operasional</label><input type="date" id="c_date" value="2026-08-05"></div>
          <div><label>Forecast Produksi (BCM)</label><input type="number" id="c_prod" value="40000" step="100" min="1000"></div>
        </div>
        <div class="form-row">
          <div><label>Curah Hujan (mm)</label><input type="number" id="c_rain" value="12.5" step="0.1" min="0"></div>
          <div><label>Spike Count HD785-7MUD</label><input type="number" id="c_spike" value="1" min="0" max="10"></div>
        </div>
        <button type="submit">📊 Hitung Kapasitas</button>
      </form>
      <div class="loading" id="capacity_result_loading">⏳ Menghitung kapasitas...</div>
      <div class="result-box" id="capacity_result"><pre style="color:#475569;">Hasil kalkulasi kapasitas & timeline 24 jam akan muncul di sini.</pre></div>
    </div>
    <script>
    function submitCapacity() {
      const spikeVal = parseInt(document.getElementById('c_spike').value) || 0;
      const payload = {
        date: document.getElementById('c_date').value,
        forecast_prod_bcm: parseFloat(document.getElementById('c_prod').value),
        curah_hujan_mm: parseFloat(document.getElementById('c_rain').value),
        nn_spike_count_by_unit: spikeVal > 0 ? {"HD785-7MUD": spikeVal} : null
      };
      postAPI('/api/v1/calculate-capacity', payload, 'capacity_result');
    }
    </script>
    """
    return _layout("Kalkulasi Kapasitas", "capacity", body)
