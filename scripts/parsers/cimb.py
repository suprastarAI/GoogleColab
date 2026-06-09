from .base import BaseParser, BillingData


class CIMBParser(BaseParser):
    """Dipakai untuk CIMB 0407, 5614, dan 6174 — beda card_id saat instansiasi."""

    def __init__(self, card_id: str, bank: str, last4: str):
        self.card_id = card_id
        self.bank = bank
        self.last4 = last4

    def extract(self, text: str) -> BillingData:
        data = BillingData(card_id=self.card_id, bank=self.bank, last4=self.last4)

        data.total_balance = self._find_amount(
            text,
            r"Total\s+Tagihan[^\d]*?([\d.,]+)",
            r"Jumlah\s+Tagihan[^\d]*?([\d.,]+)",
            r"Outstanding\s+Balance[^\d]*?([\d.,]+)",
        )
        data.minimum_payment = self._find_amount(
            text,
            r"Pembayaran\s+Minimum[^\d]*?([\d.,]+)",
            r"Minimum\s+Payment[^\d]*?([\d.,]+)",
        )
        data.due_date = self._find_date(
            text,
            r"Jatuh\s+Tempo\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
            r"Due\s+Date\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )
        data.billing_date = self._find_date(
            text,
            r"Tanggal\s+Tagihan\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
            r"Statement\s+Date\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )
        data.interest_charged = self._find_amount(
            text,
            r"Biaya\s+Bunga[^\d]*?([\d.,]+)",
        )

        if data.total_balance is None:
            data.parse_errors.append(f"total_balance tidak ditemukan di PDF CIMB {self.last4}")

        return data
