# Exercise: Thinking Out Loud

**Goal:** Create `exercises/prep/practice-log.md` by recording a two-minute and a thirty-second version of two answers out loud, then writing a delivery self-score that names specific problems: filler words, buried results, and whether the short version collapsed correctly.

**Why:** An answer that reads well on paper still fails in the room if you have only rehearsed it silently. The thirty-second question comes without warning; if you have only the long version, you will ramble. One listen-through reveals failures that silent rehearsal hides.

## Steps

1. Copy `exercises/prep/practice-log.template.md` to `exercises/prep/practice-log.md`. Read the worked example entry; your entries follow the same format.

2. Choose two answers from your `exercises/prep/answers-log.md` to use as the source material. You are not writing new answers; you are practicing the delivery of answers you have already constructed.

3. For each answer, do this in order:

   a. **Two-minute version:** Record yourself saying the full answer out loud. Time it. Aim for two minutes; stop yourself if you pass three. Write the version down in the `**2-minute version:**` field (prose, as you would say it, not a script). Then note the actual time it took.

   b. **Thirty-second version:** Record yourself saying the compressed version. The thirty-second version is not a summary of the long one; it collapses to one phrase of situation and task, then the result and the learning. Write it down in the `**30-second version:**` field.

   c. **Delivery self-score:** Listen to both recordings once. Write what you hear in the `**Delivery self-score:**` field. Be specific. Name:
      - Any filler words or hesitation markers ("um," "like," "so," "basically").
      - Whether the result arrived before the ninety-second mark in the long version or was buried in context.
      - Whether the thirty-second version actually collapsed to result and learning, or retained structure that does not fit the format.
      - One specific sentence you would cut or rewrite.

4. You do not need recording equipment beyond your phone or laptop microphone. The exercise requires one honest listen; you do not need multiple takes.

## Done When

Open `exercises/prep/` and run:

```
python check_prep.py --module 2
```

The validator exits 0 when `practice-log.md` contains at least two `### PL<n>` entries, each with a `**2-minute version:**`, `**30-second version:**`, and `**Delivery self-score:**` field filled in and no placeholder text. It exits 1 if any field is empty, missing, or contains a placeholder.

## Stretch

Add a third entry using an answer you have not yet rehearsed out loud. After the self-score, write one `**Revised 30-second version:**` field that fixes the specific problem you named in the score. Then record the revised version and note whether it improved the problem or revealed a new one.
