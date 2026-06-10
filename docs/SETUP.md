# Setup Automasi Laporan Keuangan Bulanan

## Arsitektur (100% Gratis, Berjalan di PC)

```
Gmail (tagihan bank)
    ↓ [Google Apps Script — GRATIS, bagian akun Google]
Google Drive: Tagihan_KK/YYYY-MM/*.pdf
    ↓ [Google Drive for Desktop — sync otomatis ke PC, GRATIS]
C:\Users\BEELINK\Google Drive\Tagihan_KK\YYYY-MM\*.pdf
    ↓ [Python — Windows Task Scheduler, hari ke-1 tiap bulan]
C:\Users\BEELINK\OneDrive\Documents\Credit Card Billings\NamaBulan\
```

**Tidak butuh Google Cloud, tidak butuh billing, tidak butuh GitHub Actions.**

---

## Bagian 1: Instal Google Drive for Desktop

1. Download dari: [drive.google.com/drive/download](https://drive.google.com/drive/download)
2. Login dengan akun Google Anda
3. Pilih **Mirroring** (bukan streaming) agar file tersedia offline
4. Buat folder **Tagihan_KK** di Google Drive lewat browser
5. Setelah sync, folder akan tersedia di: `C:\Users\BEELINK\Google Drive\Tagihan_KK\`

---

## Bagian 2: Install Python & Dependencies

1. Download Python 3.11+ dari [python.org](https://python.org)
   - Centang **"Add Python to PATH"** saat instalasi
2. Buka Command Prompt, masuk ke folder repo:
   ```
   cd C:\path\to\GoogleColab
   pip install -r requirements.txt
   ```
3. Test:
   ```
   python scripts/main.py --help
   ```

---

## Bagian 3: Simpan Password PDF (Sekali Saja)

Buat file `C:\Users\BEELINK\.kk_passwords.json` (jangan di-commit ke GitHub!):

```json
{
  "bca":          "tanggal_lahir_atau_no_hp",
  "dbs_3099":     "password_dbs",
  "mandiri_3517": "password_mandiri",
  "cimb_0407":    "password_cimb",
  "cimb_5614":    "password_cimb",
  "cimb_6174":    "password_cimb_syariah",
  "bni_0493":     "password_bni",
  "bni_2256":     "password_bni",
  "bsi_6634":     "password_bsi",
  "mega_6566":    "password_mega"
}
```

> File ini tersimpan di home folder user, **bukan** di dalam folder repo.

---

## Bagian 4: Google Apps Script (Gmail → Drive)

Apps Script gratis dan berjalan di akun Google Anda — tidak butuh Google Cloud.

### 4.1 Deploy

1. Buka [script.google.com](https://script.google.com) → **New project**
2. Paste isi file `scripts/gmail_to_drive.gs`
3. Rename project: **KK-Gmail-to-Drive**
4. Klik **Run → saveTagihanToDrive** untuk authorize (izinkan Gmail + Drive)

### 4.2 Tambahkan Trigger Bulanan

1. Klik ikon jam (Triggers) di sisi kiri
2. **Add Trigger**:
   - Function: `saveTagihanToDrive`
   - Event source: **Time-driven**
   - Type: **Month timer**, hari ke-**1**, pukul **05:00–06:00**
3. Save

### 4.3 Sesuaikan Query (bila perlu)

Edit `BANK_SEARCH_RULES` di file `.gs` — sesuaikan dengan subject/pengirim email tagihan bank Anda.

---

## Bagian 5: Windows Task Scheduler

Jalankan script Python otomatis setiap tanggal 1 bulan.

1. Buka **Task Scheduler** (cari di Start Menu)
2. **Create Basic Task**:
   - Name: `KK Monthly Report`
   - Trigger: **Monthly**, hari **1**, pukul **08:00**
   - Action: **Start a program**
     - Program: `C:\path\ke\GoogleColab\scripts\run_monthly.bat`
3. Finish

### Cara Test Manual

Buka Command Prompt:
```
cd C:\path\ke\GoogleColab\scripts
python main.py 2026-06
```

Ganti `2026-06` dengan bulan yang ingin diproses.

---

## Bagian 6: Struktur Folder

```
Google Drive (lokal via Drive for Desktop):
  C:\Users\BEELINK\Google Drive\
    Tagihan_KK\
      2026-06\
        BCA_202606_tagihan.pdf
        DBS_202606_statement.pdf
        ...

Output laporan (OneDrive):
  C:\Users\BEELINK\OneDrive\Documents\Credit Card Billings\
    Juni2026\
      02_Rencana_PembayaranJuni2026.md
      03_Checklist_PembayaranJuni2026.md
      Suwandhy_FinancialPlan_2026-06.xlsx

Repo GitHub (salinan untuk history):
  financial-reports\
    02_Rencana_PembayaranJuni2026.md
    03_Checklist_PembayaranJuni2026.md
    Suwandhy_FinancialPlan_2026-06.xlsx
```

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| PDF gagal di-decrypt | Cek `.kk_passwords.json`, pastikan password sesuai |
| Parser tidak menemukan saldo | Buka PDF manual, cek format angka; update regex di `scripts/parsers/` |
| File PDF tidak terbaca | Pastikan Google Drive for Desktop sudah sync (ikon tray berwarna) |
| Apps Script tidak menemukan email | Cek query di `BANK_SEARCH_RULES`, pastikan email ada di inbox |
| Task Scheduler tidak jalan | Cek log: `GoogleColab\logs\run_log.txt` |
| Git push gagal | Set `GIT_AUTO_PUSH = False` di `main.py` jika tidak butuh auto-push |

---

*Setup by SUWANDHY PRAHARTO — sistem berjalan otomatis setiap bulan tanpa Claude.*
