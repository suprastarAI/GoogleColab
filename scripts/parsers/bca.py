import re
from .base import BaseParser, BillingData


class BCAParser(BaseParser):
    card_id = "bca"
    bank = "BCA"
    last4 = "multi"

    def extract(self, text: str) -> BillingData:
        data = BillingData(card_id=self.card_id, bank=self.bank, last4=self.last4)

        data.total_balance = self._find_amount(
            text,
            r"Total\s+Tagihan[^\d]*?([\d.,]+)",
            r"TOTAL\s+TAGIHAN[^\d]*?([\d.,]+)",
            r"Jumlah\s+Tagihan[^\d]*?([\d.,]+)",
        )
        data.minimum_payment = self._find_amount(
            text,
            r"Pembayaran\s+Minimum[^\d]*?([\d.,]+)",
            r"Minimum\s+Payment[^\d]*?([\d.,]+)",
            r"PEMBAYARAN\s+MINIMUM[^\d]*?([\d.,]+)",
        )
        data.credit_limit = self._find_amount(
            text,
            r"Limit\s+Kredit[^\d]*?([\d.,]+)",
            r"Credit\s+Limit[^\d]*?([\d.,]+)",
        )
        data.available_limit = self._find_amount(
            text,
            r"Limit\s+Tersedia[^\d]*?([\d.,]+)",
            r"Available\s+Limit[^\d]*?([\d.,]+)",
        )
        data.due_date = self._find_date(
            text,
            r"Jatuh\s+Tempo\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
            r"Payment\s+Due\s+Date\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )
        data.billing_date = self._find_date(
            text,
            r"Tanggal\s+Tagihan\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
            r"Statement\s+Date\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )
        data.interest_charged = self._find_amount(
            text,
            r"Bunga[^\d]*?([\d.,]+)",
            r"Finance\s+Charge[^\d]*?([\d.,]+)",
        )

        if data.total_balance is None:
            data.parse_errors.append("total_balance tidak ditemukan di PDF BCA")

        return data
