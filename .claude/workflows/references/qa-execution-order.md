# QA Execution Order — `qa-pipeline.md` step 2

> **Which executors serialise, which run alongside, and why the order within the serial three is a choice
> rather than a contract.** Split out of `qa-pipeline.md` under the promotion rule in
> `client/feature-documentation.md`: it is read once, when the coverage assignment is being dispatched.

**Three of the four executors are serial, and the tools frontmatter forces it** — `qa-automation-engineer`,
`playtest-tester` and `performance-qa-engineer` all hold `mcp__<server>__*` against one Editor process, each
barred from starting a second. Same hard sandbox as `feature-development.md` step 2, stated there.

`build-verification-tester` holds **no Editor tooling at all**, which is why it runs alongside those three.
That freedom is about the Editor and nothing else: it **serialises with `performance-qa-engineer` whenever
both target the same physical device** — a walkthrough over adb and a Development Build profiled over adb are
the same wire. That is invariant I7, as hard as the Editor lock.

**The order within the three is the pipeline's choice, not a contract.** `qa-automation-engineer` goes first
because it alone writes `.cs`, so its domain reload lands before anyone enters Play Mode;
`performance-qa-engineer` goes last because it needs a quiet Editor for a run-to-run spread — and a design flaw found in playtest would make measuring this build pointless anyway.

## The two locks, claimed before dispatch

Both are global, both live in `<state-root>/project-state.md`, and both are claimed **before** the dispatch
and released on the return — never assumed free because no other run is visible from here.

| Lock | Invariant | Held by |
|---|---|---|
| Unity Editor | **I3** | `qa-automation-engineer`, `playtest-tester`, `performance-qa-engineer` — and seven more outside this pipeline |
| Physical device | **I7** | `performance-qa-engineer` profiling over adb, `build-verification-tester` walking cases over adb |

They are independent: an agent can hold both. A lock whose holder cannot be confirmed running is reclaimed by
the procedure in `state/README.md`, never silently — invariant **I9**.

## Dispatch only what was named

`qa-lead`'s coverage assignment names which `agent-id` covers what. **Dispatch exactly those**, never all
four by default. Unasked-for coverage is the same waste as speculative code, and `effort-allocation.md`'s
artifact budget forbids a test matrix beyond the paths the change touches at A3.

## Coverage the plan assigned but the pipeline cannot dispatch

`qa-lead` plans from the spec and the platform targets, so at any mobile target it will legitimately assign
**device** coverage — `build-verification-tester` on the artifact, `performance-qa-engineer` on a Development
Build. Neither can be dispatched unless a build exists, and `build-run-engineer` acts only on an explicit GD
request. Live, a plan assigned both against a project with no build and no attached device.

**Check the assignment against what exists before dispatching any of it**, and where it names device coverage
with no artifact, **ask the GD for the build then** — carrying what `qa-lead` assigned it to prove. Dispatching
anyway to collect the `Blocked` is a round spent learning what the plan already said: the device lane's rows
are the recovery, not the route. Where the GD declines, that coverage is unrun from the outset and joins the
gap list at step 4 rather than being re-dispatched, per `qa-exit-and-custody.md`.
