# Kill switches, circuit breakers, canary tokens

The budget governor decides *when* to stop a runaway. This lesson is the *how* — the control plane that actually halts an agent, and the detectors that decide a halt is warranted before any budget is breached. None of it is new computer science. All of it is old reliability engineering, reasserted against a thing that can now read its own off switch.

## The first rule: the agent reads it, the agent cannot write it

A kill switch is a boolean the loop checks before every action: set, and the next action does not run. Module 3 put one in the agent loop on day one. The defining property is worth stating sharply, because it is the property that makes it a *safety* control and not just a flag the agent flips for itself: the agent can read the switch and must never be able to write it.

If the off switch lives in the agent's reachable state — a variable in its memory, a file in its working directory, a tool it can call — then the agent can disable its own kill switch, and you have a kill switch in name only. The whole point is that an agent going wrong cannot turn off the thing designed to stop it. So the switch lives *outside* the agent's blast radius:

- a **feature flag** in a service the agent has no credentials to mutate (LaunchDarkly, Statsig, Unleash),
- a **Redis key** on an instance the agent can read but not write,
- a **signed config** the agent verifies but cannot forge, or
- a **container-level kill** — the orchestrator stops the pod from the outside, where no in-process flag can save it.

```python
# module4-fleet/control/kill_switch.py — read-only from the agent's side
import redis

class KillSwitch:
    """The agent gets a handle with GET only. The operator's tooling holds SET.
    Wire the Redis ACL so the agent's credential cannot write this key."""
    def __init__(self, client: redis.Redis, key: str = "fleet:killswitch"):
        self._r = client          # connection scoped to a read-only ACL
        self._key = key

    def tripped(self) -> bool:
        return self._r.get(self._key) == b"1"

# in the loop:
def step(agent, switch: KillSwitch):
    if switch.tripped():
        raise Halted("kill switch engaged — no further actions")
    return agent.act()
```

The read-only access-control rule (ACL) is the load-bearing line, not the Python. A kill switch the agent can `SET` is theater.

## The circuit breaker: stop the failing call before it fails again

A kill switch is a manual, global halt. A circuit breaker is an automatic, scoped one — Nygard's pattern from service reliability, pointed at agent behavior. It wraps a single failing operation and stops calling it once a pattern of failure appears, so a transient problem doesn't become a retry storm.

It has three states:

- **Closed** — normal. Calls pass through. The breaker counts failures.
- **Open** — tripped. Calls fail fast without executing, for a cooldown period. The downstream gets a break; the agent stops hammering it.
- **Half-open** — probing. After the cooldown, let one call through. Succeeds, close the breaker; fails, open it again.

For agents, the trip condition is not only "the call errored." The breaker should trip on *behavioral* patterns that signal a stuck or looping agent — the clearest being **N identical tool calls in a row**. An agent that calls the same tool with the same arguments five times running is not making progress; it is stuck, and the next four calls will spend money to learn what the first four already proved. Trip the breaker on the repetition.

```python
# module4-fleet/control/breaker.py
import time

class CircuitBreaker:
    def __init__(self, fail_max: int = 5, cooldown_s: float = 30.0):
        self.fail_max, self.cooldown_s = fail_max, cooldown_s
        self.fails, self.opened_at, self.state = 0, None, "closed"
        self._last_call = None

    def call(self, fn, *args):
        if self.state == "open":
            if time.time() - self.opened_at < self.cooldown_s:
                raise BreakerOpen("circuit open — failing fast")
            self.state = "half-open"                  # probe
        sig = (fn.__name__, args)
        if sig == self._last_call:                    # behavioral trip: identical repeat
            self.fails += 1
        self._last_call = sig
        try:
            result = fn(*args)
            if self.state == "half-open":
                self.state, self.fails = "closed", 0  # recovered
            return result
        except Exception:
            self.fails += 1
            if self.fails >= self.fail_max:
                self.state, self.opened_at = "open", time.time()
            raise
```

