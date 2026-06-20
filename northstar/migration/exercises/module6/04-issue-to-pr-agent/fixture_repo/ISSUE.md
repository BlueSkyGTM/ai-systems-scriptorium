# add() returns the wrong sum

`calculator.add` is off by one. `add(2, 3)` returns `6` but should return `5`.
The test suite catches it.

file: calculator.py

## Steps to reproduce

```
python -m pytest -q   # test_add fails
```

## Expected

`add(a, b)` returns `a + b`.
