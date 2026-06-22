# Practice Log

Copy this file to `practice-log.md` and complete all two entries.
The worked example below shows the expected format for one entry.
Remove this instruction block before running the validator.

---

<!-- WORKED EXAMPLE: read this, then fill in PL1-PL2 below -->

## Example Entry (Source: A1 from answers-log.md)

### PL1

**2-minute version:** I pushed hard to replace our retrieval pipeline with a pure long-context approach in two design reviews. The argument was that newer models could handle our corpus in-context without retrieval overhead. The team committed a quarter to the migration on my conviction. When I ran the eval before cutover, quality matched but cost ran four times my projection. Cache hit rates collapsed under our update frequency; p95 latency doubled. I spent two weeks trying to tune my way out of it. After marginal gains, I stopped. I wrote a one-page memo stating plainly that my recommendation was wrong on the economics. I proposed a hybrid and presented it to the same audience. We kept it. The postmortem produced one rule: any architecture pitch requires a cost model under realistic update patterns, not peak conditions. I still attach kill criteria to my own proposals because of it. (Timed: 1 min 52 sec)

**30-second version:** I pushed a retrieval-to-long-context migration that failed on cost: four times my projection at realistic update frequency. After two weeks of tuning, I wrote a one-page memo calling the recommendation wrong, proposed a hybrid, and got it approved. The lesson: always attach a kill criterion to your own proposals. (Timed: 28 sec)

**Delivery self-score:** The long version buries the result: the outcome (hybrid approved, 60% of work salvaged) does not appear until 1:40. It should arrive by 1:00. No significant filler words, but "I spent two weeks trying to tune my way out of it" is weak phrasing -- "tune my way out" is vague; revise to "two weeks of marginal gains before I stopped." The thirty-second version correctly collapses to result and learning; it does not retain the Situation and Task framing of the long version. One sentence to cut from the long version: "The argument was that newer models could handle our corpus in-context without retrieval overhead" -- this is context nobody asked for; it can be one phrase.

---

## PL1

**2-minute version:** TODO

**30-second version:** TODO

**Delivery self-score:** TODO

---

## PL2

**2-minute version:** TODO

**30-second version:** TODO

**Delivery self-score:** TODO
