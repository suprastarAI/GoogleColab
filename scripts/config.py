"""
Konfigurasi kartu kredit dan parameter keuangan Suwandhy Praharto.
Update bagian CARDS dan ACTIVE_INSTALLMENTS setiap ada perubahan.
"""

from datetime import date

OWNER = "SUWANDHY PRAHARTO"
EMAIL = "suwandhypraharto@gmail.com"

# ── Kartu Kredit ─────────────────────────────────────────────────────────────
# has_late_billing = True  → tagihan datang awal bulan berikutnya → estimasi jika belum ada PDF
CARDS = [
    {
        "id": "mandiri_3517",
        "bank": "Mandiri",
        "product": "Platinum",
        "last4": "3517",
        "interest_rate": 0.0175,
        "due_day": 2,
        "billing_day": 13,
        "limit": 29_000_000,
        "active_until": "2026-12",
        "has_late_billing": False,
        "gmail_sender": "e-statement@bankmandiri.co.id",
        "gmail_subject_kw": "e-Statement Mandiri",
    },
    {
        "id": "mega_6566",
        "bank": "Bank Mega",
        "product": "Ultima 6566",
        "last4": "6566",
        "interest_rate": 0.0175,
        "due_day": 3,
        "billing_day": 18,
        "limit": 122_000_000,
        "active_until": "2027-03",
        "has_late_billing": False,
        "gmail_sender": "info@bankmega.co.id",
        "gmail_subject_kw": "e-Statement",
    },
    {
        "id": "cimb_0407",
        "bank": "CIMB Niaga",
        "product": "MC Platinum Accor",
        "last4": "0407",
        "interest_rate": 0.0175,
        "due_day": 9,
        "billing_day": 24,
        "limit": 90_000_000,
        "active_until": "2027-04",
        "has_late_billing": False,
        "gmail_sender": "eStatement@cimbniaga.co.id",
        "gmail_subject_kw": "e-Statement CIMB",
    },
    {
        "id": "cimb_5614",
        "bank": "CIMB Niaga",
        "product": "MC Platinum CashPlus",
        "last4": "5614",
        "interest_rate": 0.0059,
        "due_day": 5,
        "billing_day": 20,
        "limit": 90_000_000,
        "active_until": "2027-03",
        "has_late_billing": False,
        "gmail_sender": "eStatement@cimbniaga.co.id",
        "gmail_subject_kw": "e-Statement CIMB",
    },
    {
        "id": "cimb_6174",
        "bank": "CIMB Syariah",
        "product": "MC Platinum Syariah",
        "last4": "6174",
        "interest_rate": 0.0,
        "due_day": 5,
        "billing_day": 19,
        "limit": 90_000_000,
        "active_until": "2026-07",
        "has_late_billing": False,
        "gmail_sender": "eStatement@cimbniaga.co.id",
        "gmail_subject_kw": "e-Statement CIMB",
    },
    {
        "id": "bni_0493",
        "bank": "BNI",
        "product": "MC Titanium",
        "last4": "0493",
        "interest_rate": 0.0175,
        "due_day": 6,
        "billing_day": 17,
        "limit": 54_000_000,
        "active_until": "2027-01",
        "has_late_billing": False,
        "gmail_sender": "e-statement@bni.co.id",
        "gmail_subject_kw": "e-Statement BNI",
    },
    {
        "id": "bni_2256",
        "bank": "BNI",
        "product": "Lotte Mart Platinum",
        "last4": "2256",
        "interest_rate": 0.0175,
        "due_day": 3,
        "billing_day": 14,
        "limit": 11_000_000,
        "active_until": "2026-11",
        "has_late_billing": False,
        "gmail_sender": "e-statement@bni.co.id",
        "gmail_subject_kw": "e-Statement BNI",
    },
    {
        "id": "bsi_6634",
        "bank": "BSI",
        "product": "Hasanah Card Gold",
        "last4": "6634",
        "interest_rate": 0.0175,
        "due_day": 8,
        "billing_day": 18,
        "limit": 25_000_000,
        "active_until": "2026-09",
        "has_late_billing": False,
        "gmail_sender": "info@bankbsi.co.id",
        "gmail_subject_kw": "e-Statement BSI",
    },
    {
        "id": "dbs_3099",
        "bank": "DBS digibank",
        "product": "Visa Travel Platinum",
        "last4": "3099",
        "interest_rate": 0.0175,
        "due_day": 10,
        "billing_day": 25,
        "limit": 12_500_000,
        "active_until": "2026-06",
        "has_late_billing": True,
        "gmail_sender": "donotreply@dbs.com",
        "gmail_subject_kw": "digibank statement",
    },
    {
        "id": "bca",
        "bank": "BCA",
        "product": "Multi-Kartu",
        "last4": "multi",
        "interest_rate": 0.0175,
        "due_day": 19,
        "billing_day": 3,
        "limit": 94_000_000,
        "active_until": "2027-04",
        "has_late_billing": True,
        "gmail_sender": "eBill@bca.co.id",
        "gmail_subject_kw": "eBill BCA",
    },
]

