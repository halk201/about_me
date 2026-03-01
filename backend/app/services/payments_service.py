from dataclasses import dataclass
from decimal import Decimal

from app.services.ledger_service import LedgerService


@dataclass
class PaymentRecord:
    payment_id: str
    user_id: str
    account_id: str
    amount: Decimal
    kind: str
    status: str


class PaymentsService:
    def __init__(self, ledger: LedgerService) -> None:
        self.ledger = ledger
        self.records: dict[str, PaymentRecord] = {}

    def deposit(self, request_id: str, payment_id: str, user_id: str, account_id: str, amount: Decimal) -> PaymentRecord:
        self.ledger.transfer(request_id, "platform", account_id, amount, f"payment:deposit:{payment_id}")
        rec = PaymentRecord(payment_id, user_id, account_id, amount, "DEPOSIT", "COMPLETED")
        self.records[payment_id] = rec
        return rec

    def withdraw(self, request_id: str, payment_id: str, user_id: str, account_id: str, amount: Decimal) -> PaymentRecord:
        self.ledger.transfer(request_id, account_id, "platform", amount, f"payment:withdraw:{payment_id}")
        rec = PaymentRecord(payment_id, user_id, account_id, amount, "WITHDRAW", "COMPLETED")
        self.records[payment_id] = rec
        return rec
