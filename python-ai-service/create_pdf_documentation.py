import os
import sys
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas kustom untuk menambahkan Header & Footer profesional dengan nomor halaman otomatis (Page X of Y).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1E293B")) # Dark Slate
        
        # Header (Only on page 2 and later)
        if self._pageNumber > 1:
            self.drawString(36, 815, "PT KIDECO JAYA AGUNG — FUEL RATIO AI MICROSERVICE DOCUMENTATION")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 808, 559, 808)
            
        # Footer (All pages)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        page_str = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(559, 25, page_str)
        self.drawString(36, 25, "CONFIDENTIAL — DOKUMEN SISTEM ALUR & FORMULASI PERHITUNGAN AI")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 35, 559, 35)
        
        self.restoreState()

def build_pdf_documentation():
    pdf_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DOKUMENTASI_ALUR_DAN_PERHITUNGAN_AI_SERVICE.pdf")
    
    # Page setup: A4 with 0.5 inch margins (36pt)
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=45,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    COLOR_PRIMARY = colors.HexColor("#0F172A")    # Deep Navy
    COLOR_SECONDARY = colors.HexColor("#0284C7")  # Oceanic Blue
    COLOR_DARK = colors.HexColor("#334155")       # Charcoal
    COLOR_ACCENT = colors.HexColor("#0D9488")     # Teal
    COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")   # Light Slate
    
    # Modify Styles
    styles['Normal'].textColor = COLOR_DARK
    styles['Normal'].fontSize = 9.5
    styles['Normal'].leading = 13.5
    styles['Normal'].fontName = 'Helvetica'

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=COLOR_PRIMARY,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=COLOR_SECONDARY,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=COLOR_SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0F172A")
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11.5
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    story = []
    
    # -------------------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------------------
    story.append(Paragraph("PANDUAN LENGKAP ALUR SISTEM & FORMULASI PERHITUNGAN", title_style))
    story.append(Paragraph("<b>Microservice Python AI Engine — KIDECO Fuel Ratio Optimization System</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_SECONDARY, spaceAfter=15))
    
    # Meta Info Card Table
    meta_data = [
        [
            Paragraph("<b>Pengembang System:</b> AI Engineering DeepMind Team", table_cell_style),
            Paragraph("<b>Target Sub-Proyek:</b> <code>python-ai-service/</code>", table_cell_style)
        ],
        [
            Paragraph(f"<b>Tanggal Rilis:</b> {datetime.datetime.now().strftime('%d %B %Y')}", table_cell_style),
            Paragraph("<b>Versi Core AI:</b> v1.0.0 (FastAPI + XGBoost + PyTorch)", table_cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[260, 263])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # SECTION 1: RINGKASAN EKSEKUTIF & ARSITEKTUR
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Ringkasan Eksekutif & Arsitektur Microservice", h1_style))
    story.append(Paragraph(
        "Microservice Python AI Engine dirancang khusus untuk mengolah data operasional penambangan batu bara PT Kideco Jaya Agung. "
        "Service ini menyediakan 3 kapabilitas utama berbasis kecerdasan buatan: "
        "<b>(1) Prediksi Fuel Ratio Harian (XGBoost Regressor)</b>, "
        "<b>(2) Deteksi Anomali Lonjakan BBM Unit Alat Berat (PyTorch Autoencoder Neural Network)</b>, dan "
        "<b>(3) Penentuan Alokasi Kapasitas Efektif & Solar Kombinasi (Combined Capacity Engine dengan Rain Derating Non-Linear)</b>.",
        styles['Normal']
    ))
    story.append(Spacer(1, 8))

    # Architecture Overview Table
    arch_data = [
        [Paragraph("<b>Komponen System</b>", table_header_style), Paragraph("<b>Teknologi / Algoritma</b>", table_header_style), Paragraph("<b>Peran & Fungsi Utama</b>", table_header_style)],
        [Paragraph("API Framework", table_cell_style), Paragraph("FastAPI + Uvicorn (Python 3.10)", table_cell_style), Paragraph("High-performance REST API Server dengan async lifespan model warm-up.", table_cell_style)],
        [Paragraph("Forecasting Engine", table_cell_style), Paragraph("XGBoost Regressor + TimeSeriesSplit CV", table_cell_style), Paragraph("Prediksi Fuel Ratio (L/BCM) berbasis 13 fitur operasional & cuaca.", table_cell_style)],
        [Paragraph("Anomaly Detector", table_cell_style), Paragraph("PyTorch Deep Autoencoder (3→16→8→3)", table_cell_style), Paragraph("Melatih data normal (nn_anomaly=0) untuk mengisolasi unit spike anomaly.", table_cell_style)],
        [Paragraph("Capacity Engine", table_cell_style), Paragraph("Non-Linear Rain Derating Calculator", table_cell_style), Paragraph("Kalkulasi utilisasi, unit aktif, & BBM per-unit per-jam untuk 4 aktivitas.", table_cell_style)],
        [Paragraph("Database Layer", table_cell_style), Paragraph("SQLAlchemy ORM + PostgreSQL / SQLite", table_cell_style), Paragraph("3NF Relational database dengan composite B-Tree indexes.", table_cell_style)]
    ]
    t_arch = Table(arch_data, colWidths=[110, 170, 243])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # SECTION 2: ALUR KERJA UTAMA (SYSTEM WORKFLOW)
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Diagram Alur Kerja Utama Microservice (System Workflow)", h1_style))
    story.append(Paragraph(
        "Alur pemrosesan data di dalam microservice berlangsung secara terstruktur dari tahap penerimaan input hingga penyimpanan database:",
        styles['Normal']
    ))
    story.append(Spacer(1, 6))

    flow_box_content = [
        [Paragraph("<b>[STEP 1: INGESTION]</b> Input parameter dari Laravel Portal (Tanggal, Curah Hujan, Temp, Wind, Haul Distance, Target Prod).", table_cell_style)],
        [Paragraph("⬇️", table_cell_style)],
        [Paragraph("<b>[STEP 2: QUALITY CHECK & FEATURE ENGINEERING]</b> Imputasi missing values, outlier clipping, pembentukan 13 fitur ML (Rain Lags, FR Lags, Rolling 7d Avg).", table_cell_style)],
        [Paragraph("⬇️", table_cell_style)],
        [Paragraph("<b>[STEP 3: XGBOOST INFERENCE]</b> Model XGBoost menghitung prediksi Fuel Ratio Harian (L/BCM) & mengevaluasi status (NORMAL / WARNING / CRITICAL).", table_cell_style)],
        [Paragraph("⬇️", table_cell_style)],
        [Paragraph("<b>[STEP 4: PYTORCH AUTOENCODER SCAN]</b> Scan log unit harian. Autoencoder menghitung MSE reconstruction error & menguji terhadap Adaptive MAD Threshold per aktivitas.", table_cell_style)],
        [Paragraph("⬇️", table_cell_style)],
        [Paragraph("<b>[STEP 5: CAPACITY & RAIN DERATING ENGINE]</b> Menghitung derating hujan non-linear, utilisasi %, unit operasional, serta alokasi BBM kombi per-unit per-jam.", table_cell_style)],
        [Paragraph("⬇️", table_cell_style)],
        [Paragraph("<b>[STEP 6: DATABASE SYNC & REST RESPONSE]</b> Penyelarasan log ke tabel DB <code>daily_forecast_logs</code>, <code>unit_anomaly_spikes</code>, & <code>capacity_unit_allocations</code>.", table_cell_style)]
    ]
    t_flow = Table(flow_box_content, colWidths=[523])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_SECONDARY),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_flow)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # SECTION 3: FORMULASI PERHITUNGAN DETAIL & RUMUS MATEMATIKA
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Formulasi Perhitungan Detail & Rumus Matematika", h1_style))
    
    # 3.1 13 Fitur Machine Learning
    story.append(Paragraph("3.1. Formulasi 13 Fitur Machine Learning (Feature Engineering)", h2_style))
    story.append(Paragraph(
        "Model XGBoost Regressor menggunakan 13 fitur yang diturunkan dari data historis operasional dan meteorologi:",
        styles['Normal']
    ))
    story.append(Spacer(1, 4))
    
    feat_data = [
        [Paragraph("<b>Nama Fitur</b>", table_header_style), Paragraph("<b>Simbol Matematika</b>", table_header_style), Paragraph("<b>Rumus / Penjelasan Formulasi</b>", table_header_style)],
        [Paragraph("Curah_Hujan_mm", table_cell_style), Paragraph("<i>R(t)</i>", table_cell_style), Paragraph("Curah hujan harian aktual / prakiraan (mm)", table_cell_style)],
        [Paragraph("Temp_Max_C", table_cell_style), Paragraph("<i>T<sub>max</sub>(t)</i>", table_cell_style), Paragraph("Temperatur udara maksimum harian (°C)", table_cell_style)],
        [Paragraph("Kecepatan_Angin_kmh", table_cell_style), Paragraph("<i>W(t)</i>", table_cell_style), Paragraph("Kecepatan angin harian (km/h) (Solusi Celah #13)", table_cell_style)],
        [Paragraph("Haul_Distance_m", table_cell_style), Paragraph("<i>H(t)</i>", table_cell_style), Paragraph("Jarak angkut rata-rata dari pit ke ROM/dump (meter)", table_cell_style)],
        [Paragraph("Daily_Prod_BCM", table_cell_style), Paragraph("<i>P(t)</i>", table_cell_style), Paragraph("Total volume produksi overburden/batu bara (BCM)", table_cell_style)],
        [Paragraph("DayOfWeek", table_cell_style), Paragraph("<i>Dow(t)</i>", table_cell_style), Paragraph("Indeks hari dalam seminggu (0 = Senin, 6 = Minggu)", table_cell_style)],
        [Paragraph("Month", table_cell_style), Paragraph("<i>M(t)</i>", table_cell_style), Paragraph("Indeks bulan (1 s/d 12)", table_cell_style)],
        [Paragraph("IsWeekend", table_cell_style), Paragraph("<i>Wknd(t)</i>", table_cell_style), Paragraph("1 jika <i>Dow(t) ∈ {5, 6}</i>, 0 untuk hari kerja biasa", table_cell_style)],
        [Paragraph("Rain_Lag1", table_cell_style), Paragraph("<i>R(t-1)</i>", table_cell_style), Paragraph("Curah hujan 1 hari sebelumnya (mm)", table_cell_style)],
        [Paragraph("Rain_Lag2", table_cell_style), Paragraph("<i>R(t-2)</i>", table_cell_style), Paragraph("Curah hujan 2 hari sebelumnya (mm)", table_cell_style)],
        [Paragraph("FR_Lag1", table_cell_style), Paragraph("<i>FR(t-1)</i>", table_cell_style), Paragraph("Fuel Ratio realisasi 1 hari sebelumnya (L/BCM)", table_cell_style)],
        [Paragraph("FR_Lag2", table_cell_style), Paragraph("<i>FR(t-2)</i>", table_cell_style), Paragraph("Fuel Ratio realisasi 2 hari sebelumnya (L/BCM)", table_cell_style)],
        [Paragraph("RollingAvg_FR_7d", table_cell_style), Paragraph("<i>FR̄<sub>7d</sub>(t)</i>", table_cell_style), Paragraph("Rata-rata bergerak Fuel Ratio 7 hari: <b>(1/7) ∑<sub>i=1..7</sub> FR(t-i)</b>", table_cell_style)]
    ]
    t_feat = Table(feat_data, colWidths=[120, 95, 308])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 10))

    # 3.2 XGBoost & Dynamic Status Threshold
    story.append(Paragraph("3.2. Model XGBoost & Evaluasi Status Threshold Dynamic", h2_style))
    story.append(Paragraph(
        "Model XGBoost dilatih menggunakan <i>TimeSeriesSplit (5-Fold Cross Validation)</i> untuk mencegah data leakage. "
        "Hasil prediksi <i>FR<sub>Forecast</sub></i> dibandingkan dengan threshold anggaran baseline:",
        styles['Normal']
    ))
    story.append(Spacer(1, 4))
    
    formula_xgb = [
        [Paragraph("<b>Budget Baseline FR:</b> <code>FR_Budget = 1.018 L/BCM</code>", table_cell_style)],
        [Paragraph("<b>Warning Threshold (+8%):</b> <code>FR_Warning = 1.018 * 1.08 = 1.0994 L/BCM</code>", table_cell_style)],
        [Paragraph("<b>Critical Threshold (+18%):</b> <code>FR_Critical = 1.018 * 1.18 = 1.2012 L/BCM</code>", table_cell_style)],
        [Paragraph("<b>Aturan Evaluasi Status:</b><br/>"
                   "• Jika <i>FR<sub>Forecast</sub> ≥ 1.2012</i> ➔ <b>CRITICAL</b><br/>"
                   "• Jika <i>1.0994 ≤ FR<sub>Forecast</sub> < 1.2012</i> ➔ <b>WARNING</b><br/>"
                   "• Jika <i>FR<sub>Forecast</sub> < 1.0994</i> ➔ <b>NORMAL</b>", table_cell_style)]
    ]
    t_fxgb = Table(formula_xgb, colWidths=[523])
    t_fxgb.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_fxgb)
    story.append(Spacer(1, 10))

    # Page Break for clean layout
    story.append(PageBreak())

    # 3.3 PyTorch Autoencoder & Adaptive MAD Threshold
    story.append(Paragraph("3.3. PyTorch Deep Autoencoder & Adaptive MAD Threshold Anomaly Detector", h1_style))
    story.append(Paragraph(
        "Untuk mendeteksi lonjakan konsumsi BBM (*spike anomaly*) yang tidak wajar pada unit alat berat, digunakan jaringan saraf <b>PyTorch Deep Autoencoder</b>.",
        styles['Normal']
    ))
    story.append(Spacer(1, 4))

    ae_rules = [
        [Paragraph("<b>1. Pelatihan Hanya pada Data Normal (Solusi Celah #4):</b> Autoencoder di-train HANYA menggunakan record dengan <code>nn_anomaly_spike == 0</code>. Dengan demikian, model hanya mempelajari pola konsumsi BBM efisien.", table_cell_style)],
        [Paragraph("<b>2. Arsitektur Jaringan:</b> Encoder: <code>Input(3) ➔ 16 (ReLU) ➔ 8 (ReLU) ➔ Latent(3)</code>. Decoder: <code>Latent(3) ➔ 8 (ReLU) ➔ 16 (ReLU) ➔ Input(3)</code>.", table_cell_style)],
        [Paragraph("<b>3. Fitur Rasio Relatif Unit:</b> Input tensor berupa <code>[FC_Ratio, Unit_FR_Ratio, Unit_Fuel_Ratio]</code> di mana <i>FC_Ratio = FC_Actual / FC_Base</i>. Hal ini mengeliminasi bias perbedaan ukuran alat berat.", table_cell_style)],
        [Paragraph("<b>4. Mean Squared Reconstruction Error (MSE):</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>e<sub>i</sub> = (1 / 3) ∑<sub>j=1..3</sub> (x<sub>i,j</sub> - x̂<sub>i,j</sub>)<sup>2</sup></i>", table_cell_style)],
        [Paragraph("<b>5. Adaptive Threshold berbasis Median Absolute Deviation (MAD) (Solusi Celah #5):</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>MAD = Median( | e<sub>i</sub> - Median(e) | )</i><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>Threshold<sub>Activity</sub> = max( Percentile<sub>99.5</sub>(e<sub>Normal</sub>), Median(e<sub>Normal</sub>) + 5.0 × 1.4826 × MAD )</i>", table_cell_style)],
        [Paragraph("<b>6. Isolasi Spike Anomali:</b> Jika <i>e<sub>i</sub> > Threshold<sub>Activity</sub></i>, record ditandai <b>Is_Spike = 1</b> dan memicu buffer Solar sebesar +15%.", table_cell_style)]
    ]
    t_aerules = Table(ae_rules, colWidths=[523])
    t_aerules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_aerules)
    story.append(Spacer(1, 12))

    # 3.4 Capacity Engine & Non-Linear Rain Derating
    story.append(Paragraph("3.4. Combined Capacity Engine & Formulasi Derating Hujan Non-Linear", h1_style))
    story.append(Paragraph(
        "Kapasitas produksi tambang mengalami penurunan non-linear saat terjadi hujan akibat slip jalan tambang dan visibilitas berkurang (Solusi Celah #9):",
        styles['Normal']
    ))
    story.append(Spacer(1, 4))

    derating_formula_box = [
        [Paragraph("<b>Formulasi Derating Hujan Non-Linear D(R) di mana R = Curah Hujan (mm):</b><br/>"
                   "• Jika <i>R ≤ 5.0 mm</i> ➔ <b>D(R) = 1.00</b> (Tanpa Derating)<br/>"
                   "• Jika <i>5.0 < R ≤ 20.0 mm</i> ➔ <b>D(R) = 1.00 - 0.01 × (R - 5.0)<sup>1.3</sup></b> (Penurunan Moderat)<br/>"
                   "• Jika <i>20.0 < R ≤ 50.0 mm</i> ➔ <b>D(R) = max(0.65, 0.82 - 0.005 × (R - 20.0)<sup>1.1</sup>)</b> (Penurunan Signifikan)<br/>"
                   "• Jika <i>R > 50.0 mm</i> ➔ <b>D(R) = 0.60</b> (Kapasitas Minimum Operasional)", table_cell_style)]
    ]
    t_derate = Table(derating_formula_box, colWidths=[523])
    t_derate.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, COLOR_SECONDARY),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_derate)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Formulasi Perhitungan Alokasi Kapasitas Per-Unit & Per-Jam:</b>", h2_style))
    
    cap_calc_box = [
        [Paragraph("<b>1. Kapasitas Terpasang Total:</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>Cap<sub>Installed</sub> = ∑ ( Qty<sub>u</sub> × ProdBCMhr<sub>u</sub> ) &nbsp;&nbsp;(BCM/hr)</i>", table_cell_style)],
        [Paragraph("<b>2. Kapasitas Efektif Harian Total:</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>Cap<sub>Effective</sub> = Cap<sub>Installed</sub> × 20.0 jam × D(R) &nbsp;&nbsp;(BCM/day)</i>", table_cell_style)],
        [Paragraph("<b>3. Persentase Utilisasi Armada (%):</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>Utilisation % = min( 100.0, max( 10.0, ( ForecastProdBCM / Cap<sub>Effective</sub> ) × 100% ) )</i>", table_cell_style)],
        [Paragraph("<b>4. Jumlah Unit Operasional per Tipe Alat (Operating Units):</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>OperatingUnits<sub>u</sub> = min( Qty<sub>u</sub>, ⌈ ( Utilisation % / 100 ) × Qty<sub>u</sub> ⌉ )</i>", table_cell_style)],
        [Paragraph("<b>5. Produktivitas Per Jam & Per Hari per Tipe Alat (BCM):</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>ProdBCMhrTotal<sub>u</sub> = OperatingUnits<sub>u</sub> × ProdBCMhr<sub>u</sub> &nbsp;&nbsp;(BCM/hr)</i><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>ProdBCMdayTotal<sub>u</sub> = ProdBCMhrTotal<sub>u</sub> × 20.0 jam × D(R) &nbsp;&nbsp;(BCM/day)</i>", table_cell_style)],
        [Paragraph("<b>6. Konsumsi BBM Solar Per Jam & Per Hari per Tipe Alat (Liter):</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>FuelLhrTotal<sub>u</sub> = OperatingUnits<sub>u</sub> × FCLhr<sub>u</sub> &nbsp;&nbsp;(Liter/hr)</i><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>BaseFuelDay<sub>u</sub> = FuelLhrTotal<sub>u</sub> × 20.0 jam × ( Utilisation % / 100 ) &nbsp;&nbsp;(Liter/day)</i><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>CombinedFuelDay<sub>u</sub> = BaseFuelDay<sub>u</sub> × ( 1.0 + 0.15 × SpikeCount<sub>u</sub> ) &nbsp;&nbsp;(Liter/day)</i>", table_cell_style)],
        [Paragraph("<b>7. Individual Unit Fuel Ratio (L/BCM):</b><br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<i>UnitFR<sub>u</sub> = CombinedFuelDay<sub>u</sub> / max( 1.0, ProdBCMdayTotal<sub>u</sub> ) &nbsp;&nbsp;(L/BCM)</i>", table_cell_style)]
    ]
    t_capcalc = Table(cap_calc_box, colWidths=[523])
    t_capcalc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_capcalc)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # SECTION 4: PANDUAN INTEGRASI REST API & LARAVEL CONSUMPTION
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Panduan Integrasi REST API untuk Aplikasi Laravel", h1_style))
    story.append(Paragraph(
        "Aplikasi Laravel Web Portal dapat memanggil 3 endpoint utama REST API microservice pada port 8000:",
        styles['Normal']
    ))
    story.append(Spacer(1, 4))

    api_summary_table = [
        [Paragraph("<b>Endpoint HTTP</b>", table_header_style), Paragraph("<b>Fungsi & Kegunaan</b>", table_header_style), Paragraph("<b>Tabel Sync Database</b>", table_header_style)],
        [Paragraph("<code>POST /api/v1/forecast</code>", table_cell_style), Paragraph("Prediksi Fuel Ratio harian (L/BCM) & status alert.", table_cell_style), Paragraph("<code>daily_forecast_logs</code>", table_cell_style)],
        [Paragraph("<code>POST /api/v1/anomaly-detect</code>", table_cell_style), Paragraph("Scan log BBM unit & isolasi lonjakan spike anomali.", table_cell_style), Paragraph("<code>unit_anomaly_spikes</code>", table_cell_style)],
        [Paragraph("<code>POST /api/v1/calculate-capacity</code>", table_cell_style), Paragraph("Kalkulasi utilisasi %, unit aktif, & BBM per-unit per-jam.", table_cell_style), Paragraph("<code>capacity_allocations</code> & <code>capacity_unit_allocations</code>", table_cell_style)],
        [Paragraph("<code>GET /ready</code>", table_cell_style), Paragraph("Readiness probe memastikan model ML ter-load di RAM.", table_cell_style), Paragraph("RAM Cache Status", table_cell_style)]
    ]
    t_apisum = Table(api_summary_table, colWidths=[160, 213, 150])
    t_apisum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_apisum)
    story.append(Spacer(1, 14))

    # Sign-off box
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_SECONDARY, spaceAfter=10))
    story.append(Paragraph("<b>DOKUMEN INI DIBUAT DENGAN KEPATUHAN MUTLAK PADA GROUND-TRUTH PLAN KIDECO FUEL RATIO OPTIMIZATION SYSTEM</b>", ParagraphStyle('SignOff', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=COLOR_PRIMARY, alignment=1)))

    # Build PDF Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Dokumen PDF berhasil dibuat di: {pdf_filename}")

if __name__ == "__main__":
    build_pdf_documentation()