# ── Cicilan Aktif ─────────────────────────────────────────────────────────────
# Update setiap bulan: naikkan 'current', hapus yang sudah selesai (current >= total)
ACTIVE_INSTALLMENTS = [
    {
        "card_id": "bca",
        "description": "BCA Insurance",
        "monthly": 2_582_524,
        "total": 3,
        "current": 2,
        "end_ym": "2026-07",
        "rate": 0.0,
    },
    {
        "card_id": "bca",
        "description": "Galaxy Mall UR",
        "monthly": 169_833,
        "total": 12,
        "current": 5,
        "end_ym": "2027-01",
        "rate": 0.0,
    },
    {
        "card_id": "cimb_5614",
        "description": "CashPlus Telesales A",
        "monthly": 508_124,
        "total": 12,
        "current": 8,
        "end_ym": "2026-09",
        "rate": 0.0059,
    },
    {
        "card_id": "cimb_5614",
        "description": "CashPlus Telesales B",
        "monthly": 3_556_864,
        "total": 12,
        "current": 8,
        "end_ym": "2026-09",
        "rate": 0.0059,
    },
    {
        "card_id": "cimb_0407",
        "description": "Shopee BARU 1/12",
        "monthly": 686_127,
        "total": 12,
        "current": 1,
        "end_ym": "2027-04",
        "rate": 0.0,
    },
    {
        "card_id": "cimb_0407",
        "description": "Ocean Dental BSD",
        "monthly": 308_333,
        "total": 12,
        "current": 7,
        "end_ym": "2026-10",
        "rate": 0.0,
    },
    {
        "card_id": "mandiri_3517",
        "description": "Power Cash",
        "monthly": 583_332,
        "total": 12,
        "current": 9,
        "end_ym": "2026-08",
        "rate": 0.0,
    },
    {
        "card_id": "mandiri_3517",
        "description": "Adidas Outlet",
        "monthly": 175_000,
        "total": 12,
        "current": 4,
        "end_ym": "2027-01",
        "rate": 0.0,
    },
    {
        "card_id": "bni_0493",
        "description": "SS Tag 0%",
        "monthly": 2_538_483,
        "total": 6,
        "current": 4,
        "end_ym": "2026-07",
        "rate": 0.0,
    },
    {
        "card_id": "bni_0493",
        "description": "Shopee BNI 5/12 A",
        "monthly": 189_743,
        "total": 12,
        "current": 5,
        "end_ym": "2026-12",
        "rate": 0.0,
    },
    {
        "card_id": "bni_0493",
        "description": "Shopee BNI 5/12 B",
        "monthly": 101_696,
        "total": 12,
        "current": 5,
        "end_ym": "2026-12",
        "rate": 0.0,
    },
]

# ── Budget per bulan ──────────────────────────────────────────────────────────
MONTHLY_BUDGET = {
    "2026-06": 12_500_000,
    "2026-07": 15_000_000,
    "2026-08": 17_500_000,
    "2026-09": 20_000_000,
}
DEFAULT_BUDGET = 25_000_000  # Oct 2026 onwards

# ── Google Drive ──────────────────────────────────────────────────────────────
DRIVE_INBOX_FOLDER = "Tagihan_KK"       # PDF masuk disimpan di sini
DRIVE_REPORT_FOLDER = "Laporan_KK"      # Laporan output disimpan di sini

# ── Hari eksekusi GitHub Actions ──────────────────────────────────────────────
# Jalankan tiap tanggal 1: sebagian besar tagihan sudah masuk, BCA/DBS diestimasi
RUN_DAY = 1

INDONESIAN_MONTHS = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}
