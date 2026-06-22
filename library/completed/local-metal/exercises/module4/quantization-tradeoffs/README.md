# Exercise: Quantization Tradeoffs

**Goal:** Build `vram_fit.py` (stdlib only): a planning script that encodes a model's parameter
count and a quantization's bits-per-weight as constants, estimates the model's VRAM footprint,
adds a context overhead allowance, and prints whether the model FITS or SPILLS against your
card's VRAM budget.

**Why:** Choosing the wrong quantization means either running the model across the system bus
(paying a 10x to 50x speed penalty) or leaving quality on the table. A checked script that
computes the fit before you pull a multi-gigabyte model surfaces a bad choice in seconds
instead of after a long download.

## Steps

1. Create `exercises/module4/quantization-tradeoffs/vram_fit.py`.

2. Add the top-of-file constants. These are your inputs; edit the values to match the model
   and card you are planning for.

   ```python
   # --- Budget constants (edit these to match your plan) ---

   PARAMS_B: float = 32.0        # model parameter count in billions
   VRAM_GB: float = 16.0         # card's total VRAM in GB
   CONTEXT_OVERHEAD_GB: float = 2.0  # KV cache + compute buffers (estimate)

   BITS_PER_WEIGHT: dict = {
       "Q4_K_M": 4.9,
       "Q8_0":   8.5,
       "F16":   16.0,
   }

   QUANT = "Q4_K_M"  # the level you are evaluating
   ```

3. Add the size calculation. Convert parameter count and bits-per-weight to a gigabyte estimate.

   ```python
   # --- Derived values ---

   bits = BITS_PER_WEIGHT[QUANT]
   size_gb = PARAMS_B * 1e9 * bits / 8 / 1e9   # params × bits ÷ 8 = bytes; ÷ 1e9 = GB
   total_needed_gb = size_gb + CONTEXT_OVERHEAD_GB
   ```

4. Add the verdict. Print the computed size and whether the model fits.

   ```python
   print(f"Model:          {PARAMS_B:.0f}B at {QUANT}")
   print(f"Estimated size: {size_gb:.1f} GB")
   print(f"With overhead:  {total_needed_gb:.1f} GB  (context/buffers: {CONTEXT_OVERHEAD_GB} GB)")
   print(f"Card VRAM:      {VRAM_GB:.0f} GB")
   print()

   if total_needed_gb <= VRAM_GB:
       headroom = VRAM_GB - total_needed_gb
       print(f"FITS  ({headroom:.1f} GB headroom)")
   else:
       shortfall = total_needed_gb - VRAM_GB
       print(f"SPILLS  ({shortfall:.1f} GB over budget)")
   ```

5. Run the script from the exercise directory:

   ```
   python vram_fit.py
   ```

   Try it first with `PARAMS_B = 32.0` and `QUANT = "Q4_K_M"`. Then switch to `QUANT = "F16"`
   and observe the change.

## Done When

`python vram_fit.py` exits 0, prints the estimated model size in GB, and prints either `FITS`
(with headroom in GB) or `SPILLS` (with the shortfall in GB). Both are valid outcomes; SPILLS
is information, not a crash.

## Expected Output Shape

With `PARAMS_B = 14.0`, `QUANT = "Q4_K_M"`, `VRAM_GB = 16.0`, `CONTEXT_OVERHEAD_GB = 2.0`:

```
Model:          14B at Q4_K_M
Estimated size: 8.6 GB
With overhead:  10.6 GB  (context/buffers: 2.0 GB)
Card VRAM:      16 GB

FITS  (5.4 GB headroom)
```

With `PARAMS_B = 32.0`, `QUANT = "Q4_K_M"`, `VRAM_GB = 16.0`, `CONTEXT_OVERHEAD_GB = 2.0`:

```
Model:          32B at Q4_K_M
Estimated size: 19.6 GB
With overhead:  21.6 GB  (context/buffers: 2.0 GB)
Card VRAM:      16 GB

SPILLS  (5.6 GB over budget)
```

## Stretch

Loop over all three quantization levels in `BITS_PER_WEIGHT` and print a verdict for each.
Which levels fit a 32B model on a 16 GB card? Which fit a 14B model? Record the break-even
quantization for each model in a comment at the top of the file.
