from .base import BaseParser, BillingData


class BSIParser(BaseParser):
    card_id = "bsi_6634"
    bank = "BSI"
    last4 = "6634"

    def extract(self, text: str) -> BillingData:
        data = BillingData(card_id=self.card_id, bank=self.bank, last4=self.last4)

        data.total_balance = self._find_amount(
            text,
            r"Total\s+Tagihan[^\d]*?([\d.,]+)",
            r"Jumlah\s+Tagihan[^\d]*?([\d.,]+)",
        )
        data.minimum_payment = self._find_amount(
            text,
            r"Pembayaran\s+Minimum[^\d]*?([\d.,]+)",
            r"Minimum\s+Payment[^\d]*?([\d.,]+)",
        )
        data.due_date = self._find_date(
            text,
            r"Jatuh\s+Tempo\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )
        data.billing_date = self._find_date(
            text,
            r"Tanggal\s+Tagihan\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )

        if data.total_balance is None:
            data.parse_errors.append("total_balance tidak ditemukan di PDF BSI")

        return data
