"""
Kalkulasi pembayaran kartu kredit dan estimasi saldo BCA/DBS.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date, datetime
import calendar

from config import CARDS, ACTIVE_INSTALLMENTS, MONTHLY_BUDGET, DEFAULT_BUDGET, INDONESIAN_MONTHS
from parsers.base import BillingData


@dataclass
class CardPaymentPlan:
    card_id: str
    bank: str
    last4: str
    current_balance: int
    minimum_payment: int
    recommended_payment: int
    due_date: Optional[str]
    is_estimated: bool
    priority: str          # KRITIS / TINGGI / SEDANG / RENDAH
    active_installments_total: int
    notes: str = ""


def get_budget(year_month: str) -> int:
    return MONTHLY_BUDGET.get(year_month, DEFAULT_BUDGET)


def get_active_installments_for_card(card_id: str, year_month: str) -> list:
    """Kembalikan cicilan aktif untuk kartu tertentu di bulan year_month (YYYY-MM)."""
    result = []
    for inst in ACTIVE_INSTALLMENTS:
        if inst["card_id"] != card_id:
            continue
        end_ym = inst["end_ym"]
        if year_month <= end_ym:
            result.append(inst)
    return result


def estimate_balance(card_id: str, prev_balance: int, payment_made: int, year_month: str) -> int:
    """
    Estimasi saldo BCA atau DBS saat tagihan belum masuk.
    Formula: saldo_lama × (1 + rate) - pembayaran_bulan_lalu
    Asumsi: tidak ada pembelian baru.
    """
    card_cfg = next((c for c in CARDS if c["id"] == card_id), None)
    if card_cfg is None:
        return prev_balance

    rate = card_cfg["interest_rate"]
    # Hitung total cicilan aktif bulan ini (sudah tertanam di saldo, bukan tambahan)
    # Interest hanya pada bagian revolving = saldo - cicilan balances
    installments = get_active_installments_for_card(card_id, year_month)
    installment_balance = sum(
        i["monthly"] * (i["total"] - i["current"])
        for i in installments
    )
    revolving_balance = max(0, prev_balance - installment_balance)
    interest = int(revolving_balance * rate)
    estimated = prev_balance + interest - payment_made
    return max(0, estimated)


def compute_minimum_payment(balance: int, rate: float = 0.0175, pct: float = 0.05) -> int:
    """
    Minimum payment = max(10% saldo, 5% saldo + bunga) — umumnya bank Indonesia.
    Simplified: 5% dari total tagihan, min Rp 50.000.
    """
    minimum = max(50_000, int(balance * pct))
    return minimum


def build_payment_plans(
    billing_data: dict,          # card_id → BillingData
    prev_balances: dict,         # card_id → int (saldo bulan lalu, untuk estimasi)
    prev_payments: dict,         # card_id → int (pembayaran bulan lalu)
    target_month: str,           # YYYY-MM (bulan untuk perencanaan pembayaran)
) -> list[CardPaymentPlan]:
    """
    Buat rencana pembayaran untuk semua kartu aktif di target_month.
    """
    plans = []
    budget = get_budget(target_month)
    total_remaining = budget

    # Urutkan kartu: due date terkecil dahulu, kartu lewat jatuh tempo prioritas tertinggi
    today_str = date.today().strftime("%Y-%m-%d")

    for card in CARDS:
        cid = card["id"]

        # Skip kartu sudah ditutup
        if card.get("active_until") and target_month > card["active_until"]:
            continue

        bd: Optional[BillingData] = billing_data.get(cid)

        # Gunakan estimasi jika kartu late_billing dan PDF belum ada
        if bd is None or bd.total_balance is None:
            prev_bal = prev_balances.get(cid, 0)
            prev_pay = prev_payments.get(cid, 0)
            balance = estimate_balance(cid, prev_bal, prev_pay, target_month)
            is_estimated = True
            due_date = None
            min_pay = compute_minimum_payment(balance, card["interest_rate"])
        else:
            balance = bd.total_balance
            is_estimated = bd.is_estimated
            due_date = bd.due_date
            min_pay = bd.minimum_payment or compute_minimum_payment(balance, card["interest_rate"])

        if balance <= 0:
            continue

        # Prioritas
        overdue = due_date and due_date < today_str
        if overdue:
            priority = "KRITIS"
        elif balance > 20_000_000:
            priority = "TINGGI"
        elif balance > 5_000_000:
            priority = "SEDANG"
        else:
            priority = "RENDAH"

        # Cicilan aktif
        installments = get_active_installments_for_card(cid, target_month)
        inst_total = sum(i["monthly"] for i in installments)

        # Rekomendasi bayar = min + ekstra proporsional dari sisa budget
        rec_pay = max(min_pay, inst_total)

        notes = ""
        if is_estimated:
            notes = "⚠️ ESTIMASI — tagihan belum masuk"
        if overdue:
            notes = "🔴 LEWAT JATUH TEMPO — bayar segera!"

        plans.append(CardPaymentPlan(
            card_id=cid,
            bank=card["bank"],
            last4=card["last4"],
            current_balance=balance,
            minimum_payment=min_pay,
            recommended_payment=rec_pay,
            due_date=due_date,
            is_estimated=is_estimated,
            priority=priority,
            active_installments_total=inst_total,
            notes=notes,
        ))

    # Urutkan: KRITIS → TINGGI → SEDANG → RENDAH, lalu due date
    priority_order = {"KRITIS": 0, "TINGGI": 1, "SEDANG": 2, "RENDAH": 3}
    plans.sort(key=lambda p: (priority_order.get(p.priority, 9), p.due_date or "9999"))

    # Distribusi budget: isi recommended_payment dari budget tersedia
    remaining = budget
    for p in plans:
        if p.recommended_payment > remaining:
            p.recommended_payment = max(p.minimum_payment, min(p.recommended_payment, remaining))
        remaining -= p.recommended_payment
        remaining = max(0, remaining)

    return plans


def total_debt(billing_data: dict, prev_balances: dict, prev_payments: dict, target_month: str) -> int:
    plans = build_payment_plans(billing_data, prev_balances, prev_payments, target_month)
    return sum(p.current_balance for p in plans)
