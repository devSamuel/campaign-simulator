from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class Budget(ValueObject):
    amount: Decimal
    currency: str  # ISO 4217 code, e.g. "USD"

    def __post_init__(self) -> None:
        if self.amount <= Decimal("0"):
            raise ValueError(f"Budget amount must be positive, got {self.amount}")
        if len(self.currency) != 3:
            raise ValueError(f"Currency must be a 3-letter ISO 4217 code, got '{self.currency}'")

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency.upper()}"
