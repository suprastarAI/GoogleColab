"""
Base class untuk semua parser tagihan bank.
"""

import re
import io
import pikepdf
import pdfplumber
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BillingData:
    card_id: str
    bank: str
    last4: str
    billing_date: Optional[str] = None       # YYYY-MM-DD
    due_date: Optional[str] = None           # YYYY-MM-DD
    total_balance: Optional[int] = None      # Total tagihan (Rp)
    minimum_payment: Optional[int] = None    # Minimum payment (Rp)
    credit_limit: Optional[int] = None
    available_limit: Optional[int] = None
    interest_charged: Optional[int] = None
    is_estimated: bool = False               # True = angka estimasi, bukan dari PDF
    parse_errors: list = field(default_factory=list)


class BaseParser:
    """
    Subclass wajib override: `extract(text) -> BillingData`
    """

    card_id: str = ""
    bank: str = ""
    last4: str = ""

    def parse(self, pdf_bytes: bytes, password: str = "") -> BillingData:
        text = self._extract_text(pdf_bytes, password)
        if text is None:
            data = BillingData(card_id=self.card_id, bank=self.bank, last4=self.last4)
            data.parse_errors.append("Gagal membuka PDF — periksa password")
            return data
        return self.extract(text)

    def extract(self, text: str) -> BillingData:
        raise NotImplementedError

    def _extract_text(self, pdf_bytes: bytes, password: str = "") -> Optional[str]:
        try:
            pdf_io = io.BytesIO(pdf_bytes)
            if password:
                with pikepdf.open(pdf_io, password=password) as pdf:
                    out = io.BytesIO()
                    pdf.save(out)
                    out.seek(0)
                    pdf_io = out
            pdf_io.seek(0)
            with pdfplumber.open(pdf_io) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages)
        except Exception as e:
            return None

    # ── Helper regex ──────────────────────────────────────────────────────────

    def _find_amount(self, text: str, *patterns) -> Optional[int]:
        """Cari angka rupiah dari beberapa pola regex, return integer atau None."""
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                raw = m.group(1).replace(".", "").replace(",", "").strip()
                try:
                    return int(raw)
                except ValueError:
                    continue
        return None

    def _find_date(self, text: str, *patterns) -> Optional[str]:
        """Cari tanggal, kembalikan dalam format YYYY-MM-DD."""
        month_map = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "mei": "05", "may": "05", "jun": "06", "jul": "07",
            "agu": "08", "aug": "08", "sep": "09", "okt": "10",
            "oct": "10", "nov": "11", "des": "12", "dec": "12",
        }
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                groups = m.groups()
                try:
                    if len(groups) == 3:
                        d, mo, y = groups
                        mo = mo.strip().lower()[:3]
                        mo = month_map.get(mo, mo.zfill(2))
                        y = y.strip()
                        if len(y) == 2:
                            y = "20" + y
                        return f"{y}-{mo}-{d.zfill(2)}"
                except Exception:
                    continue
        return None
