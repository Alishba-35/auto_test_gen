"""
conftest.py — Shared pytest fixtures (auto-generated)
Module: sample_code

Each class gets a module-scoped fixture with correct constructor arguments.
Import path: pytest discovers this automatically when placed alongside test file.
"""

import pytest
from sample_code import BankAccount

# =============================================================================
# Class fixtures — constructor args derived from __init__ type hints
# =============================================================================

@pytest.fixture
def bankaccount_instance():
    """
    Fresh BankAccount for each test.
    Constructor: BankAccount(owner: str, balance: float)
    """
    return BankAccount(owner="hello", balance=99.9)


@pytest.fixture
def bankaccount_instance_alt():
    """
    Alternate BankAccount instance with different constructor values.
    Useful for comparison / equality tests.
    """
    return BankAccount(owner="world", balance=99.9)