Statistical detectors — an EWMA or CUSUM on call rate or error rate — refine the trip condition, catching a slow drift a fixed count misses. They are an upgrade, not a replacement: a smoothed average is still a number that can be wrong, so a statistical breaker layers *on top of* the hard limits, never instead of them. The hard count is the floor that does not bend.

## Canary tokens: detect the breach you didn't predict

The kill switch and breaker stop misbehavior you can characterize — a global pull, a repeated call, a failure rate. A canary token detects the misbehavior you didn't anticipate: an agent reaching for something it has no legitimate reason to touch.

A canary token is a fake credential, a honeypot record, a decoy file — planted where a well-behaved agent will never go, and wired to alarm the instant anything reads it. A real example: drop an unused, monitored API key labeled `prod-db-admin` into the environment. No legitimate task needs it. The day a compromised or misaligned agent enumerates its environment and *touches* that key, you have detection — not from predicting the attack, but from the agent stepping on a tripwire that exists only to be stepped on.

The strength is that it costs the agent nothing to avoid and the attacker everything to detect. A clean run never sees the canary. A run that has gone wrong — prompt-injected, jailbroken, exfiltrating — trips it, and you learn about the breach from the tripwire instead of from the incident report.

## Quarantine: reroute, don't just kill

Sometimes the right response is not to kill the agent but to *contain* it — keep it running, sever its reach, and watch. At the kernel layer, eBPF-based tooling like Cilium enforces and redirects a pod's network egress in the datapath, before a packet leaves the node: point a quarantined pod's egress at a node-local backend and the agent thinks it is talking to the production database while its packets land on a forensic honeypot instead. The agent keeps acting, you keep observing, and nothing it does reaches a real system. It is a kill switch with a one-way mirror — you stop the harm without stopping the evidence.

## The control plane, defined once

Put the three together and you have a control plane that sits *beside* the agent, not inside it: a kill switch the operator owns and the agent cannot write, a circuit breaker that trips on failure and behavioral patterns, and canary tokens that catch what you didn't model. The budget governor from lesson 06 is the fourth member — its breach is one of the events that trips the switch.

This is the control plane M4's fleet lessons govern at scale. A fleet runs the same kill switch across many agents, the same breaker per dependency, the same canaries across the environment — referenced there, defined here. Build it once for one agent and the fleet inherits it; the only thing that changes at scale is how many readers share the one switch the operator holds.

A control plane the agent can edit is not a control plane — it is a suggestion. Keep the off switch in your hand, not the agent's.

## Core concepts

- A kill switch is a boolean the agent reads but cannot write — a feature flag, a Redis key under a read-only ACL, a signed config, or a container-level kill — placed outside the agent's blast radius so a misbehaving agent cannot disable its own stop.
- A circuit breaker trips on failure *and* behavioral patterns (five identical tool calls in a row), moving closed → open → half-open; statistical detectors (EWMA/CUSUM) layer on top of hard counts, never replace them.
- A canary token is a honeypot credential or decoy record an agent has no legitimate reason to touch, wired to alarm on access — it detects the breach you didn't predict at zero cost to a clean run.
- Quarantine (eBPF/Cilium egress reroute) contains a suspect agent without stopping it, preserving evidence; together these form a control plane defined for one agent and inherited unchanged by a fleet.

<div class="claude-handoff" data-exercise="exercises/module4/07-kill-switches-circuit-breakers-canary-tokens/">

**Build it in Claude Code** — give the `_harness/` agents a control plane they cannot subvert: a kill switch backed by a key the agents' credentials can read but not write, checked before every action; a circuit breaker that trips on five identical tool calls in a row (closed/open/half-open); and a canary token — a decoy credential in the agent's environment that alarms and trips the kill switch the instant an agent reads it. Prove the agent cannot turn off its own switch. Open the repo and run the exercise for this lesson.

</div>
