from .base import BaseParser, BillingData


class BNIParser(BaseParser):
    def __init__(self, card_id: str, last4: str, product: str):
        self.card_id = card_id
        self.bank = "BNI"
        self.last4 = last4
        self.product = product

    def extract(self, text: str) -> BillingData:
        data = BillingData(card_id=self.card_id, bank=self.bank, last4=self.last4)

        data.total_balance = self._find_amount(
            text,
            r"Total\s+Tagihan[^\d]*?([\d.,]+)",
            r"Jumlah\s+Tagihan[^\d]*?([\d.,]+)",
            r"Saldo\s+Tagihan[^\d]*?([\d.,]+)",
        )
        data.minimum_payment = self._find_amount(
            text,
            r"Pembayaran\s+Minimum[^\d]*?([\d.,]+)",
            r"Minimum\s+Payment[^\d]*?([\d.,]+)",
        )
        data.due_date = self._find_date(
            text,
            r"Jatuh\s+Tempo\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
            r"Tanggal\s+Jatuh\s+Tempo\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )
        data.billing_date = self._find_date(
            text,
            r"Tanggal\s+Tagihan\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
            r"Tanggal\s+Cetak\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )

        if data.total_balance is None:
            data.parse_errors.append(f"total_balance tidak ditemukan di PDF BNI {self.last4}")

        return data
