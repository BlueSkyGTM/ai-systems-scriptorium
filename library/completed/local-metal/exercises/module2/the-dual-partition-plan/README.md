# Exercise: The Dual-Partition Plan

**Goal:** Build `partition_plan.py` (stdlib only): a planning script that encodes your NVMe
budget as constants, computes the Linux partition size, asserts it leaves enough room for your
model storage plus a safety margin, and prints the split.

**Why:** Partitioning is not easily undone. Encoding the budget as checked constants before you
touch the partitioner surfaces a bad split immediately, at the cost of running a script rather
than at the cost of a reinstall.

## Steps

1. Create `exercises/module2/the-dual-partition-plan/partition_plan.py`.

2. Add the top-of-file constants. These are your inputs; edit the values to match your
   actual plan.

   ```python
   # --- Budget constants (edit these to match your plan) ---

   TOTAL_NVME_GB: int = 2000          # physical drive capacity (GB)
   WINDOWS_RESERVE_GB: int = 500      # Windows OS + games + driver cache
   OVERHEAD_GB: int = 70              # Linux OS, CUDA toolkit, Docker images, swap

   MODEL_COUNT: int = 4               # number of models to keep on disk simultaneously
   AVG_MODEL_GB: float = 10.0         # average on-disk size per model (GB)

   SAFETY_MARGIN_GB: int = 50         # minimum free space to leave after model budget
   ```

3. Add the derived calculations. Compute the Linux partition size and the headroom left after
   model storage.

   ```python
   # --- Derived values ---

   linux_total_gb: float = TOTAL_NVME_GB - WINDOWS_RESERVE_GB - OVERHEAD_GB
   model_budget_gb: float = MODEL_COUNT * AVG_MODEL_GB
   headroom_gb: float = linux_total_gb - model_budget_gb - SAFETY_MARGIN_GB
   ```

4. Add the assertion. The script must exit 1 with a clear message when the budget does not
   fit; it must exit 0 when it does.

   ```python
   import sys

   if headroom_gb < 0:
       print(
           f"FAIL: Linux partition ({linux_total_gb:.0f} GB) is too small. "
           f"Model budget ({model_budget_gb:.0f} GB) + safety margin ({SAFETY_MARGIN_GB} GB) "
           f"requires {model_budget_gb + SAFETY_MARGIN_GB:.0f} GB; "
           f"shortfall is {abs(headroom_gb):.0f} GB.",
           file=sys.stderr,
       )
       sys.exit(1)
   ```

5. Print the split summary on success.

   ```python
   print(f"Drive split plan")
   print(f"  Total NVMe:        {TOTAL_NVME_GB:>6} GB")
   print(f"  Windows partition: {WINDOWS_RESERVE_GB:>6} GB")
   print(f"  Linux partition:   {linux_total_gb:>6.0f} GB")
   print(f"    OS + tools:      {OVERHEAD_GB:>6} GB")
   print(f"    Model storage:   {model_budget_gb:>6.0f} GB  ({MODEL_COUNT} models × {AVG_MODEL_GB:.0f} GB each)")
   print(f"    Headroom:        {headroom_gb:>6.0f} GB  (safety margin: {SAFETY_MARGIN_GB} GB)")
   print("Assertion passed: Linux partition fits the model budget.")
   ```

6. Run the script from the exercise directory:

   ```
   python partition_plan.py
   ```

   It should exit 0 and print the split. Then deliberately break the budget (for example,
   set `MODEL_COUNT = 40`) and confirm it exits 1 with a specific failure message.

## Done When

`python partition_plan.py` exits 0 and prints the split summary when the budget fits.
It exits 1 with a message naming the shortfall (in GB) when the Linux partition is too small
for the model budget plus the safety margin.

## Expected Output Shape

```
Drive split plan
  Total NVMe:          2000 GB
  Windows partition:    500 GB
  Linux partition:     1430 GB
    OS + tools:          70 GB
    Model storage:       40 GB  (4 models × 10 GB each)
    Headroom:          1340 GB  (safety margin: 50 GB)
Assertion passed: Linux partition fits the model budget.
```

Example failure output (with `MODEL_COUNT = 200`):

```
FAIL: Linux partition (1430 GB) is too small. Model budget (2000 GB) + safety margin (50 GB) requires 2050 GB; shortfall is 620 GB.
```

## Stretch

Model weights come in multiple quantizations. A 14B model at Q4 is roughly 9 GB; at Q8 it is
roughly 15 GB; at F16 (full precision) it is roughly 28 GB. Extend `partition_plan.py` to
accept a `QUANTIZATION` constant (`"Q4"`, `"Q8"`, or `"F16"`) and a `BASE_MODEL_PARAMS_B`
(parameter count in billions). Compute `AVG_MODEL_GB` from those two inputs rather than
setting it directly. Re-run the assertion against your actual model targets. How much of the
Linux partition does a four-model Q8 library consume compared to a four-model Q4 library?
