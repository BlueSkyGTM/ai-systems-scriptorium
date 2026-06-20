"""A tiny module with one seeded bug. The agent's job is to fix add()."""


def add(a, b):
    # BUG: off-by-one. add(2, 3) returns 6, not 5.
    return a + b + 1


def sub(a, b):
    return a - b
