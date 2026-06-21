# Exercise: The Full Design Under Pressure

**Goal:** Run a timed 45-minute full SPIDER design on your chosen prompt, then write the
**Audit verdict:** field of your entry in `exercises/prep/systems-design-log.md` and run the
validator to confirm the entry is complete.

**Why:** All prior exercises in this module built your design in layers, with time to reflect
between each step. An interview gives you 45 minutes and no pause. This exercise closes the
loop: you run the full design under real time pressure, then audit your own performance against
the weak-design red flags. The audit is what distinguishes a prepared candidate from one who
practiced without feedback. The validator exit confirms the entry is structurally complete.

## Steps

1. Before starting the timed run, open `exercises/prep/systems-design-log.md` and read your
   existing entry -- **Prompt:** through **Evaluation:**. The prompt is set. You are not
   re-choosing. The timed run is a dress rehearsal of the entire design from the S phase forward.

2. Set a timer for 45 minutes. Run the full SPIDER framework out loud or on paper as if you are
   in the interview:
   - S (5 min): Scope and clarify. Ask the six questions; answer them from your **Scope:** field
     or by assumption.
   - P (3 min): Prioritize. State your top-two priorities out loud.
   - I (10 min): Draw the architecture. Name every component.
   - D (15 min): Deep dive two or three critical paths. Pick the paths your **Scope:** makes
     most important.
   - E (5 min): Evaluation and observability. State metrics and monitoring approach.
   - R (5 min): Reliability and scale. State failure modes and degradation strategy.

   Do not stop the timer if you get stuck. Keep talking. An interviewer who sees you stuck and
   talking through the stuck point scores you higher than an interviewer who sees silence.

3. After the timer, debrief yourself. Do not edit your existing log fields yet.
   Ask: which weak-design red flags did you risk in the timed run?

   The named red flags from the lesson are:
   - Skipping the data pipeline (Pitfall 1)
   - One-size-fits-all model selection (Pitfall 2)
   - Ignoring the evaluation layer (Pitfall 3)
   - Post-retrieval tenant filtering (Pitfall 4)
   - No graceful degradation (Pitfall 5)
   - Monologuing without interaction (Pitfall 11)
   - Not managing time (Pitfall 16)
   - Ignoring hallucination risk (Pitfall 19)
   - Security as an afterthought (Pitfall 20)

   Name the ones you risked. Be specific: "I skipped the data pipeline because I spent 12
   minutes on the architecture and ran out of time for ingestion" is a diagnosis. "I could have
   done the data pipeline better" is not.

4. Write the **Audit verdict:** field in `exercises/prep/systems-design-log.md`. The field must
   include:
   - Which pitfalls from the list above you risked in the timed run (name them by number and
     title)
   - Which of those you addressed in your existing log fields (from the prior exercises) and
     which you left thin in the timed run
   - The one specific change you would make if you had five more minutes (name the component,
     the phase, or the argument; not a general improvement)

5. From `exercises/prep/`, run:

   ```
   python check_prep.py --module 5
   ```

   The validator checks that all eight fields in your `systems-design-log.md` entry are filled
   in and free of placeholder text, and that the M1, M2, and M3 dossier artifacts are also
   complete. Exit 0 means the full Module 5 gate is cleared.

## Done When

```
python check_prep.py --module 5
```

exits 0 from `exercises/prep/`. This requires both that your `systems-design-log.md` entry is
complete (all eight fields filled, no placeholder text) and that all prior dossier artifacts
(M1, M2, M3) are also complete.

## Stretch

Run the timed design a second time, one week later, on a different prompt from the list in the
first exercise. Compare the two **Audit verdict:** fields. Which pitfalls recur? A pitfall that
appears in both runs is a systematic gap, not a one-time miss. Add a note to your second entry
naming the systematic gap and one drill to close it.
