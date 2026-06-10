"""
Orkestrasi laporan keuangan bulanan (mode lokal — jalankan dari PC).

Alur:
1. Baca PDF tagihan dari folder lokal (Google Drive for Desktop sync)
2. Parse setiap PDF dengan parser bank masing-masing
3. Hitung rencana pembayaran
4. Generate laporan (checklist.md, payment_plan.md, .xlsx)
5. Simpan ke folder OneDrive laporan bulanan
6. (Opsional) Commit & push ke GitHub
"""

import os
import sys
import json
import subprocess
from datetime import date
from pathlib import Path

from config import (
    CARDS, INDONESIAN_MONTHS,
    DRIVE_INBOX_FOLDER,   # nama folder di Google Drive (untuk path lokal)
)
from parsers import PARSER_MAP
from calculator import build_payment_plans
from report_generator import generate_checklist_md, generate_payment_plan_md, generate_excel

# ─── Konfigurasi path lokal ────────────────────────────────────────────────────
# Sesuaikan dengan lokasi Google Drive for Desktop di PC Anda
GDRIVE_ROOT = Path(r"G:\My Drive")

# Folder output laporan (OneDrive)
ONEDRIVE_ROOT = Path(r"C:\Users\BEELINK\OneDrive\Documents\Credit Card Billings")

# File password PDF (simpan di luar repo, jangan di-commit!)
# Format JSON: {"bca": "password123", "dbs_3099": "pass456", ...}
# Buat file ini sekali di: C:\Users\BEELINK\.kk_passwords.json
PASSWORDS_FILE = Path.home() / ".kk_passwords.json"

# Aktifkan git push otomatis? (True/False)
GIT_AUTO_PUSH = True

# ─── Helpers ───────────────────────────────────────────────────────────────────

# Prefix nama file PDF → card_id (sesuaikan dengan prefix di gmail_to_drive.gs)
PDF_FILENAME_PATTERNS = {
    "bca_":      "bca",
    "ebilling_bca": "bca",
    "dbs_":      "dbs_3099",
    "digibank":  "dbs_3099",
    "mandiri_":  "mandiri_3517",
    "cimb_0407": "cimb_0407",
    "cimb_5614": "cimb_5614",
    "cimb_6174": "cimb_6174",
    "bni_0493":  "bni_0493",
    "bni_2256":  "bni_2256",
    "bsi_":      "bsi_6634",
    "mega_":     "mega_6566",
}


def _load_passwords() -> dict:
    if PASSWORDS_FILE.exists():
        with open(PASSWORDS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _infer_card_id(filename: str) -> str | None:
    lower = filename.lower()
    for prefix, card_id in PDF_FILENAME_PATTERNS.items():
        if prefix in lower:
            return card_id
    return None


def _load_prev_state() -> tuple[dict, dict]:
    state_file = Path(__file__).parent / "state.json"
    if state_file.exists():
        with open(state_file, encoding="utf-8") as f:
            state = json.load(f)
        return state.get("balances", {}), state.get("payments", {})
    return {}, {}


def _save_state(plans):
    state = {
        "balances": {p.card_id: p.current_balance for p in plans},
        "payments": {p.card_id: p.recommended_payment for p in plans},
    }
    state_file = Path(__file__).parent / "state.json"
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def _git_commit_push(files: list[Path], year_month: str):
    repo_root = Path(__file__).parent.parent
    m_int = int(year_month.split("-")[1])
    month_label = f"{INDONESIAN_MONTHS[m_int]} {year_month.split('-')[0]}"
    for f in files:
        subprocess.run(["git", "add", str(f)], cwd=repo_root, check=True)
    msg = f"chore: auto-generate laporan {month_label}"
    subprocess.run(["git", "commit", "-m", msg], cwd=repo_root, check=True)
    branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_root, text=True
    ).strip()
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=repo_root, check=True)


# ─── Main ──────────────────────────────────────────────────────────────────────

