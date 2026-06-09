"""
Orkestrasi laporan keuangan bulanan:
1. Ambil PDF tagihan dari Google Drive (Tagihan_KK/YYYY-MM/)
2. Parse setiap PDF dengan parser bank masing-masing
3. Hitung rencana pembayaran
4. Generate 3 file laporan (checklist.md, payment_plan.md, .xlsx)
5. Upload laporan ke Drive (Laporan_KK/YYYY-MM/)
6. Commit & push ke GitHub
"""

import os
import sys
import json
import subprocess
import tempfile
from datetime import date, datetime
from pathlib import Path

from config import (
    CARDS, DRIVE_INBOX_FOLDER, DRIVE_REPORT_FOLDER,
    MONTHLY_BUDGET, DEFAULT_BUDGET, INDONESIAN_MONTHS
)
from parsers import PARSER_MAP
from calculator import build_payment_plans
from report_generator import generate_checklist_md, generate_payment_plan_md, generate_excel
from drive_client import get_service, find_or_create_folder, list_pdfs_in_folder, download_file, upload_bytes, upload_file

# Card-id → GitHub Secret name for PDF password
PDF_PASSWORD_SECRETS = {
    "bca":          "PDF_PASS_BCA",
    "dbs_3099":     "PDF_PASS_DBS",
    "mandiri_3517": "PDF_PASS_MANDIRI",
    "cimb_0407":    "PDF_PASS_CIMB",
    "cimb_5614":    "PDF_PASS_CIMB",
    "cimb_6174":    "PDF_PASS_CIMB_SYARIAH",
    "bni_0493":     "PDF_PASS_BNI",
    "bni_2256":     "PDF_PASS_BNI",
    "bsi_6634":     "PDF_PASS_BSI",
    "mega_6566":    "PDF_PASS_MEGA",
}

# Prefix of PDF filename → card_id (filename sent by bank email)
PDF_FILENAME_PATTERNS = {
    "eBilling_BCA":      "bca",
    "BCA_":              "bca",
    "DBS_":              "dbs_3099",
    "digibank":          "dbs_3099",
    "Mandiri":           "mandiri_3517",
    "CIMB_0407":         "cimb_0407",
    "CIMB_5614":         "cimb_5614",
    "CIMB_6174":         "cimb_6174",
    "BNI_0493":          "bni_0493",
    "BNI_2256":          "bni_2256",
    "BSI_":              "bsi_6634",
    "Mega_6566":         "mega_6566",
}


def _get_password(card_id: str) -> str:
    secret_name = PDF_PASSWORD_SECRETS.get(card_id, "")
    return os.environ.get(secret_name, "")


def _infer_card_id(filename: str) -> str | None:
    for prefix, card_id in PDF_FILENAME_PATTERNS.items():
        if prefix.lower() in filename.lower():
            return card_id
    return None


def _load_prev_state() -> tuple[dict, dict]:
    """
    Baca prev_balances dan prev_payments dari file state JSON jika ada.
    Returns (prev_balances, prev_payments) — dict card_id → int.
    """
    state_file = Path(__file__).parent / "state.json"
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        return state.get("balances", {}), state.get("payments", {})
    return {}, {}


def _save_state(plans):
    """Simpan saldo dan rekomendasi pembayaran bulan ini sebagai state bulan depan."""
    state = {
        "balances": {p.card_id: p.current_balance for p in plans},
        "payments": {p.card_id: p.recommended_payment for p in plans},
    }
    state_file = Path(__file__).parent / "state.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def _git_commit_push(files: list[str], year_month: str):
    repo_root = Path(__file__).parent.parent
    branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_root, text=True
    ).strip()

    for f in files:
        subprocess.run(["git", "add", f], cwd=repo_root, check=True)

    month_label = f"{INDONESIAN_MONTHS[int(year_month.split('-')[1])]} {year_month.split('-')[0]}"
    msg = f"chore: auto-generate laporan {month_label}"
    subprocess.run(["git", "commit", "-m", msg], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "push", "-u", "origin", branch],
        cwd=repo_root, check=True
    )


