"""
sample_code.py — Demo file for the AST Test Generator
Upload this file to see what tests get generated!
"""

from typing import List, Dict, Optional


# ── Top-level functions ───────────────────────────────────────────────────────

def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def divide(numerator: float, denominator: float) -> float:
    """Divide numerator by denominator.

    Raises:
        ZeroDivisionError: if denominator is zero.
        ValueError: if either argument is negative.
    """
    if denominator == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    if numerator < 0 or denominator < 0:
        raise ValueError("Arguments must be non-negative")
    return numerator / denominator


def reverse_string(text: str) -> str:
    """Return the reversed version of a string."""
    return text[::-1]


def find_max(numbers: List[int]) -> Optional[int]:
    """Return the largest number in a list, or None if empty."""
    if not numbers:
        return None
    return max(numbers)


def greet(name: str, formal: bool = False) -> str:
    """Build a greeting message."""
    prefix = "Dear" if formal else "Hey"
    return f"{prefix} {name}!"


def word_count(text: str) -> Dict[str, int]:
    """Count occurrences of each word in a text."""
    result: Dict[str, int] = {}
    for word in text.lower().split():
        result[word] = result.get(word, 0) + 1
    return result


def is_palindrome(word: str) -> bool:
    """Return True if word reads the same forwards and backwards."""
    cleaned = word.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


# ── Class with methods ────────────────────────────────────────────────────────

class BankAccount:
    """A simple bank account model."""

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self.balance = balance
        self._transactions: List[float] = []

    def deposit(self, amount: float) -> float:
        """Deposit money. Returns new balance.

        Raises:
            ValueError: if amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self._transactions.append(amount)
        return self.balance

    def withdraw(self, amount: float) -> float:
        """Withdraw money. Returns new balance.

        Raises:
            ValueError: if amount is negative or exceeds balance.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self._transactions.append(-amount)
        return self.balance

    def get_statement(self) -> List[float]:
        """Return list of all transactions."""
        return list(self._transactions)

    @staticmethod
    def currency_symbol() -> str:
        """Return the default currency symbol."""
        return "$"

    @classmethod
    def zero_account(cls, owner: str) -> "BankAccount":
        """Create a BankAccount with zero balance."""
        return cls(owner=owner, balance=0.0)
