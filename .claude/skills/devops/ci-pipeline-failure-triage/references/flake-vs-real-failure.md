# Flake against Real Failure — reproduction discipline for a red run

Sources: [Pipeline: Basic Steps — retry](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/). Not sourced from a single URL otherwise — synthesized from this project's `defect-reporting.md` and `verification-standards.md` rules, which govern how an intermittent finding is reported.
Covers: SKILL.md §4 — **"Establish whether the failure reproduces, and state how many runs you looked at"**.

What a re-run proves, what it does not, and why "add a retry" is a decision to stop investigating rather than
a fix. The failure this file prevents is the expensive one: a real defect that reproduces one run in three,
closed as a flake, and shipped.

## What a green re-run establishes

| Observation | Establishes | Does not establish |
|---|---|---|
| Failed once, passed once | The failure is not deterministic under these conditions | That it is fixed, or that it was infrastructure |
| Failed twice on the same agent, passed on another | Agent state is implicated | Which state, or that the code is innocent |
| Failed on every agent, at the same stage | A deterministic failure | Anything about its class |
| Passed after a cache wipe | Cache damage is implicated | That the cache key is wrong, only that this run's cache was |
| Passed after "nothing changed" | Something changed that nobody is tracking — the clock, an external service, a dependency resolved at run time | That there is no defect |

The last row is the one that matters most in a Unity pipeline: an unpinned CLI, an unpinned gem, a package
resolved from a registry, and a certificate with an expiry date are all inputs that change with no commit
behind them.

## Reporting an intermittent failure

Per `defect-reporting.md`'s reproduction rules, a finding that does not reproduce every time is reported as
intermittent **with its rate** — never as reliable, and never discarded because the second run was green.

```
- Reproduction: 2 of 3 runs (builds #418, #419 failed; #420 passed), same agent, same commit
- Common to the failing runs: <the line, timing, or resource both share>
- Absent from the passing run: <what differed>
```

Two failing runs with one shared symptom are worth more than ten runs counted without comparison. The
comparison is the instrument; the count alone is a statistic.

## Retries

| Retry is | When |
|---|---|
| Legitimate | A genuinely external, transient step — a network fetch, a registry call — where the failure mode is known and bounded |
| Not a diagnosis | Anywhere else. It converts a one-in-three failure into a silent one-in-twenty-seven and removes the evidence that it happens |
| Actively harmful | Around a Unity build or a signing step: it costs a full stage each time, holds an agent, and can leave partial state the next attempt inherits |

A pipeline whose green rate depends on retries has an unmeasured failure rate. When a retry is added anyway,
the run must still record that the earlier attempts failed — a hidden retry is a false verification claim, per
`verification-standards.md`.

## Timing and ordering faults worth suspecting

| Pattern | Usual cause |
|---|---|
| Fails only on the nightly, passes on demand | Something time-bound — a licence lease, a token, a scheduled external service, or another job racing it |
| Fails only when two jobs run close together | A missing lock over the project, the licence pool, or a device |
| Fails only on the first run after an agent is rebuilt | A step that depends on state the previous run left behind — a cache, an installed tool, an unlocked keychain |
| Fails only on the slowest agent | A real timing dependency in a test, not infrastructure — this one is a defect, and it belongs to the code's owner |

## When to stop

Return the class as **inconclusive** rather than guessing when: only one run is available and its log does not
reach a signature; the log is truncated at the failure; or the two failing runs share no observable symptom.
State what would settle it — a clean-cache run, a run on a different agent, the log at a higher verbosity —
and route the request rather than acting on it. An honest inconclusive costs one round trip; a confident
wrong class costs a cycle and sends someone looking in a file that was never involved.
