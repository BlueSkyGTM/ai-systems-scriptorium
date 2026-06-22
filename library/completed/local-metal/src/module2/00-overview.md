# Module 2: Linux and CUDA

The machine from Module 1 powers on and passes its stress test, but it is not yet a place a model
can run. It has no operating system you would serve from, no GPU driver, and no CUDA toolkit. This
module installs all three and proves they work together.

The instinct is to install whatever is easiest and move on. That instinct is how people end up with
a half-working CUDA stack that breaks on the next kernel update and a weekend lost to driver errors.
Local Metal treats the base layer as something you set up once, deliberately, so every module above
it never has to fight its own environment.

The plan is a dual boot. Windows stays for gaming and firmware updates; a Linux partition becomes
the inference workhorse. You will see why the bare Linux partition beats WSL2 for a serving host,
choose a distribution on real criteria rather than taste, install the NVIDIA driver and CUDA toolkit
the way that survives updates, and finish by proving the GPU answers to code with `nvidia-smi` and a
minimal CUDA check.

The reference build runs Ubuntu LTS, the distribution with the deepest CUDA documentation and the
largest community to search when something breaks. Your choice can differ; the reasoning should not.

You leave this module with a second file in the portfolio repository: `SETUP.md`, the software
baseline that records the distro, the driver, the CUDA version, and the verification readout that
proves the stack is live. The metal was documented in Module 1; now the runtime is too.
