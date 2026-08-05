# [TASK-03] Nginx Reverse Proxy, SSL Termination & CORS/CSP Hardening

## 1. Metadata
- **Sprint**: Infra-MLOps-DevOps - Sprint 13
- **Kategori**: Security / Infrastructure
- **Status**: Ready for Implementation
- **Estimasi Effort**: 5 Story Points (~10 Jam)

## 2. Deskripsi Task
Menyusun konfigurasi server web Nginx sebagai Reverse Proxy dan Gatekeeper keamanan tingkat lanjut (*security hardening*). Task ini mencakup terminasi enkripsi HTTPS/TLS SSL, pengkonfigurasian header *Cross-Origin Resource Sharing* (CORS) terbatas pada domain resmi aplikasi, pembatasan ukuran request body, serta penerapan header *Content Security Policy* (CSP), `X-Frame-Options`, dan `X-Content-Type-Options` guna melindungi Laravel Web Portal dan Python AI Engine dari serangan XSS, Clickjacking, dan Data Interception.

## 3. Objective & Key Results (OKR)
- Objective: Menjamin seluruh lalu lintas HTTP ter-enkripsi via HTTPS dan terlindungi oleh header keamanan standar industri.
- Key Results:
  - [ ] Nginx Reverse Proxy mengalihkan (*redirect*) seluruh traffic HTTP (port 80) ke HTTPS (port 443).
  - [ ] Header CORS dikonfigurasi ketat hanya mengizinkan domain frontend terverifikasi.
  - [ ] Penilaian keamanan header Nginx meraih Grade A/A+ pada pengujian SSL/Security Headers evaluation.

## 4. Technical Deliverables & Specifications
- **Target Files**:
  - `infra-mlops-devops/nginx/conf.d/app.conf`
  - `infra-mlops-devops/nginx/snippets/security.conf`
- **Konfigurasi Nginx Server Block (`app.conf`)**:
  ```nginx
  server {
      listen 80;
      server_name kideco-fuel.com *.kideco-fuel.com;
      return 301 https://$host$request_uri;
  }

  server {
      listen 443 ssl http2;
      server_name kideco-fuel.com;

      ssl_certificate /etc/nginx/ssl/fullchain.pem;
      ssl_certificate_key /etc/nginx/ssl/privkey.pem;
      ssl_protocols TLSv1.2 TLSv1.3;
      ssl_ciphers HIGH:!aNULL:!MD5;

      include /etc/nginx/snippets/security.conf;

      # Proxy pass ke Laravel Web Portal
      location / {
          proxy_pass http://laravel-portal:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto https;
      }

      # Proxy pass ke Python AI Service REST API
      location /api/v1/ {
          proxy_pass http://python-ai:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto https;
      }
  }
  ```
- **Security Headers Snippet (`security.conf`)**:
  ```nginx
  add_header X-Frame-Options "SAMEORIGIN" always;
  add_header X-XSS-Protection "1; mode=block" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header Referrer-Policy "no-referrer-when-downgrade" always;
  add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
  add_header Access-Control-Allow-Origin "https://kideco-fuel.com" always;
  add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE" always;
  ```

## 5. Acceptance Criteria (Definition of Done)
- [ ] Nginx Reverse Proxy berhasil melakukan *routing* trafik secara transparan ke Laravel dan Python AI Engine.
- [ ] Request HTTP otomatis di-redirect ke HTTPS dengan TLS 1.2/1.3 valid.
- [ ] Header keamanan `X-Frame-Options`, `X-Content-Type-Options`, dan `Access-Control-Allow-Origin` muncul pada respons HTTP.
