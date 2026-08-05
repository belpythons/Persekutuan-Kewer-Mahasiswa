# Laravel Web Portal — Dekomposisi Sprint 1 hingga Sprint 18

Dokumen ini berisi panduan implementasi teknis mendetail per sprint untuk sub-proyek **`laravel-web-portal/`** (Laravel 11.x Backend & DB Core) berdasarkan acuan `implementation_plan.md` dan `prd.md`.

---

## 📅 Matriks Ringkasan Sprint `laravel-web-portal/`

| Sprint | Judul / Fokus Utama | Output / Deliverable | Target Celah |
|:-------|:-------------------|:---------------------|:-------------|
| **Sprint 1** | Project Setup & DB Migrations | Structure, Migrations, Core Models | Baseline Setup |
| **Sprint 2** | Robust Baseline Excel Parser | Import Classes + Validation Layer | #10 (Parser Index) |
| **Sprint 3** | Weather Scraping Engine | Open-Meteo Service + Fallback + Derating | #7 (Fallback), #9 (Derating) |
| **Sprint 4** | Database Time-Series Aggregator | TimeSeriesBuilder Service | Data Ingestion |
| **Sprint 5-7**| AI Microservice Client Integration | `AiEngineService` Guzzle Client + Fallback | Microservice Bridge |
| **Sprint 8** | Auth, RBAC & Audit Trail | Spatie Role & Permission + Middleware | #12 (RBAC Detail) |
| **Sprint 9** | Dashboard Data APIs | Dashboard API Endpoints | Dashboard Backend |
| **Sprint 10**| Reporting & Export Controllers | DomPDF & Excel Export Services | Report Service |
| **Sprint 11**| Chatbot Core & Security Whitelist | `ChatbotService` + `QueryWhitelistGuard` | #2 (SQL Injection) |
| **Sprint 12**| Enhanced Disambiguation & SSE Stream | `ConfidenceScorer` + SSE Response Stream | #8 (Disambiguasi) |
| **Sprint 13**| Security Hardening & CORS/CSP | CORS, CSP Headers, Rate Limiting | Security Check |
| **Sprint 14**| PHPUnit / Pest Test Suite | Unit & Integration Tests (Coverage ≥ 80%) | #11 (Testing) |
| **Sprint 15**| Redis Query Caching & Tuning | Redis Cache Layer & Optimization | Performance |
| **Sprint 16-18**| Production Readiness & Handover | Staging/Prod Deployment Support & UAT | Go-Live |

---

## 🛠️ Detil Instruksi Pengerjaan Per Sprint

### 📌 Sprint 1: Project Setup, Config & Database Migrations
**Folder Target:** `laravel-web-portal/`
- **Langkah Pengerjaan:**
  1. Jalankan `composer create-project laravel/laravel .` pada folder `laravel-web-portal/`.
  2. Install dependensi composer:
     `composer require maatwebsite/excel spatie/laravel-permission openai-php/laravel inertiajs/inertia-laravel barryvdh/laravel-dompdf`
  3. Konfigurasi database PostgreSQL pada `.env`:
     ```env
     DB_CONNECTION=pgsql
     DB_HOST=postgres
     DB_PORT=5432
     DB_DATABASE=kideco_fuel_ratio
     DB_USERNAME=kideco_user
     DB_PASSWORD=kideco_secret
     ```
  4. Buat file migration secara berurutan:
     - `database/migrations/2026_09_01_000001_create_equipment_catalogs_table.php`
     - `database/migrations/2026_09_01_000002_create_loading_units_baseline_table.php`
     - `database/migrations/2026_09_01_000003_create_hauling_units_baseline_table.php`
     - `database/migrations/2026_09_01_000004_create_supporting_units_baseline_table.php`
     - `database/migrations/2026_09_01_000005_create_dewatering_units_baseline_table.php`
     - `database/migrations/2026_09_01_000006_create_weather_daily_logs_table.php`
     - `database/migrations/2026_09_01_000007_create_daily_forecast_logs_table.php`
     - `database/migrations/2026_09_01_000008_create_unit_anomaly_spikes_table.php`
     - `database/migrations/2026_09_01_000009_create_capacity_allocations_table.php`
  5. Jalankan `php artisan migrate`.

---

