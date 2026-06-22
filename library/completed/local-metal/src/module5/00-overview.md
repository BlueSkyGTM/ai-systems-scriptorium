# Module 5: The Routing Layer

The rig can now serve a model and you can measure what that costs. What you do not have yet is a
reason to reach for it. A local model that you remember to use sometimes is a toy; a local model that
your tooling reaches for automatically, on the right requests, is infrastructure. This module builds
the piece that makes the choice: a router.

The decision is not "local or cloud, pick one forever." It is per request. Some work is a perfect fit
for the rig: short prompts, routine edits, anything you would rather not send off your machine, the
high-volume drudgery where the cloud bill adds up. Other work is not: a refactor that needs 200,000
tokens of context the local model cannot hold, a one-off hard problem where you want the best answer
regardless of cost. A router reads a few signals off each request and sends it to the side that fits.

Those signals are the substance of the module. Cost: local inference is amortized hardware, near zero
per token, while cloud is metered. Latency budget: the local model is slower, which is fine for a
background job and wrong for an interactive one. Context size: the request either fits the local
model's window or it does not. Sensitivity: some data should not leave the machine. You will turn
those four into a written policy with concrete thresholds, justified against the latency baseline you
measured in Module 4.

Then you build `route.py`. Its core is a pure function: hand it a request, it returns a decision and
the reason for it. That core runs and self-tests with no rig and no cloud key, because a routing
policy is logic, not a network call. The live path is where the compounding pays off: when the
decision is "local," `route.py` calls the `ollama_client.py` you built in Module 3. The client you
wrote three modules ago becomes the local arm of a hybrid system.

You leave this module with a fifth file in the portfolio repository: `ROUTING.md`, the policy that
says, in writing, which work goes where and why. The metal, the runtime, the stack, and its speed were
documented in the first four modules; now the decision layer on top of them is too. Module 6 takes the
last step, wiring this router into Claude Code so the delegation happens without you thinking about it.
