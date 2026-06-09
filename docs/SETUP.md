# Setup Automation Laporan Keuangan Bulanan

## Gambaran Arsitektur

```
Gmail (tagihan bank)
    ↓ [Google Apps Script — bulanan, hari ke-1]
Google Drive: Tagihan_KK/YYYY-MM/*.pdf
    ↓ [GitHub Actions — cron hari ke-1 pukul 08:00 WIB]
Python scripts/main.py
    ↓
financial-reports/*.md + *.xlsx  →  GitHub commit
                                 →  Drive: Laporan_KK/YYYY-MM/
```

---

## Bagian 1: Google Service Account (sekali saja)

### 1.1 Buat Project & Enable API

1. Buka [Google Cloud Console](https://console.cloud.google.com)
2. Buat project baru, misalnya **KK-Reports**
3. Enable **Google Drive API**: *APIs & Services → Library → Google Drive API → Enable*

### 1.2 Buat Service Account

1. *IAM & Admin → Service Accounts → Create Service Account*
2. Name: `kk-reports-sa`
3. Role: **Editor** (atau buat custom role dengan Drive permissions saja)
4. *Keys → Add Key → JSON* → download file `credentials.json`

### 1.3 Share Folder Drive ke Service Account

1. Buka Google Drive di browser
2. Buat folder **Tagihan_KK** (jika belum ada)
3. Klik kanan → Share → masukkan email service account (format: `kk-reports-sa@PROJECT_ID.iam.gserviceaccount.com`)
4. Berikan akses **Editor**
5. Lakukan hal yang sama untuk folder **Laporan_KK**

### 1.4 Simpan Credentials ke GitHub Secrets

1. Buka repo GitHub → *Settings → Secrets and variables → Actions → New repository secret*
2. Nama: `GOOGLE_CREDENTIALS`
3. Value: isi seluruh konten file `credentials.json` (format JSON)

---

## Bagian 2: GitHub Secrets — Password PDF

Tambahkan secret berikut (password untuk decrypt PDF tagihan):

| Secret Name         | Bank                  | Keterangan                        |
|---------------------|-----------------------|-----------------------------------|
| `PDF_PASS_BCA`      | BCA                   | Biasanya nomor HP / tgl lahir     |
| `PDF_PASS_DBS`      | DBS digibank          |                                   |
| `PDF_PASS_MANDIRI`  | Mandiri               |                                   |
| `PDF_PASS_CIMB`     | CIMB Niaga 0407/5614  |                                   |
| `PDF_PASS_CIMB_SYARIAH` | CIMB Syariah 6174 |                                  |
| `PDF_PASS_BNI`      | BNI 0493/2256         |                                   |
| `PDF_PASS_BSI`      | BSI 6634              |                                   |
| `PDF_PASS_MEGA`     | Bank Mega 6566        |                                   |

Cara tambah: *Settings → Secrets → Actions → New repository secret*

---

## Bagian 3: Google Apps Script (Gmail → Drive)

### 3.1 Deploy Script

1. Buka [script.google.com](https://script.google.com) → *New project*
2. Paste isi file `scripts/gmail_to_drive.gs`
3. Rename project menjadi **KK-Gmail-to-Drive**
4. Klik *Run → saveTagihanToDrive* untuk authorize (izinkan Gmail + Drive)

### 3.2 Tambahkan Trigger Bulanan

1. Klik ikon jam (Triggers) di kiri
2. *Add Trigger*:
   - Function: `saveTagihanToDrive`
   - Event source: **Time-driven**
   - Type: **Month timer**, hari ke-**1**, pukul **06:00–07:00** (WIB = UTC+7)
3. Save

### 3.3 Sesuaikan Query Gmail (jika perlu)

Edit variabel `BANK_SEARCH_RULES` di file `.gs` sesuai subject/pengirim email tagihan bank Anda.

---

## Bagian 4: GitHub Actions

Workflow sudah terkonfigurasi di `.github/workflows/monthly_report.yml`.

- Jadwal otomatis: **hari ke-1 setiap bulan pukul 08:00 WIB** (01:00 UTC)
- Bisa dijalankan manual: *Actions → Monthly Credit Card Report → Run workflow*
  - Isi `year_month` (format YYYY-MM) untuk proses bulan tertentu, atau kosongkan untuk bulan lalu

---

## Bagian 5: Update Konfigurasi Bulanan

Edit `scripts/config.py` bila ada perubahan:

```python
# Update saldo awal bulan (bila ingin override estimasi)
MONTHLY_BUDGET = {
    "2026-06": 12_500_000,
    "2026-07": 15_000_000,
    # dst.
}

# Tambah/hapus cicilan aktif
ACTIVE_INSTALLMENTS = [
    {"card_id": "bca", "description": "...", "monthly": 2_582_524, ...},
]
```

---

## Bagian 6: Struktur Folder Drive

```
My Drive/
├── Tagihan_KK/           ← input (diisi oleh Apps Script)
│   ├── 2026-06/
│   │   ├── BCA_202606_tagihan.pdf
│   │   ├── DBS_202606_statement.pdf
│   │   └── ...
│   └── 2026-07/
│       └── ...
└── Laporan_KK/           ← output (diisi oleh GitHub Actions)
    ├── 2026-06/
    │   ├── 03_Checklist_PembayaranJuni2026.md
    │   ├── 02_Rencana_PembayaranJuni2026.md
    │   └── Suwandhy_FinancialPlan_2026-06.xlsx
    └── ...
```

---

## Trouble Shooting

| Masalah | Solusi |
|---------|--------|
| PDF gagal di-decrypt | Cek password di GitHub Secret, pastikan sesuai |
| Parser tidak menemukan saldo | Buka PDF manual, cek format angka; update regex di `parsers/` |
| Drive permission denied | Pastikan folder di-share ke email service account |
| Apps Script tidak menemukan email | Cek `BANK_SEARCH_RULES` query, pastikan email sudah di inbox |
| GitHub Actions gagal push | Pastikan workflow punya permission `contents: write` |

---

*Setup by SUWANDHY PRAHARTO — sistem ini berjalan otomatis setiap bulan tanpa intervensi Claude.*
