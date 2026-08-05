# Implementation Plan — KIDECO Fuel Ratio Integrated System

## Eksekusi Proyek Terdekomposisi: 6 Fase, 18 Sprint (Frontend: Vue 3 + Inertia.js)

> **Durasi Sprint:** 2 minggu (10 hari kerja)  
> **Total Estimasi:** ~36 minggu (9 bulan)  
> **Tech Stack Frontend:** Vue 3 (Composition API / `<script setup>`), Inertia.js Vue 3, Tailwind CSS, Vue ApexCharts (`vue3-apexcharts`), Lucide Vue Next

---

## Peta Fase & Sprint

```mermaid
gantt
    title Roadmap Eksekusi Proyek KIDECO Fuel Ratio (Vue 3 + Inertia)
    dateFormat YYYY-MM-DD
    axisFormat %b %Y

    section Fase 1: Foundation
    Sprint 1 - Setup & Infra           :s1, 2026-09-01, 14d
    Sprint 2 - Data Collection & Parser :s2, after s1, 14d
    Sprint 3 - Weather Engine           :s3, after s2, 14d

    section Fase 2: AI Engine
    Sprint 4 - Data Pipeline & EDA      :s4, after s3, 14d
    Sprint 5 - XGBoost Forecasting      :s5, after s4, 14d
    Sprint 6 - Autoencoder Anomaly      :s6, after s5, 14d
    Sprint 7 - Capacity Engine & API    :s7, after s6, 14d

    section Fase 3: Web App (Vue 3)
    Sprint 8 - Laravel Core & Auth Vue  :s8, after s7, 14d
    Sprint 9 - Dashboard Vue ApexCharts :s9, after s8, 14d
    Sprint 10 - Reporting & Export Vue  :s10, after s9, 14d

    section Fase 4: Chatbot (Vue 3)
    Sprint 11 - Chatbot Backend         :s11, after s10, 14d
    Sprint 12 - Disambiguasi & Vue Widget :s12, after s11, 14d

    section Fase 5: Hardening
    Sprint 13 - Security Hardening      :s13, after s12, 14d
    Sprint 14 - Testing Komprehensif    :s14, after s13, 14d
    Sprint 15 - Performance Tuning      :s15, after s14, 14d

    section Fase 6: Deploy & MLOps
    Sprint 16 - Deployment Pipeline     :s16, after s15, 14d
    Sprint 17 - MLOps & Monitoring      :s17, after s16, 14d
    Sprint 18 - UAT & Handover          :s18, after s17, 14d
```

---

## Ringkasan Pemetaan Solusi Celah → Sprint

| Celah | Severity | Sprint Penanganan | Sub-Proyek |
|:------|:---------|:------------------|:-----------|
| #1 Data sintetis → riil | 🔴 Kritis | Sprint 2, 4 | `laravel-web-portal`, `python-ai-service` |
| #2 SQL Injection chatbot | 🔴 Kritis | Sprint 11, 13 | `laravel-web-portal`, `infra-mlops-devops` |
| #3 Retraining & model drift | 🔴 Kritis | Sprint 17 | `python-ai-service`, `infra-mlops-devops` |
| #4 Autoencoder data terpolusi | 🟠 Signifikan | Sprint 6 | `python-ai-service` |
| #5 Threshold anomali statis | 🟠 Signifikan | Sprint 6 | `python-ai-service` |
| #6 XGBoost split tidak realistis | 🟠 Signifikan | Sprint 5 | `python-ai-service` |
| #7 Error handling & fallback | 🟠 Signifikan | Sprint 3, 7, 12 | `laravel-web-portal`, `python-ai-service` |
| #8 Disambiguasi sederhana | 🟠 Signifikan | Sprint 12 | `laravel-web-portal`, `frontend-vue` |
| #9 Formula derating inkonsisten | 🟡 Minor | Sprint 3 | `laravel-web-portal` |
| #10 Excel parser fragile | 🟡 Minor | Sprint 2 | `laravel-web-portal` |
| #11 Tidak ada testing | 🟡 Minor | Sprint 14 | Semua Sub-Proyek |
| #12 RBAC tidak didefinisikan | 🟡 Minor | Sprint 8 | `laravel-web-portal`, `frontend-vue` |
| #13 Fitur angin hilang | 🟡 Minor | Sprint 4 | `python-ai-service` |

---

> [!NOTE]
> Seluruh panduan per sub-proyek dapat diakses di file berikut:
> - `laravel-web-portal/sprints.md`
> - `python-ai-service/sprints.md`
> - `frontend-vue/sprints.md`
> - `infra-mlops-devops/sprints.md`
