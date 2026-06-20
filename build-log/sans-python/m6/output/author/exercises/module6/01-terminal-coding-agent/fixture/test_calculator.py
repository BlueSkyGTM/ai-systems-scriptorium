"""The acceptance test. It fails until the agent fixes calculator.add."""

from calculator import add


def test_add():
    assert add(2, 3) == 5


def test_add_zero():
    assert add(0, 0) == 0