def run(year_month: str | None = None):
    today = date.today()
    if year_month is None:
        # Proses bulan lalu (script dijalankan di awal bulan baru)
        if today.month == 1:
            year_month = f"{today.year - 1}-12"
        else:
            year_month = f"{today.year}-{today.month - 1:02d}"

    run_date = today.strftime("%Y-%m-%d")
    m_int = int(year_month.split("-")[1])
    month_label = INDONESIAN_MONTHS[m_int] + year_month.split("-")[0]   # e.g. "Juni2026"
    month_label_space = f"{INDONESIAN_MONTHS[m_int]} {year_month.split('-')[0]}"
    print(f"=== Laporan Keuangan {month_label_space} | Run: {run_date} ===\n")

    # 1. Temukan folder PDF di Google Drive lokal
    inbox_dir = GDRIVE_ROOT / DRIVE_INBOX_FOLDER / year_month
    if not inbox_dir.exists():
        print(f"[PERINGATAN] Folder tidak ditemukan: {inbox_dir}")
        print("  Pastikan Google Drive for Desktop sudah sync dan folder Tagihan_KK sudah ada.")
        pdf_files = []
    else:
        pdf_files = sorted(inbox_dir.glob("*.pdf"))
        print(f"Ditemukan {len(pdf_files)} PDF di {inbox_dir}")

    # 2. Parse PDF tagihan
    passwords = _load_passwords()
    billing_data = {}

    for pdf_path in pdf_files:
        card_id = _infer_card_id(pdf_path.name)
        if card_id is None:
            print(f"  SKIP {pdf_path.name} — kartu tidak dikenali")
            continue
        parser = PARSER_MAP.get(card_id)
        if parser is None:
            print(f"  SKIP {pdf_path.name} — tidak ada parser untuk {card_id}")
            continue

        print(f"  Parsing {pdf_path.name} → {card_id} ...", end=" ")
        pdf_bytes = pdf_path.read_bytes()
        password = passwords.get(card_id, "")
        bd = parser.parse(pdf_bytes, password)
        if bd.parse_errors:
            print(f"PERINGATAN: {'; '.join(bd.parse_errors)}")
        else:
            print(f"OK  (balance = Rp {bd.total_balance:,})")
        billing_data[card_id] = bd

    # 3. Hitung rencana pembayaran
    prev_balances, prev_payments = _load_prev_state()
    plans = build_payment_plans(billing_data, prev_balances, prev_payments, year_month)

    print(f"\nTotal kartu aktif: {len(plans)}")
    for p in plans:
        est = " [EST]" if p.is_estimated else ""
        print(f"  {p.bank} ...{p.last4}: Rp {p.current_balance:,}  →  rec Rp {p.recommended_payment:,}{est}")

    # 4. Generate laporan
    checklist_md = generate_checklist_md(plans, year_month, run_date)
    payment_md   = generate_payment_plan_md(plans, year_month, run_date)

    # Output: OneDrive folder bulan ini
    out_dir = ONEDRIVE_ROOT / month_label
    out_dir.mkdir(parents=True, exist_ok=True)

    checklist_path = out_dir / f"03_Checklist_Pembayaran_{month_label}.md"
    payment_path   = out_dir / f"02_Rencana_Pembayaran_{month_label}.md"
    excel_path     = out_dir / f"Suwandhy_FinancialPlan_{year_month}.xlsx"

    checklist_path.write_text(checklist_md, encoding="utf-8")
    payment_path.write_text(payment_md, encoding="utf-8")
    generate_excel(plans, year_month, str(excel_path))

    print(f"\nLaporan disimpan di: {out_dir}")
    print(f"  {checklist_path.name}")
    print(f"  {payment_path.name}")
    print(f"  {excel_path.name}")

    # Juga simpan salinan ke repo (untuk git history)
    repo_reports = Path(__file__).parent.parent / "financial-reports"
    repo_reports.mkdir(exist_ok=True)
    (repo_reports / checklist_path.name).write_text(checklist_md, encoding="utf-8")
    (repo_reports / payment_path.name).write_text(payment_md, encoding="utf-8")
    generate_excel(plans, year_month, str(repo_reports / excel_path.name))

    # 5. Simpan state untuk estimasi bulan depan
    _save_state(plans)

    # 6. (Opsional) Git commit & push
    if GIT_AUTO_PUSH:
        try:
            state_file = Path(__file__).parent / "state.json"
            repo_checklist = repo_reports / checklist_path.name
            repo_payment   = repo_reports / payment_path.name
            repo_excel     = repo_reports / excel_path.name
            _git_commit_push(
                [repo_checklist, repo_payment, repo_excel, state_file],
                year_month,
            )
            print("Git commit & push berhasil.")
        except subprocess.CalledProcessError as e:
            print(f"[PERINGATAN] Git push gagal: {e}")

    print("\n=== Selesai ===")
    return plans


if __name__ == "__main__":
    ym = sys.argv[1] if len(sys.argv) > 1 else None
    run(ym)
