# Module 1: The Build

A local model server is a hardware problem before it is a software problem. You can read every Ollama
tutorial in existence, but until a machine with the right GPU sits on your desk, none of it runs. This
module gets you that machine, and gets you it for the right reasons.

The temptation is to treat the parts list as a shopping trip: pick a GPU, grab some RAM, check out.
That path leaves you with a gaming PC that happens to run a model, and a set of choices you cannot
defend when one of them becomes a bottleneck. Local Metal treats the build as engineering. Every part
in the reference machine was chosen to serve inference, and you should be able to say why each one is
there before you pay for it.

So this module moves in order. First, the case for owning compute at all, and the shape of the rig
that answers it. Then the parts, one decision at a time: why sixteen gigabytes of VRAM and not eight,
why DDR5-6000 and not a cheaper kit, why a small-form-factor case changes the power supply you buy.
Then the build itself, done the low-risk way, at a counter that assembles and stress-tests it for you.
Finally, the record: you commit the machine you actually bought to a file called `HARDWARE.md`, the
first artifact in the repository that becomes your portfolio.

The reference build is a small-form-factor machine with a Ryzen 7 7700X, a 16GB RTX 4060 Ti, 64GB of
DDR5-6000, and a 2TB NVMe drive, codenamed Cthulhu in the spec this book is built from. Your build does
not have to match it part for part. It has to match the reasoning, so that when you substitute a part,
you substitute it on purpose.

You leave this module with a parts list you can defend, a machine that boots and holds under load, and
a documented build record. That record is the foundation the rest of the book stands on: there is no
model stack, no routing layer, and no delegation until the metal is real.
