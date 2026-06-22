# Introduction

Every engineer who builds with frontier models meets the same wall. The prototype works, the demo
lands, usage grows, and the invoice grows with it. Tokens are cheap until they are a budget line.
Context windows overflow, retries stack, and a background agent that runs all day turns metered
inference into rent. The frontier API is the right tool for the hard ten percent of your work. The
other ninety percent does not need it, and paying frontier prices for it is a choice, not a law.

Local Metal is the other choice. You buy a machine, you put it on your desk, and you host the models
that handle the routine work yourself. The marginal cost of a token it serves is the electricity to
compute it. This book runs the whole arc: from the Micro Center parts counter to a networked
inference host your other machines, and Claude Code, can delegate to. You select the hardware,
assemble it, install Linux and CUDA, fit a coding model entirely in GPU memory, split a larger model
across the GPU and system RAM, design the routing layer that decides what stays local and what goes
to the frontier, and wire it into your daily tooling. You finish owning a slice of compute and the
judgment to use it.

## This Is Home-Scale, on Purpose

This is not a datacenter book. There is no Kubernetes, no multi-GPU cluster, no rack. It is one
machine you can build in an afternoon and run next to your monitor, and the whole design holds that
line: a small-form-factor box, a single consumer GPU, a model stack you can reason about end to end.
Local Metal is the companion to Sans Python, not a capstone above it. Sans Python taught you to build
AI systems on hosted compute; this teaches the same engineer to own the compute. You do not need to
finish the rest of the library to start here. You can build the rig early and host your first model
the day it boots; what grows over time is how hard you push it.

## What You Build

The portfolio artifact is concrete and demonstrable: a working, networked local-model inference
server with a routing layer, integrated into Claude Code as a delegation target. Along the way you
commit the build itself to a repository, starting with `HARDWARE.md`, the record of the machine you
chose and why. By the last module you can point a hiring manager at a repository and say the most
literal thing an AI engineer can say: I built the inference server my tooling delegates to.

## How to Read This

Each lesson ends in an exercise you run in Claude Code, with this repository open. The lesson holds
the why; the exercise is where you build. The command outputs printed in these pages are the results
you should expect on the reference build; treat them as the target and confirm them against your own
machine. You do not need the hardware in hand to start reading, but the book is written to be
finished with a real one humming under your desk.

Turn the page. Module 1 starts at the parts counter, because nothing else is possible until the
machine exists.
