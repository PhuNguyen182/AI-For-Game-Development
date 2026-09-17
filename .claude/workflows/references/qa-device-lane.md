# The Device Lane — `qa-pipeline.md` step 2b

> **The only lane in this project that can satisfy "it works on the target platform".** Split out of
> `qa-pipeline.md` under the promotion rule in `client/feature-documentation.md`: it exists only when a build
> exists, and `build-run-engineer` refuses anything but an explicit GD request — so most QA runs never open
> it.

Everything else in the QA pipeline is Editor-bound and never more than indicative, per
`qa/verification-standards.md`. That is what this lane is for, and why its absence is a stated gap rather
than a pass.

When a build exists, its `Result:` — the artifact path plus the platform and configuration it was built at — is what the verifier is dispatched with. Three things then happen in this order, the order being the contract:

1. **The cases are derived, not improvised.** `/plan-test-coverage` turns the spec into per-case
   `Starting state / Actions / Expected`; hand over only those marked `Observe via: build/device` that
   `qa-lead` already named. The command produces cases; it never decides which are owed.
2. **The device is confirmed before the artifact is touched.** No device is `Blocked` on that coverage — not
   a licence to substitute an Editor run. The artifact-only checks still run; the rest becomes a gap.
3. **A crash stops that case's path** — logs pulled, nothing silently relaunched past it, trace to `/investigate-device-crash`.

This lane is the only thing in the project that can satisfy `verification-standards.md`'s *"it works on the target platform"* row; everything else here is Editor-bound and never more than indicative.

## Routing — the device lane's own rows

Lifted from `qa-pipeline.md`'s routing table, because every one of them is unreachable unless this lane is
open. That pipeline keeps a single pointer row to this table.

| Return | Action |
|---|---|
| `build-verification-tester` → `Blocked`, `Routed to: build-run-engineer` | No artifact exists. Ask the **GD** for the build — never dispatch one off pipeline state |
| `build-verification-tester` reports no device reachable | That coverage is unrun. It goes to `qa-lead`'s gap list at step 4, and on to CP4 if it cannot be closed. Never an Editor substitute |
| A fix for a device-found defect returns at **E3** | The artifact is stale — the build that found the defect still contains it. Ask the **GD** for a rebuild; without one that coverage stays unrun and joins the gap list. Never re-run the walkthrough against the old build |
| A device walkthrough classified a **design flaw** | The GD, immediately — same as `playtest-tester`. I5 is not limited to the Editor |
| A crash or ANR on the device under test | `/investigate-device-crash`. Never `crash-anr-investigator`, which declines a local trace by contract |
| `build-run-engineer` → `Rejected`, `Routed to: gd` | It was handed pipeline state instead of a GD request. A correct refusal; get the request or drop the branch |

- **A design flaw never re-enters the engineering loop**, from a device any more than from the Editor. It
  goes to the GD immediately, per invariant **I5**.
- **The device lock is invariant I7** and is claimed in `<state-root>/project-state.md` before dispatch:
  `build-verification-tester` walking cases over adb and `performance-qa-engineer` profiling a Development
  Build over adb are the same wire, so the two never run at once. It is independent of the Editor lock — an
  agent can hold both.
