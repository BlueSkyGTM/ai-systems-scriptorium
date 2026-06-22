# Exercise: Comprehensions and Generators

**Goal:** Build a script that constructs a list comprehension and a generator expression over the same data, asserts they produce equal results, demonstrates the memory difference using `sys.getsizeof`, and exits 0.

**Why:** Every data-prep pipeline in production chooses between materializing a sequence and streaming it. Knowing the cost of each choice, and being able to confirm it with a measurement, is the skill that prevents silent OOM failures when a corpus scales past available RAM.

## Steps

1. Import only standard library modules:

   ```python
   import sys
   ```

2. Build the same transformation as both a list comprehension and a generator expression over a range of 10 million integers:

   ```python
   n = 10_000_000
   eager = [x * x for x in range(n)]
   lazy  = (x * x for x in range(n))
   ```

3. Assert the generator produces the same values as the list. Consume the generator into a list for comparison, then check equality:

   ```python
   lazy_list = list(lazy)
   assert eager == lazy_list, "comprehension and generator must produce equal results"
   ```

4. Measure the size of the materialized list versus a fresh generator object. Create a second generator (the first is now exhausted) to measure its object size:

   ```python
   lazy2       = (x * x for x in range(n))
   list_bytes  = sys.getsizeof(eager)
   gen_bytes   = sys.getsizeof(lazy2)
   ```

5. Assert the generator object is far smaller than the list. A factor of 1000x is a safe floor:

   ```python
   assert gen_bytes * 1000 < list_bytes, (
       f"generator object ({gen_bytes} B) must be far smaller than list ({list_bytes} B)"
   )
   ```

6. Print a structured comparison and confirm the script exits 0:

   ```python
   print(f"[PASS] values match: {len(eager):,} items verified equal")
   print(f"[PASS] list size:      {list_bytes:>12,} bytes")
   print(f"[PASS] generator size: {gen_bytes:>12,} bytes")
   print(f"[PASS] ratio:          {list_bytes // gen_bytes:,}x smaller")
   ```

## Done When

All three assertions pass, the four `[PASS]` lines print, and the script exits with code 0. Run it with:

```sh
python comprehensions_and_generators.py
```

No external dependencies. Standard library only.

## Stretch

Add a `yield` function that produces the same squares sequence and assert its output matches the comprehension result. Then add a dict comprehension that maps each integer from 0 to 9 to its square, and a set comprehension that collects only the even squares from that dict. Print both results and confirm the set contains no odd values with an assertion.

```python
def squares_gen(n: int):
    for x in range(n):
        yield x * x

assert list(squares_gen(10)) == [x * x for x in range(10)], \
    "yield function must match the comprehension"

square_map  = {x: x * x for x in range(10)}
even_squares = {v for v in square_map.values() if v % 2 == 0}

assert all(v % 2 == 0 for v in even_squares), "set must contain only even squares"
print(f"[STRETCH] square map:   {square_map}")
print(f"[STRETCH] even squares: {sorted(even_squares)}")
```
