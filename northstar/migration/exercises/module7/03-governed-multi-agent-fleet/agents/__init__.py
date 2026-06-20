"""The SWE team's nodes — architect, coder (x2), reviewer, tester.

Each node is a function ``run(task, ctx) -> A2AResult`` that takes a typed A2A
handoff, does its work under the fleet's governance (budget charged per call,
kill switch checked, every action audited), and hands a typed result to the next
node. The coder node is the M6 terminal coding agent reused as a team member —
elevate, don't author.
"""
