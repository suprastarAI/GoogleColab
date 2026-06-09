import re
from .base import BaseParser, BillingData


class DBSParser(BaseParser):
    card_id = "dbs_3099"
    bank = "DBS digibank"
    last4 = "3099"

    def extract(self, text: str) -> BillingData:
        data = BillingData(card_id=self.card_id, bank=self.bank, last4=self.last4)

        data.total_balance = self._find_amount(
            text,
            r"Total\s+Amount\s+Due[^\d]*?([\d.,]+)",
            r"Statement\s+Balance[^\d]*?([\d.,]+)",
            r"Tagihan[^\d]*?([\d.,]+)",
        )
        data.minimum_payment = self._find_amount(
            text,
            r"Minimum\s+Payment[^\d]*?([\d.,]+)",
            r"Min(?:imum)?\s+Due[^\d]*?([\d.,]+)",
        )
        data.due_date = self._find_date(
            text,
            r"Payment\s+Due\s+Date\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
            r"Due\s+Date\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )
        data.billing_date = self._find_date(
            text,
            r"Statement\s+Date\D*?(\d{1,2})\s+(\w+)\s+(\d{4})",
        )

        if data.total_balance is None:
            data.parse_errors.append("total_balance tidak ditemukan di PDF DBS")

        return data
