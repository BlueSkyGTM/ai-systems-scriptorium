# Exercise: The Cost Wall and the Rig

**Goal:** Build `breakeven.py`, a stdlib-only Python cost model that tells you the exact month when
cumulative local costs drop below cumulative frontier spending.

**Why:** Every hardware investment case rests on a break-even date. Knowing yours before you buy is
the difference between an engineering decision and a purchase you regret. This model is also the
foundation for the routing-layer analysis in Module 5: once you know your break-even, you know how
aggressively to route traffic local.

## Steps

1. Create `exercises/module1/the-cost-wall-and-the-rig/breakeven.py`.

2. At the top of the file, define these constants (the reader edits them to match their setup):

   ```python
   # --- edit these to match your setup ---

   # Monthly token volume (in millions of tokens)
   MONTHLY_INPUT_MTOK  = 5.0    # input tokens per month
   MONTHLY_OUTPUT_MTOK = 2.0    # output tokens per month

   # Frontier pricing (USD per million tokens)
   # Source: https://platform.claude.com/docs/en/about-claude/pricing (verified 2026-06-21)
   # These rates change; confirm before relying on them.
   FRONTIER_INPUT_PER_MTOK  = 3.00   # Claude Sonnet 4.6 input rate
   FRONTIER_OUTPUT_PER_MTOK = 15.00  # Claude Sonnet 4.6 output rate

   # Rig cost basis (USD): one-time capital cost
   # Source: Cthulhu SPEC BOM: Ryzen 7 7700X + RTX 4060 Ti 16GB + 64GB DDR5-6000 + 2TB NVMe
   #         + Fractal Ridge + SF750 + Express ProBuild. Open-box prices vary on the day.
   RIG_UPFRONT_COST = 1_567.50   # midpoint of the $1,450-$1,685 SPEC range

   # Monthly electricity cost (USD) for local inference load
   MONTHLY_POWER_COST = 12.00
   ```

3. Write a `monthly_frontier_cost()` function that returns the monthly frontier spend:

   ```python
   def monthly_frontier_cost() -> float:
       """Return monthly spend on the frontier API at the configured volume."""
       return (
           MONTHLY_INPUT_MTOK  * FRONTIER_INPUT_PER_MTOK +
           MONTHLY_OUTPUT_MTOK * FRONTIER_OUTPUT_PER_MTOK
       )
   ```

4. Write a `find_breakeven(max_months: int = 120) -> int` function that walks month by month,
   tracking cumulative costs on each side, and returns the first month where cumulative local cost
   is less than cumulative frontier cost:

   ```python
   def find_breakeven(max_months: int = 120) -> int:
       """Return the month when cumulative local cost first beats cumulative frontier cost.

       Local cumulative = one-time hardware + (month * monthly power).
       Frontier cumulative = month * monthly frontier spend.

       Raises ValueError if no break-even occurs within max_months.
       """
       f_monthly = monthly_frontier_cost()

       for month in range(1, max_months + 1):
           frontier_total = month * f_monthly
           local_total    = RIG_UPFRONT_COST + month * MONTHLY_POWER_COST
           if local_total < frontier_total:
               return month

       raise ValueError(
           f"No break-even within {max_months} months. "
           "Check your volume and cost constants; increase token volume or frontier rate."
       )
   ```

5. Add a `main()` block that prints a summary and asserts the break-even is finite and positive:

   ```python
   if __name__ == "__main__":
       f_monthly = monthly_frontier_cost()
       month     = find_breakeven()

       print(f"Monthly frontier cost:  ${f_monthly:>8.2f}")
       print(f"Monthly local cost:     ${MONTHLY_POWER_COST:>8.2f}  (electricity only, after hardware)")
       print(f"Upfront hardware cost:  ${RIG_UPFRONT_COST:>8.2f}  (one-time)")
       print(f"Break-even month:       {month}")

       assert month > 0, "Break-even must be a positive month"
       print("assertion passed: break-even is finite and positive")
   ```

6. Run `python breakeven.py` from the exercise directory. Confirm it exits 0 and prints the
   break-even month.

## Done When

`python breakeven.py` exits 0, prints a break-even month, and the assertion passes. No third-party
packages required: stdlib only. The month printed must be positive and less than 120.

Expected output shape (numbers vary with your constants):

```
Monthly frontier cost:  $   45.00
Monthly local cost:     $   12.00  (electricity only, after hardware)
Upfront hardware cost:  $ 1567.50  (one-time)
Break-even month:       48
assertion passed: break-even is finite and positive
```

## Stretch

Add a second frontier tier to the model. Define `FRONTIER_PREMIUM_INPUT_PER_MTOK` and
`FRONTIER_PREMIUM_OUTPUT_PER_MTOK` (e.g., Claude Opus 4.8 at $5.00/$25.00 per MTok), and a
fraction `PREMIUM_FRACTION` (0.0-1.0) for what share of your volume uses the premium tier.
Update `monthly_frontier_cost()` to blend both tiers, and print both the blended frontier cost
and the new break-even month. How much does routing even 10% of traffic to Opus pull the date in?
