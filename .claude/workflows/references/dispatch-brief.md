# The Dispatch Brief — what every dispatch carries (I1)

An agent sees only its brief. Every row here is keyed to an agent's own `If absent` behaviour: omit it and you get
`Blocked`, or worse, a silent default the agent never states. Supply from the feature's `LEDGER.md` where one
exists, never from memory of an earlier run. Name each value; never paste a standard's content — cite its path.

## The four that travel with every dispatch

| Value | Source | With no ledger |
|---|---|---|
| **Tier and the five axes** — A1–A5 plus D, C, U, R, X separately | The ledger, set at `feature-intake.md` step 2 | Classify from the request yourself (`task-classification.md`); a tier you can classify in one read is not a missing input |
| **Attempt budget** | From D (`task-classification.md` Step 4) | Derived the same way |
| **Verification floor** — sent as the **V-number** (`V2`), never the A-tier (`A2` reads as V1, but a code change always changes state) | From A | Derived the same way |
| **Track** — client, or client + multiplayer, stated on or off | The ledger; never re-derived | `project-state.md` → `Track:`, else G26 — never "probably client-only" |

On an ordinary re-entry only **U** is re-read (research or CP1 spent it down). A change request re-reads all five.
Counters carry across every door; the only resets are listed in `references/bounds.md` → *Resets*.

## Implementing agents — `feature-development.md`

| Carry | Because |
|---|---|
| The agent's task section, plus `Module boundaries:` and `Client-server contract:` | No agent can respect a boundary it was never shown; other agents' tasks are withheld |
| The feature root, where its code and `DECISIONS.md` live | Otherwise the agent searches the tree, or blocks |
| The netcode foundation (backend track only) | Otherwise `netcode-engineer` routes to `cto` for a value the ledger holds; if genuinely unset, ask the GD once (G44) |
| The per-platform performance budget | Otherwise a guessed budget |
| The track standards to read, by path — `.claude/standards/client/*` per `rules/standards-index.md` | Naming them is what loads them |
| On **E3**: strikes, prior findings, attempts already spent. On any door whose work fixes a recorded bug — **E3**, or an **E2** or escalated lane opened for one — each defect **by bug ID** with its record | No agent can count its own rounds; the ID is how its fix is tracked |
| That `BUGS.md` and `bug-log.md` are read-only to it | Only the orchestrator records bugs; an implementing agent names what it fixed, it never edits a status |

**Forward what earlier agents produced** — agents cannot see each other's returns:

| From → field | To |
|---|---|
| `csharp-engineer` → `Public contract:` | `unity-engineer`, `ui-ux-programmer`, `netcode-engineer`, `server-authoritative-engineer` |
| `csharp-engineer` → `Determinism:` | `netcode-engineer`, `server-authoritative-engineer` |
| `csharp-engineer` → `Assumptions and known limitations:` | every downstream agent, **and** the G40 review ask as the concrete cost of skipping |
| `technical-artist` → `Authored:`, `Pipeline:` | `unity-engineer` |
| `unity-engineer` → `Core calls used:`, `Changed:` | `ui-ux-programmer` |
| `netcode-engineer` → `Message contract:` | `server-authoritative-engineer` |

**Ask the agent to state back** what no envelope carries: attempts used out of the budget and, past the first, what
improved; what verification actually ran and what was impossible, and why; wherever the brief named a bug, each
bug ID it fixed (it
never closes one) and any test that now guards it; and, from `tech-lead-sdk-platform`, its assumptions and known
limitations.

## Assembling the Implementation Note

| Field | Comes from |
|---|---|
| Spec | The brief you sent — only you know which clauses |
| Tier | The ledger / the brief |
| Attempts | What the agent stated back; where it did not, record that it did not — never a default `1` |
| Changed | The working-tree diff, read against the envelope's `Files:` / `Changed:` / `Authored:` / `Implemented:` |
| Assumptions, Known limitations | The envelope's `Assumptions and known limitations:` |
| Deliberately out of scope | A `Routed to:` returned beside `Status: Done` — evidence when present, never proof of absence |
| Fixes | What the agent stated back on **E3** — every E3 brief asks for it |
| Verification done | The envelope's verification field where one exists (`Performance:`, `Responsiveness verified:`, `Cost:`, `Behaviour under loss and latency:`), else what the agent stated back |

## Review gates — `review-pipeline.md`

The code or diff; the Tech Spec section or direct notes; the tier, axes and **V-number**; the author; the
Implementation Note; the strike count and every prior verdict; **whether this is the feature-complete submission**
(the feature-root documents are checked only then). Absent the floor, `code-reviewer` reviews and states it was not
supplied — a finding against the brief, not the author.

| Entry | Differs |
|---|---|
| **E2** audit | No author, strike, CP3, note or ledger. Name what the audit checks against — or dispatch `security-reviewer` alone |
| **E3** gated-direct, `direct` or test code | The behaviour it was written against instead of a spec section; **say which origin** — they escape differently (B4, B5) |
| Supply-chain pre-gate (G45) | `security-reviewer` alone; a go/no-go on the import, not a strike |

## QA — `qa-pipeline.md`

The Tech Spec or notes; the A-tier and **V-number**; the H/M/Q requirement list; the track; the GDD scenario and
expected feel; the performance budget and baseline; **the review status, as one of three — per submission where
they differ**: both verdicts as given; "the GD declined review", in those words; or "review is not part of this
run" at **E4** on code already in the repo — otherwise `qa-automation-engineer` blocks and `qa-lead` may read
silence as "clear"; the target platforms; for device work, the test-case list in `plan-test-coverage`'s format and
whether a device is expected. **At sign-off, the coverage assignment and exit criteria from the plan, verbatim** —
`qa-lead` otherwise re-derives the bar silently.

**Assurance in the gated-direct lane** gets the Implementation Note, both review verdicts and the tier, and the
intended behaviour the change was written against in place of a requirement list; it is told no QA plan exists, so
it scores the note's claims, not coverage. **`qa-lead` at E4** gets the behaviour and its source in place of a
spec, and `bug-log.md` → *Unattached bugs* in place of `BUGS.md`.

**Bugs, both ways.** Every QA executor gets the path to the feature's `BUGS.md`, so a finding matching a known bug
cites its ID. On **E3**, the bug IDs marked `Fixed` that it must verify, each with its record; it returns a per-ID
verdict in `Bug verification:`. `qa-lead` at sign-off gets the feature's bug list with every status.

**Root cause for a bug reopened twice (B6).** `technical-architect` gets, in place of a rejection history, the
bug's full record — every history row, each QA verification's evidence, and every fix the owner returned.
**`qa-lead` re-entering plan mode** on a feature that already has a `BUGS.md` gets it, so existing cases and bugs
are planned around, not re-derived. **At E4**, executors get `bug-log.md` → *Unattached bugs* in place of a
feature's `BUGS.md`.
