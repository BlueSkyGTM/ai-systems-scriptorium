# Answers Log

Copy this file to `answers-log.md` and complete all five entries.
The worked example below shows the expected format for one entry.
Remove this instruction block before running the validator.

---

<!-- WORKED EXAMPLE — read this, then fill in A1-A5 below -->

## Example Entry (Question: "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong.")

### Step 1: Decompose

**Literal parse:** The action noun is "advocated for a technical decision" and the constraint is that the decision was wrong. The candidate picks the story.

**Signal category:** Ownership (secondary: Judgment Under Uncertainty)

**Primary hypothesis:** The interviewer is trying to determine whether the candidate takes genuine accountability for outcomes they drove, including the ones they got wrong.

### Step 2: Identify the Signal

**Restated hypothesis:** The answer must show that the candidate owned the original call, owned the correction, and applied a structural lesson from the failure.

**Evidence required:**
- A specific technical decision the candidate personally advocated for (not "the team decided")
- A measurable or concrete failure signal (not "it did not work out")
- A clear account of how the candidate corrected course publicly
- A named change in practice afterward

### Step 3: Construct the Answer

I pushed hard to replace our retrieval pipeline with a pure long-context approach in two design reviews. The argument was that newer models could handle our corpus in-context without the retrieval latency overhead. The team committed a quarter to the migration partly on my conviction.

When I ran the eval before full cutover, quality matched our baseline, but cost was running four times my projection. The cache hit rates collapsed under our update frequency, and p95 latency doubled. My first instinct was to tune for two more weeks. After two weeks of marginal gains, I stopped and wrote a one-page memo stating plainly that my recommendation was wrong on the economics. I presented the hybrid alternative to the same audience: long-context for small static corpora, retrieval for everything else.

We kept the hybrid and salvaged about 60% of the migration work. The postmortem produced one team rule we still use: any architecture pitch must include a cost model under realistic update patterns, not peak conditions.

### Step 4: Stress-Test

Could a weak candidate give this answer? No. The specifics that block a weak candidate: "cost ran four times my projection," "cache hit rates collapsed under update frequency," "two weeks of marginal gains before I stopped," "one-page memo stating plainly the recommendation was wrong." A weak candidate gives "I learned to think about costs" and stops there.

**Revision:** none required; the answer passes the stress test.

### Scores

**Specificity:** strong
**Structure:** strong
**Completeness:** strong

---

## A1

### Step 1: Decompose

**Literal parse:** TODO

**Signal category:** TODO

**Primary hypothesis:** TODO

### Step 2: Identify the Signal

**Restated hypothesis:** TODO

**Evidence required:** TODO

### Step 3: Construct the Answer

TODO

### Step 4: Stress-Test

TODO

### Scores

**Specificity:** TODO
**Structure:** TODO
**Completeness:** TODO

---

## A2

### Step 1: Decompose

**Literal parse:** TODO

**Signal category:** TODO

**Primary hypothesis:** TODO

### Step 2: Identify the Signal

**Restated hypothesis:** TODO

**Evidence required:** TODO

### Step 3: Construct the Answer

TODO

### Step 4: Stress-Test

TODO

### Scores

**Specificity:** TODO
**Structure:** TODO
**Completeness:** TODO

---

## A3

### Step 1: Decompose

**Literal parse:** TODO

**Signal category:** TODO

**Primary hypothesis:** TODO

### Step 2: Identify the Signal

**Restated hypothesis:** TODO

**Evidence required:** TODO

### Step 3: Construct the Answer

TODO

### Step 4: Stress-Test

TODO

### Scores

**Specificity:** TODO
**Structure:** TODO
**Completeness:** TODO

---

## A4

### Step 1: Decompose

**Literal parse:** TODO

**Signal category:** TODO

**Primary hypothesis:** TODO

### Step 2: Identify the Signal

**Restated hypothesis:** TODO

**Evidence required:** TODO

### Step 3: Construct the Answer

TODO

### Step 4: Stress-Test

TODO

### Scores

**Specificity:** TODO
**Structure:** TODO
**Completeness:** TODO

---

## A5

### Step 1: Decompose

**Literal parse:** TODO

**Signal category:** TODO

**Primary hypothesis:** TODO

### Step 2: Identify the Signal

**Restated hypothesis:** TODO

**Evidence required:** TODO

### Step 3: Construct the Answer

TODO

### Step 4: Stress-Test

TODO

### Scores

**Specificity:** TODO
**Structure:** TODO
**Completeness:** TODO
