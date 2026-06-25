# Exercise: The Graded Result

## Goal

Run the grader and the oracle, and confirm both directions: the fix passes, the broken
pipeline fails.

## Why

A rubric that cannot fail is decoration. The negative case, where the broken pipeline is
graded and fails, is what makes a green grade on your fix mean something.

## What You Are Building

Not new code: a verification run that proves the grader has teeth and your fix clears all
six criteria.

## Steps

1. Grade your fix: `python rubric.py ; echo $?` should print `0` with all six criteria checked.

2. Grade the broken pipeline: `python rubric.py --pipeline broken_pipeline ; echo $?` should
   print `1`. That is the grader's teeth.

3. Run the oracle: `python smoke.py`. It runs the broken pipeline (diagnose lights up), the
   fixed pipeline (diagnose dark, stale run raises), and the grader both directions. It exits
   `0` only if every assertion holds.

4. Run the suite together:

   ```bash
   python smoke.py && python -m pytest tests/ -q && python rubric.py
   ```

5. If smoke passes but rubric fails (or vice versa), reconcile the two before you call it done.
