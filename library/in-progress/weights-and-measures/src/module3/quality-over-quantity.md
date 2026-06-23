# Quality Over Quantity

Your fine-tune is bounded by its data. Not by the model, not by the training loop, not by the
learning rate schedule: by whatever you hand the optimizer. Before a single gradient fires, the
corpus has already set the ceiling.

That ceiling has a name. It is called the quality gate, and it belongs at the front of the
pipeline, not at the back.

## The Three Dimensions of Quality

Quality in a fine-tune set is not a feeling. It breaks into three properties you can check
mechanically:

**Coverage** is whether the corpus contains the behaviors you want the model to learn. A model
trained only on polite customer-service exchanges cannot route a technical escalation. The training
data defined the job; the model did exactly what the data asked. If a behavior is absent from the
training set, the model has no mechanism to acquire it.

**Correctness** is whether each example targets the right output. A training example with a wrong
assistant turn does not fail silently: the optimizer uses it to update weights, and those weights
carry the mistake forward. One bad label does not wash out; it competes with the correct signal
and wins some fraction of the time.

**Consistency** is one format and one style, end to end. Mixed schema shapes force the model to
reconcile contradictory surface patterns instead of learning the underlying task. A validator can
check consistency before training; the optimizer cannot correct for it during.

## What the Docs Say About Size

The Azure AI Foundry fine-tuning guidance is direct on this point. From
[learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning):
the minimum is 10 examples, 50 or more are recommended, and doubling the dataset can linearly
raise quality. That last clause is the one to hold onto. Linear gains from more data sound like
the obvious path.

The same source draws the limit clearly: low-quality examples hurt, so prune to the highest-quality
examples first. More data helps when the new data is as good as the data already present. When it
is not, the line does not go up; it goes down.

The failure mode is not obscure. A 200-example set where 40 examples carry wrong targets or
inconsistent formatting is not a 200-example problem. It is a 160-example problem that is
actively training against itself. You get worse-than-nothing from the 40.

## Prune Before You Train

The cheapest epoch is the one you never run on garbage. A GPU-hour spent training on bad examples
is not a sunk cost you recover later by training more epochs on clean ones; the updates from the
bad pass are in the weights. You are not starting from zero after a bad epoch; you are starting
from a model that has already moved in the wrong direction.

Pruning changes the unit of cost. Filtering out a bad example costs one read and one discard.
Running that example through the training loop costs a forward pass, a backward pass, and a weight
update that now has to be unwound by some future good example, imperfectly, over time. The
economics are not close.

The discipline this demands is clear: data quality is a gate you enforce before training, not an
assumption you carry into training and hope for the best. Coverage, correctness, and consistency
are verifiable properties. A script can check them. The optimizer cannot.

## What This Looks Like in Practice

Score your examples before they touch the training loop. For each example, ask three questions:

- Does this example demonstrate a behavior the model should learn? (Coverage)
- Is the assistant turn the correct response to this prompt? (Correctness)
- Does this example match the format and style of every other example in the set? (Consistency)

An example that fails any of the three is a candidate for removal, not repair under time pressure.
A repaired example with ambiguous corrections is not a clean training signal; it is a source of
inconsistency that passes the format check and poisons the correctness signal.

Cut to the subset that passes all three. A smaller, clean set trains faster, produces a cleaner
gradient signal, and produces a model that generalizes to your validation set instead of
memorizing the noise you forgot to remove.

The set that ships to training is the first artifact of the pipeline. Treat it as one.

## Core Concepts

- A fine-tune is bounded by its training data; the corpus is the first quality gate, and no amount
  of training recovers from a bad corpus.
- Quality in a fine-tune set is three verifiable properties: coverage (the behaviors you want),
  correctness (no wrong targets), and consistency (one format, one style).
- Doubling the dataset can linearly raise quality, but low-quality examples hurt: prune to the
  highest-quality examples first, and a smaller clean set outperforms a larger noisy one.
- Pruning before training is always cheaper than training through bad examples; a bad epoch leaves
  traces in the weights that future good epochs must undo.
- Data quality is a gate enforced before a single epoch, checked mechanically against coverage,
  correctness, and consistency, not a vibe carried into training.
- The scored, pruned training set is the pipeline's first artifact; ship it with the same
  discipline you would apply to any other versioned artifact.

<div class="claude-handoff" data-exercise="exercises/module3/quality-over-quantity/">

**Build It in Claude Code**: Take a small messy JSONL example set (20 to 30 examples with planted
defects: a few examples with wrong assistant targets, a few with inconsistent format or missing
fields, a few that duplicate behaviors already covered elsewhere), score each example against the
three quality dimensions (coverage, correctness, consistency), and cut the set to the highest-quality
subset that passes all three checks; then write a short argument, in code comments or a README,
that explains why the smaller pruned set is a better training input than the original, citing the
linear-gain and low-quality-hurts properties from the Azure AI Foundry fine-tuning guidance.

</div>
