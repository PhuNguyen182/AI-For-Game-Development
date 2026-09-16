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

Both are global, both live in `state/project-state.md`, and both are claimed **before** the dispatch and
released on the return — never assumed free because no other run is visible from here.

| Lock | Invariant | Held by |
|---|---|---|
| Unity Editor | **I3** | `qa-automation-engineer`, `playtest-tester`, `performance-qa-engineer` — and seven more outside this pipeline |
| Physical device | **I7** | `performance-qa-engineer` profiling over adb, `build-verification-tester` walking cases over adb |

They are independent: an agent can hold both. A lock whose holder cannot be confirmed running is reclaimed by
the procedure in `state/project-state.md`, never silently — invariant **I9**.

## Dispatch only what was named

`qa-lead`'s coverage assignment names which `agent-id` covers what. **Dispatch exactly those**, never all
four by default. Unasked-for coverage is the same waste as speculative code, and `effort-allocation.md`'s
artifact budget forbids a test matrix beyond the paths the change touches at A3.
