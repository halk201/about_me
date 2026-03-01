"""Ledger service with idempotent transfer semantics.

In production, back this with PostgreSQL SERIALIZABLE transactions and row-level locks.
"""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from threading import Lock

from app.models.ledger import AccountType, EntryType, LedgerEntry, WalletAccount


class InsufficientFundsError(Exception):
    """Raised when debit account has not enough funds."""


class AccountNotFoundError(Exception):
    """Raised when a requested account does not exist."""


class DuplicateAccountError(Exception):
    """Raised when creating an existing account."""


class InMemoryLedgerRepository:
    """Thread-safe in-memory repository for local development and deterministic tests."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.accounts: dict[str, WalletAccount] = {}
        self.entries: list[LedgerEntry] = []
        self.idempotency: dict[str, dict] = {}

    def create_account(self, account: WalletAccount) -> WalletAccount:
        with self._lock:
            if account.account_id in self.accounts:
                raise DuplicateAccountError("account already exists")
            self.accounts[account.account_id] = account
            return account

    def get_account(self, account_id: str) -> WalletAccount:
        with self._lock:
            if account_id not in self.accounts:
                raise AccountNotFoundError("account not found")
            return self.accounts[account_id]

    def transfer(self, request_id: str, from_account_id: str, to_account_id: str, amount: Decimal, reference: str) -> dict:
        with self._lock:
            if request_id in self.idempotency:
                replay = self.idempotency[request_id].copy()
                replay["idempotent_replay"] = True
                return replay

            debit_acc = self.accounts.get(from_account_id)
            credit_acc = self.accounts.get(to_account_id)
            if debit_acc is None or credit_acc is None:
                raise AccountNotFoundError("account not found")

            if debit_acc.balance < amount:
                raise InsufficientFundsError("insufficient funds")

            debit_acc.balance -= amount
            credit_acc.balance += amount

            self.entries.append(
                LedgerEntry(
                    entry_id=f"{request_id}-d",
                    request_id=request_id,
                    account_id=from_account_id,
                    amount=amount,
                    entry_type=EntryType.DEBIT,
                    reference=reference,
                )
            )
            self.entries.append(
                LedgerEntry(
                    entry_id=f"{request_id}-c",
                    request_id=request_id,
                    account_id=to_account_id,
                    amount=amount,
                    entry_type=EntryType.CREDIT,
                    reference=reference,
                )
            )

            response = {
                "request_id": request_id,
                "from_account_id": from_account_id,
                "to_account_id": to_account_id,
                "amount": amount,
                "from_balance": debit_acc.balance,
                "to_balance": credit_acc.balance,
                "idempotent_replay": False,
            }
            self.idempotency[request_id] = response.copy()
            return response


class LedgerService:
    """Application-level orchestration for wallet operations."""

    def __init__(self, repo: InMemoryLedgerRepository) -> None:
        self.repo = repo

    def create_account(
        self,
        account_id: str,
        user_id: str | None,
        currency: str,
        account_type: str,
        initial_balance: Decimal = Decimal("0"),
    ) -> dict:
        account = WalletAccount(
            account_id=account_id,
            user_id=user_id,
            currency=currency,
            account_type=AccountType(account_type),
            balance=initial_balance,
        )
        return asdict(self.repo.create_account(account))

    def get_balance(self, account_id: str) -> dict:
        account = self.repo.get_account(account_id)
        return {"account_id": account.account_id, "currency": account.currency, "balance": account.balance}

    def transfer(self, request_id: str, from_account_id: str, to_account_id: str, amount: Decimal, reference: str) -> dict:
        return self.repo.transfer(
            request_id=request_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            reference=reference,
        )
