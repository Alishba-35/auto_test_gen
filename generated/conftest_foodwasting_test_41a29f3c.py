"""
conftest.py — Shared pytest fixtures (auto-generated)
Module: foodwasting_test

Each class gets a module-scoped fixture with correct constructor arguments.
Import path: pytest discovers this automatically when placed alongside test file.
"""

import pytest
from foodwasting_test import TestFoodWasteApp

# =============================================================================
# Class fixtures — constructor args derived from __init__ type hints
# =============================================================================

@pytest.fixture
def testfoodwasteapp_instance():
    """
    Fresh TestFoodWasteApp for each test.
    Constructor: TestFoodWasteApp()
    """
    return TestFoodWasteApp()


@pytest.fixture
def testfoodwasteapp_instance_alt():
    """
    Alternate TestFoodWasteApp instance with different constructor values.
    Useful for comparison / equality tests.
    """
    return TestFoodWasteApp()

