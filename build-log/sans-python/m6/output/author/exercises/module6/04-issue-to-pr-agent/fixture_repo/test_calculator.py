"""The CI gate for the fixture repo. Fails until add() is fixed.

`smoke.py` runs this via `python -m pytest` as the agent's CI. It uses plain
asserts so it runs under pytest if present and as a script under the stdlib if
not (see the __main__ block) — keeping the smoke path stdlib-only.
"""

from calculator import add, sub


def test_add():
    assert add(2, 3) == 5
    assert add(0, 0) == 0
    assert add(-1, 1) == 0


def test_sub():
    assert sub(5, 3) == 2


if __name__ == "__main__":
    # stdlib fallback so CI works even without pytest installed.
    test_add()
    test_sub()
    print("ok")
