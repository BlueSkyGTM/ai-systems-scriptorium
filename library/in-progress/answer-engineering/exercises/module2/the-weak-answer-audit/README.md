# Exercise: The Weak Answer Audit

**Goal:** Create `exercises/prep/audit-log.md` by running the systematic pitfalls audit on two of your own answers from `answers-log.md`, naming which failure modes each answer risks, checking it against both the basic bar and the staff bar, and writing a revised version of the weakest sentence.

**Why:** The stress test in Module 1 asks "could a weak candidate give this answer?" The audit goes further: it names the specific pitfall category that would let a weak candidate through, checks whether you have cleared the senior bar, and then raises the bar to staff level. The gap between a passing answer and a strong one is almost always one of these named failure modes. Naming it before the interviewer does is the skill.

## Steps

1. Copy `exercises/prep/audit-log.template.md` to `exercises/prep/audit-log.md`. Read the worked example entry; your entries follow the same format.

2. Choose two answers from `exercises/prep/answers-log.md`. Pick ones you rated `partial` or `weak` on at least one score dimension; the audit does the most work there.

3. For each answer, work through the four audit fields in order:

   - **Pitfalls present:** name every pitfall category from the lesson that this answer risks. At minimum, check it against: vague ownership ("we built" instead of "I built"), buried result (the outcome appears after the ninety-second mark), missing failure signal (no concrete thing went wrong, or the failure is described in abstract terms), and no structural lesson (the learning is stated but no named change in practice resulted). Name which are present and which are absent.

   - **Basic bar verdict:** one sentence. Does the answer pass the basic bar? The basic bar is: a weak candidate could not have given this exact answer. State what makes it pass (or what specific detail is still missing that would let a weak candidate through).

   - **Staff bar verdict:** one sentence. Does the answer pass the staff bar? The staff bar requires an organizational artifact: a process, a standard, a pattern, or a platform decision that changed what other engineers could do. Name whether the artifact is present or absent, and what it is (or what it should be).

   - **Revised sentence:** take the weakest sentence in the answer and rewrite it. Paste the original sentence first, then your revision. The revision must address a specific named pitfall, not just sharpen the prose.

4. After completing both entries, read them side by side. If you see a pattern in which pitfalls recur, note it at the bottom of the file under a `## Pattern` heading. The pattern is the most useful output of this exercise.

## Done When

Open `exercises/prep/` and run:

```
python check_prep.py --module 2
```

The validator exits 0 when `audit-log.md` contains at least two `### AL<n>` entries, each with a `**Pitfalls present:**`, `**Basic bar verdict:**`, `**Staff bar verdict:**`, and `**Revised sentence:**` field filled in and no placeholder text. It exits 1 if any field is empty, missing, or contains a placeholder.

## Stretch

Run the audit on the two answers you rated `strong` in `answers-log.md`. The staff bar check is the useful one here: even a strong basic-bar answer may not contain the organizational artifact. If it does not, write what the artifact would be, and whether it would have been honest to include it in the original.
