# Exercise: Route Five Requests

## Goal

Practice reading the four routing signals before you encode them as thresholds. A policy you cannot apply by hand is one you cannot debug.

## Why

The lesson gives you the signals; this exercise gives you the reps. Routing is not instinct. It is a small deliberate read of a few properties, and the ability to name the deciding signal is what separates a routing policy from a vague intention.

## Steps

For each of the five requests below, write four lines and then a route:

1. **Context size:** roughly how many tokens is this request, and does it fit the local 4K-8K window?
2. **Latency need:** is this a live interactive response, or can it run slow in the background?
3. **Stakes:** is the output routine and repeatable, or a consequential one-off?
4. **Sensitivity:** does the prompt contain private data you would rather not send off the machine?
5. **Route:** `local` or `cloud`, plus a one-line reason naming the signal that decided it.

### Sample Requests

Work through these four, then add one of your own.

**Request A:** Reformat 200 lines of Python to match a style guide. No private data.

Worked answer:
- Context size: small, fits easily.
- Latency need: not interactive; can run in the background.
- Stakes: routine; a wrong answer is easy to catch and rerun.
- Sensitivity: no private data.
- Route: **local**; cost-sensitive, latency-tolerant, routine task.

**Request B:** Summarize a 300-page PDF legal document (roughly 150K tokens when extracted).

Worked answer:
- Context size: far exceeds the local window.
- Latency need: background fine.
- Stakes: moderate.
- Sensitivity: depends on the document; assume not flagged for this example.
- Route: **cloud**; context size is a hard gate, the local model cannot hold the input.

**Request C:** Draft a reply to a customer ticket that includes their account number and purchase history.

Worked answer:
- Context size: small.
- Latency need: not urgent.
- Stakes: routine reply.
- Sensitivity: account numbers and purchase history are private identifiers.
- Route: **local**; sensitivity overrides, private data stays on the machine even though other signals are neutral.

**Request D:** One-shot architecture review of a new service design that you will share with the team today.

Worked answer:
- Context size: moderate, fits locally.
- Latency need: not time-critical.
- Stakes: high; the output will influence a real decision and you want the best answer available.
- Sensitivity: internal design doc; not flagged.
- Route: **cloud**; stakes are the deciding signal, quality outweighs cost for a consequential one-off.

**Request E (yours):** Write a request from your own work. Fill in the four-line analysis and state your route with the deciding signal.

## Done When

You can route any request by naming the signal that decided it, without consulting the lesson.

## Stretch

Find a request where two signals conflict: the prompt is sensitive (points local) but too large for the local window (points cloud). Write one sentence on which signal wins and why. The next lesson asks you to encode that answer as a written threshold before it becomes code.