### 📌 Sprint 2: Robust Baseline Excel Import Engine (Solusi Celah #10)
- **Aturan Bebas Halusinasi:** DILARANG keras menggunakan index kolom numerik ($row[0], $row[2]) saat mempassing Excel. WAJIB menggunakan `WithHeadingRow` berbasis nama kolom eksplisit.
- **Langkah Pengerjaan:**
  1. Buat class import pada `app/Imports/`:
     - `LoadingUnitsImport.php`
     - `HaulingUnitsImport.php`
     - `SupportingUnitsImport.php`
     - `DewateringUnitsImport.php`
  2. Implementasikan antarmuka `ToModel`, `WithHeadingRow`, `WithValidation`, `SkipsOnFailure`.
  3. Contoh implementasi `LoadingUnitsImport.php`:
     ```php
     namespace App\Imports;
     use App\Models\LoadingUnitBaseline;
     use Maatwebsite\Excel\Concerns\ToModel;
     use Maatwebsite\Excel\Concerns\WithHeadingRow;
     use Maatwebsite\Excel\Concerns\WithValidation;

     class LoadingUnitsImport implements ToModel, WithHeadingRow, WithValidation {
         public function model(array $row) {
             return new LoadingUnitBaseline([
                 'unit_code' => $row['unit_code'],
                 'activity' => 'Loading',
                 'fc_lhr' => $row['fc_l_hr'],
                 'prod_bcmhr' => $row['prod_bcm_hr'],
             ]);
         }
         public function rules(): array {
             return [
                 'unit_code' => 'required|string',
                 'fc_l_hr' => 'required|numeric|min:0',
                 'prod_bcm_hr' => 'required|numeric|min:0',
             ];
         }
     }
     ```
  4. Buat Artisan command `app/Console/Commands/ImportBaselineCommand.php` untuk eksekusi CLI.

---

### 📌 Sprint 3: Weather Scraping, Fallback & Non-Linear Derating (Solusi Celah #7 & #9)
- **Langkah Pengerjaan:**
  1. Buat `App\Services\WeatherService` menggunakan Laravel HTTP Client untuk konsumsi Open-Meteo API.
  2. Buat `App\Services\SyntheticWeatherFallback` jika HTTP client menemui koneksi gagal/timeout.
  3. Implementasikan `App\Services\DeratingCalculator` dengan logika non-linear:
     ```php
     namespace App\Services;

     class DeratingCalculator {
         public function calculate(float $rainfallMm): float {
             if ($rainfallMm <= 5.0) return 1.0;
             if ($rainfallMm <= 20.0) return 1.0 - 0.01 * pow($rainfallMm - 5.0, 1.3);
             if ($rainfallMm <= 50.0) return max(0.65, 0.82 - 0.005 * pow($rainfallMm - 20.0, 1.1));
             return 0.60;
         }
     }
     ```
  4. Buat Job `App\Jobs\FetchDailyWeatherJob.php` untuk dijalankan oleh Artisan Scheduler setiap jam 06:00.

---

### 📌 Sprint 8: RBAC & Security Audit Trail (Solusi Celah #12)
- **Langkah Pengerjaan:**
  1. Buat seeder `database/seeders/RoleAndPermissionSeeder.php`.
  2. Definisikan 4 Role utama: `admin`, `manager`, `dispatcher`, `viewer`.
  3. Daftarkan permission eksplisit:
     - `import-data`, `view-dashboard`, `export-reports`, `use-chatbot`, `configure-thresholds`.
  4. Pasang Middleware `can:permission-name` pada setiap route API di `routes/api.php` dan `routes/web.php`.

---

### 📌 Sprint 11: Direct Relational DB Chatbot Engine & Whitelist Guard (Solusi Celah #2)
- **ATURAN KEAMANAN MUTLAK:** DILARANG menggunakan `DB::raw()` atau `PDO::query()` pada chatbot.
- **Langkah Pengerjaan:**
  1. Buat Whitelist Guard `App\Security\QueryWhitelistGuard.php`:
     ```php
     namespace App\Security;

     class QueryWhitelistGuard {
         private const ALLOWED_TABLES = [
             'equipment_catalogs', 'daily_forecast_logs',
             'unit_anomaly_spikes', 'capacity_allocations', 'weather_daily_logs'
         ];
         public static function validateTable(string $tableName): void {
             if (!in_array($tableName, self::ALLOWED_TABLES)) {
                 throw new \InvalidArgumentException("Akses ke tabel '{$tableName}' ditolak demi keamanan.");
             }
         }
     }
     ```
  2. Konfigurasi koneksi database read-only `config/database.php` (`chatbot_readonly`).
  3. Buat Service `App\Services\ChatbotService.php` yang memanggil OpenAI GPT-4o dengan Structured Function Calling.

---

### 📌 Sprint 12: Enhanced Disambiguation & SSE Stream (Solusi Celah #8)
- **Langkah Pengerjaan:**
  1. Buat `App\Services\ConfidenceScorer.php` untuk menghitung skor kelengkapan parameter `S_confidence`:
     - Skor > 0.70: Langsung jalankan query database.
     - Skor < 0.70: Trigger pilihan klarifikasi interaktif.
  2. Buat `App\Services\FuzzyUnitMatcher.php` (penanganan typo nama alat seperti "HD785" -> "HD785-7").
  3. Buat `ChatbotController@streamResponse` yang menggunakan `Symfony\Component\HttpFoundation\StreamedResponse` untuk token streaming SSE ke frontend React.

---

### 📌 Sprint 14: PHPUnit / Pest Test Suite (Solusi Celah #11)
- **Langkah Pengerjaan:**
  1. Buat Test File:
     - `tests/Unit/DeratingCalculatorTest.php`
     - `tests/Unit/ExcelImportTest.php`
     - `tests/Feature/ChatbotSecurityTest.php` (Uji coba SQL injection injection payload)
     - `tests/Feature/DashboardApiTest.php`
  2. Pastikan `php artisan test` memberikan hasil 100% PASS dan coverage ≥ 80%.
