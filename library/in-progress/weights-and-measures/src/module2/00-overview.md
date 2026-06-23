# Module 2: Fitting and Not Fitting

M1 made a loop run. This module asks the harder question: is it working?

"Working" has a precise answer. A loop that drives training loss to zero while validation loss
climbs is not working; it is memorizing. The verdict comes from one place: held-out validation
loss, measured on data the model has never touched. Not training loss. Not token accuracy alone.
Not the feeling that the curve looks right. The held-out number is the signal; everything else
is noise until you have it.

The four lessons in this module build that discipline one layer at a time.

## Four Lessons

1. **The Held-Out Set** (`the-held-out-set`): why two scalar signals are mandatory and why only
   one of them tells you whether the model is learning or memorizing. You split a dataset with
   no overlap, write the validation loop with `model.eval()` and `torch.no_grad()` both present,
   and confirm the validation number is stable across two runs. The split must come before any
   preprocessing; the eval mode and the no-grad context are not optional.

2. **Reading Loss Curves** (`reading-loss-curves`): the divergence pattern is the overfitting
   signal. You log train and validation loss per epoch, tabulate the trajectory, and identify the
   epoch where validation loss turns while training loss keeps falling. That epoch is the one you
   would promote, not the last one. Token accuracy is a companion signal, not a substitute, and
   near-100% accuracy on short completions is an overfit flag, not a strength.

3. **Early Stopping as a Policy** (`early-stopping-as-a-policy`): stopping early is not a
   hyperparameter knob; it is an auditable checkpoint-promotion policy. You implement a patience
   counter, save the best checkpoint by validation loss with optimizer state included, and confirm
   that the model you restore is the best-epoch model, not the model from the last epoch. Optimizer
   state is mandatory: restoring weights without momentum and adaptive estimates causes learning
   dynamics to diverge on resume.

4. **Instrumenting the Run** (`instrumenting-the-run`): the payoff and the module's gated
   deliverable. You instrument a complete loop with the validation pass and early stopping,
   deliberately induce overfitting by training on a tiny dataset with no regularization for too many
   epochs, and confirm the promoted checkpoint is pre-divergence. Then you run the module validator
   against your loop and make it pass.

## What This Module Feeds Forward

The validation discipline you install here is the precondition for everything that follows. M4
trains LoRA adapters; knowing whether an adapter is overfitting or generalizing requires the
held-out signal this module makes routine. M5 formalizes that signal into an eval gate: the gate
only means something if the validation set is clean and the checkpoint-promotion policy is
auditable. You cannot bolt those things on later. They have to be in the loop from the start.
