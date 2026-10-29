# Flake against Real Failure

Sources: Jenkins `retry` (`https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/`); reporting rules from `qa-standards`.

## What a re-run establishes

| Observation | Establishes | Does not establish |
|---|---|---|
| Failed once, passed once | Not deterministic under these conditions | That it is fixed, or that it was infrastructure |
| Failed twice on one agent, passed on another | Agent state is implicated | Which state, or that the code is innocent |
| Failed on every agent at the same stage | Deterministic failure | Its class |
| Passed after a cache wipe | This run's cache was damaged | That the cache key is wrong |
| Passed after "nothing changed" | Something untracked changed: clock, external service, run-time dependency | That there is no defect |

Inputs that change with no commit: an unpinned CLI or gem, a package resolved from a registry, a certificate with an expiry date.

## Reporting an intermittent failure

```
- Reproduction: 2 of 3 runs (builds #418, #419 failed; #420 passed), same agent, same commit
- Common to the failing runs: <line, timing or resource both share>
- Absent from the passing run: <what differed>
```

Two failing runs with one shared symptom beat ten runs counted without comparison.

## Retries

| Retry is | When |
|---|---|
| Legitimate | A genuinely external transient step (network fetch, registry call) with a known, bounded failure mode |
| Not a diagnosis | Anywhere else: it turns a one-in-three failure into a silent one-in-twenty-seven |
| Harmful | Around a Unity build or signing step: costs a full stage, holds an agent, may leave partial state |

If a retry is added anyway, the run must still record that earlier attempts failed; a hidden retry is a false verification claim (`qa-standards`).

## Timing and ordering patterns

| Pattern | Usual cause |
|---|---|
| Only on the nightly | Something time-bound: licence lease, token, scheduled external service, another job racing it |
| Only when two jobs run close together | Missing lock over the project, licence pool or device |
| Only on the first run after an agent rebuild | Dependence on state a prior run left: cache, installed tool, unlocked keychain |
| Only on the slowest agent | A real timing dependency in a test: a defect, owned by the code's owner |

## Inconclusive

Return inconclusive when only one run is available and its log reaches no signature, the log is truncated at the failure, or the failing runs share no symptom. Name what would settle it (clean-cache run, different agent, higher log verbosity) and route the request.