def run(year_month: str | None = None):
    today = date.today()
    if year_month is None:
        # Bulan yang baru saja lewat (tagihan bulan lalu diproses di awal bulan ini)
        if today.month == 1:
            ym = f"{today.year - 1}-12"
        else:
            ym = f"{today.year}-{today.month - 1:02d}"
        year_month = ym

    run_date = today.strftime("%Y-%m-%d")
    print(f"=== Laporan Keuangan {year_month} | Run: {run_date} ===")

    # 1. Hubungkan ke Google Drive
    svc = get_service()
    inbox_root = find_or_create_folder(svc, DRIVE_INBOX_FOLDER)
    inbox_month = find_or_create_folder(svc, year_month, inbox_root)
    report_root = find_or_create_folder(svc, DRIVE_REPORT_FOLDER)
    report_month = find_or_create_folder(svc, year_month, report_root)

    # 2. Download & parse PDF tagihan
    pdfs = list_pdfs_in_folder(svc, inbox_month)
    print(f"Ditemukan {len(pdfs)} PDF di Drive/{DRIVE_INBOX_FOLDER}/{year_month}/")

    billing_data = {}
    for pdf_meta in pdfs:
        card_id = _infer_card_id(pdf_meta["name"])
        if card_id is None:
            print(f"  SKIP {pdf_meta['name']} — kartu tidak dikenali")
            continue
        parser = PARSER_MAP.get(card_id)
        if parser is None:
            print(f"  SKIP {pdf_meta['name']} — parser tidak ada untuk {card_id}")
            continue

        print(f"  Parsing {pdf_meta['name']} → {card_id} ...", end=" ")
        pdf_bytes = download_file(svc, pdf_meta["id"])
        password = _get_password(card_id)
        bd = parser.parse(pdf_bytes, password)
        if bd.parse_errors:
            print(f"PERINGATAN: {'; '.join(bd.parse_errors)}")
        else:
            print(f"OK (balance={bd.total_balance})")
        billing_data[card_id] = bd

    # 3. Hitung rencana pembayaran
    prev_balances, prev_payments = _load_prev_state()
    plans = build_payment_plans(billing_data, prev_balances, prev_payments, year_month)
    print(f"\nTotal kartu aktif: {len(plans)}")
    for p in plans:
        est = " [EST]" if p.is_estimated else ""
        print(f"  {p.bank} ...{p.last4}: Rp {p.current_balance:,} → rec Rp {p.recommended_payment:,}{est}")

    # 4. Generate laporan
    repo_root = Path(__file__).parent.parent
    reports_dir = repo_root / "financial-reports"
    reports_dir.mkdir(exist_ok=True)

    checklist_md  = generate_checklist_md(plans, year_month, run_date)
    payment_md    = generate_payment_plan_md(plans, year_month, run_date)

    m_label = f"{INDONESIAN_MONTHS[int(year_month.split('-')[1])]}{year_month.split('-')[0]}"
    checklist_path = reports_dir / f"03_Checklist_Pembayaran_{m_label}.md"
    payment_path   = reports_dir / f"02_Rencana_Pembayaran_{m_label}.md"
    excel_path     = reports_dir / f"Suwandhy_FinancialPlan_{year_month}.xlsx"

    checklist_path.write_text(checklist_md, encoding="utf-8")
    payment_path.write_text(payment_md, encoding="utf-8")
    generate_excel(plans, year_month, str(excel_path))

    print(f"\nLaporan ditulis:")
    print(f"  {checklist_path.name}")
    print(f"  {payment_path.name}")
    print(f"  {excel_path.name}")

    # 5. Upload laporan ke Drive
    for path in [checklist_path, payment_path]:
        upload_file(svc, str(path), report_month, "text/markdown")
    upload_file(
        svc, str(excel_path), report_month,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    print(f"Laporan di-upload ke Drive/{DRIVE_REPORT_FOLDER}/{year_month}/")

    # 6. Simpan state & commit
    _save_state(plans)
    state_file = str(Path(__file__).parent / "state.json")

    try:
        _git_commit_push(
            [str(checklist_path), str(payment_path), str(excel_path), state_file],
            year_month,
        )
        print("Git commit & push berhasil.")
    except subprocess.CalledProcessError as e:
        print(f"Git commit/push gagal: {e}")

    print("\n=== Selesai ===")
    return plans


if __name__ == "__main__":
    ym = sys.argv[1] if len(sys.argv) > 1 else None
    run(ym)
