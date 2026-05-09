"""
conftest.py — Shared pytest fixtures (auto-generated)
Module: class_grade

Each class gets a module-scoped fixture with correct constructor arguments.
Import path: pytest discovers this automatically when placed alongside test file.
"""

import pytest
from class_grade import Student

# =============================================================================
# Class fixtures — constructor args derived from __init__ type hints
# =============================================================================

@pytest.fixture
def student_instance():
    """
    Fresh Student for each test.
    Constructor: Student(name, rollno)
    """
    return Student(name="hello", rollno="test_value")


@pytest.fixture
def student_instance_alt():
    """
    Alternate Student instance with different constructor values.
    Useful for comparison / equality tests.
    """
    return Student(name="world", rollno="other_value")

