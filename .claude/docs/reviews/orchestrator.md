# `orchestrator.md` — Review, run over three rounds and gated before scoring

> **Working note.** Seventh and last in the series. The router is the one file every other file in the layer
> depends on, and the only one that had never been reviewed. Read [`README.md`](README.md) first — these notes
> are history, the layer that runs is `.claude/workflows/`, and the current state is `workflow-checklist.md` §16.

## Part 0 — What was run, and what that buys

**The router dispatches no agent**, so it cannot be "run" the way the six pipelines were. Running it means
making something else follow step 0 literally and recording where it hits a wall. Three rounds, three
materially different methods — the GD's instruction was that each round mark harder than the last.

| Round | Method | Result |
|---|---|---|
| **1** | An independent routing agent, **seven** real GD inputs, told to follow step 0 to the letter | **6 of 7 routed to the wrong row.** 15 findings, 7 High |
| **2** | A second independent router, **ten** inputs against the *fixed* file, plus an explicit ordering audit | 13 findings — **6 of them defects round 1 introduced** |
| **3** | `code-reviewer` over the round's **own diff, before any score**, then `assurance-evaluator` | **`Request changes`** — 17 findings, 2 High |

**What this evidence is.** The routing runs are **E2** for claims about the *specification* — the walls are
reproducible from the returns. They are **E0** about production behaviour: no pipeline ran, `.workflow/` does
not exist, and step 0 has been exercised only by agents *reading* it, never by an orchestrator dispatching
from it. All negative testing ran in a copied tree via `-Root`, never planted in the working tree.

## Part 1 — What the runs proved works

- **The four escalation criteria did real work on the one input that needed them.** "Thêm voice chat trong
  trận co-op 3 người" trips *needs more than one role* (D3+), *multiplayer-relevant* (C2+) and *rests on
  something undecided* (U3), each decidable from the request with no agent call — and rows 1–10 all correctly
  failed to match. The router working end to end.
- **The second-slug guard caught the hardest input's real hazard.** With one feature in flight, *"check
  `project-state.md` before opening one"* correctly forbade a second ledger for a mid-flight change.
- **The two agent classes resolved a mode-3 dispatch with no judgement call** — derived from `tools:`
  frontmatter, so `unity-engineer` is class B and the gate offer is owed, mechanically.
- **`feature-intake.md` E1 carrying two of four values is handled honestly**, not papered over: the tier does
  not exist until that pipeline's own step 2 produces it.

## Part 2 — Findings

### The three structural failures

**O1 — the stated reading rule inverted the safety gradient it existed to provide.** *"Read top-down, first
match wins — several rows can describe one input, and the cheaper row is listed first on purpose."* Three
catch-alls sat above every specific row:

| Input | Matched | Should have reached |
|---|---|---|
| A `Game.Core.*` cooldown, 8s → 6s | *"a tuned value"* (judgeable), **four rows above** | the gated-direct row **written for that exact change** |
| A signing-config / keystore edit | *"config"* (chore) | the criteria that make it **A5** |
| A production crash, phrased as a question | *"A question, or an ask to explain"* | `crash-anr-investigator` |

The correction existed — *"a damage formula cannot be judged by looking"* — twenty lines below the table, out
of reach of the stated procedure. `gated-direct-lane.md`'s own motivating example is the first row of that
table, and the lane was unreachable for it.

**O2 — the criteria table could see two of `task-classification.md`'s ten C3/C4 categories.** It detects
C2+ only through `Game.Core.*` and multiplayer. A credential, a store submission, real-money IAP, player PII,
save-data migration or published git history trips **nothing** — and falls to the chore lane: no gates, no
`security-reviewer`, no recorded debt, on the one rule `security.md` grants no tier exemption.

**Round 1 did not find this.** It reordered the table and left the entry condition untouched — fixing what
the ordering sorts without fixing what gets into the sort.

**O3 — three doors had no route.** `change-request`, `E4` and `E6` appeared **zero times** in
`orchestrator.md`. A mid-flight spec change — which halts work, reopens a checkpoint and resets five counters
— was reachable only if the GD named the file, which a GD phrasing a change does not do.

### The rest

| # | Finding | Sev |
|---|---|---|
| **O4** | Step 0 routed three rows to **mode 3**, which the same file defines as *"the GD's cost override, and the only one … replaces Step 0's gradient outright"*. The gradient cannot dispatch its own override. `orchestrator-direct-dispatch.md` still read *"neither is reached by sizing"* two rounds after those lane rows were added — stale in the file a router reads **on a return** | High |
| **O5** | The four values every entry carries had **no source** on the five of seven inputs with no ledger. `entry-index.md` says supply them from the ledger or return `Blocked`; `standalone-runs.md` patches it for **mode 2 only**. Read literally: `Blocked` on the commonest lane in the layer | High |
| **O6** | **The router declared no exits** while being the one file every terminal return passes through. D1/RP5/QA7's class, in the seventh file exactly as the debt register predicted | High |
| **O7** | **The gate-ask check could not see `orchestrator.md`.** Demonstrated: the forbidden sentence planted there **PASSed**; identical in `qa-pipeline.md` it **FAILed**. The one file the sentence names was outside the check's scope | High |
| **O8** | Closing a ledger was **claimed and never specified** — the ownership table says "opening and closing", the section describes only opening. **F7**'s class | Med-High |
| **O9** | **I9**'s lock-reclaim procedure was unreachable from the file that owns both locks, and **not one invariant was named by number** anywhere in the router's scope | Med-High |
| **O10** | A mode-3 optimisation at A5 has no reachable path to a measurement: `performance-qa-engineer` sits behind a door the router could not reach, and the direct lane forbids a second agent in terms | Med |
| **O11** | *"Runs on every input"* vs. the diagram routing named inputs around step 0 — **D13/RP14**'s class, in the diagram a reader follows first | Med |
| **O12** | Stale self-counts: "seven lanes" (11), "23 addressable entries" (24), "97 machine-checked claims" (98), and two debt rows claiming git/CI had no lane row when they did | Med |

### What round 2 found in round 1's own work

Six of thirteen. Stated plainly because the pattern matters more than the count:

| # | Defect round 1 introduced |
|---|---|
| **D1** | The change-request lane it added had **no decidable test** — nothing says how the router knows an approved spec exists |
| **D4** | That lane created a **strict ordering inversion**: the gated-direct row is its subset, six rows below it |
| **D5** | The new QA lane and the audit lane were separated only by a **word** — which the file's own reading rule forbids |
| **D7** | The diagram routed chores, questions and gated-direct work through a node reading *"write the feature's ledger · close it at CP4"*, while the reference written in the same round says most of what the router handles **has no ledger** |
| **D8** | The no-ledger attempt-budget row **stopped at D3**, leaving mode 3 — which has no D ceiling — with no value at all |
| **D11** | The diagram asserted *"the `Size` edges are in table order"* and listed the residue rows **reversed, inside that very edge** |

### What round 3's gate found in round 2's

| # | Finding | Sev |
|---|---|---|
| **F1** | **The flagship fix was incomplete in its own sibling.** The C3+ criterion went into `orchestrator.md`; `gated-direct-lane.md` condition 4 still read *"`Game.Core.*`, or multiplayer-relevant"*, under *"Fail any one and this lane is not available"* — so the lane went on refusing the input the criterion was added for | High |
| **F2** | Rows 1–3 outrank the criteria **by position**, so "rewrite the pushed commits that leaked the key" reaches `git-expert` — a class-B agent — with no gate, against `security.md`'s bar on self-remediation | High |
| **F8** | The new reachability check tested **6 of 24 doors**, missed `feature-intake.md` **E1**, and its scope took the whole `## Step 0` section, so the escape-upward *prose* satisfied it **with the lane table empty** | Med |
| F3–F7, F9–F17 | A fourth file stating the criteria count; a cell contradicting itself (*"none of it is"* vs *"two of those ten"*); `[int] ''` **aborting the run** under `ErrorActionPreference = 'Stop'`; an over-broad `no pipeline` exclusion exempting two whole lane rows; and nine smaller ones | Med/Low |

## Part 3 — What changed

**`references/orchestrator-exits-and-custody.md`** — new. Ten exit doors; the four-step ledger close and how
to reopen one; where the four values come from with no ledger; the **I9** reclaim; which of
`orchestration.md`'s ten invariants the router acts on; what a direct lane must never produce; and the one
case where depth genuinely is a second agent.

**`orchestrator.md`** — the lane table reordered **specific before general** with the three residue rows last
and three lanes added; a fifth **C3+** consequence-path criterion; the mode-3 category error corrected in all
three places; the diagram re-cut to branch on the real lane set and to route mode 2 through the source check;
one general rule replacing two hand-written carve-outs. **200/200 lines** — every addition paid for by
promotion or compression.

### Verifier: 98 → 107 claims, seven new checks, twenty-one negative tests

| Check | Closes | Negative-tested by |
|---|---|---|
| **Step 0 is ordered specific before general** | **The class of this round's own flagship defect.** The reorder fixed the instance; the check that followed counted *rows*, and counting cannot see order | The flagship defect **replanted** → FAIL · a destination row below a catch-all → FAIL · two specific rows swapped → **PASS**, the control |
| Every **GD-triggered door** has a step-0 lane | A pipeline declares a door the router cannot reach | 6 tests, incl. a renamed **table header** and a cross-cell split |
| Gate-ask scope includes `orchestrator.md` | A check blind to the file it is about | plant → FAIL · restore → PASS |
| Checklist states the lane count · entry count · **its own claim count** | Stale self-counts, three times in this series | 3 tests — the claim count caught two of this round's own edits mid-round |
| Every file states the same **escalation-criteria count** | Stated in four files, one auto-loaded | 4 tests, incl. **rewording the count away** |
| The exits reference states how many **invariants** it maps | Same class, third recurrence in one round | 4 tests, incl. splitting a two-ID row — must still **PASS**, since it counts IDs not rows |

**Four defects were found in this round's own checks, by running them rather than reading them:** the
gate-ask scope hole; the `no pipeline` exclusion (a markdown table row is one line, so it exempted two whole
lane rows); `[int] ''` throwing and **aborting the run**, silently skipping every later claim; and two literal
**backspace bytes** in a regex — self-inflicted while fixing a vacuous-pass defect, and which would have made
the trigger match nothing and pass vacuously.

**The seam grep caught two more of my own fixes being incomplete**: the truncated budget survived in the prose
of the file whose table I had just corrected, and the invariant table had **eight rows but nine IDs** while
the sentence above it said eight.

## Part 4 — Score

Self-marked after round 2: **8.6** — *down* from round 1's 8.7, because round 2 found six defects round 1 had
introduced. Round 3 was not self-marked; it was sent to the gate.

### `assurance-evaluator`, independent: **CONDITIONAL PASS**, weighted **8.9** against the A4 floor of 9.0

| Axis | Self | Independent | |
|---|---:|---:|---|
| Entry points and addressing | 9.0 | **9.5** | ↑ |
| Lane and sizing logic | 8.5 | **9.0** | ↑ |
| Mode logic | 9.0 | **9.0** | = |
| Result custody and exits | 9.0 | **9.0** | = |
| Counters and caps | 8.5 | **9.0** | ↑ |
| Self-description and honesty | 9.0 | **8.5** | ↓ |

**Six-axis mean 9.0.** The gate raised three axes and marked down **the one the round had scored itself
highest** — because it found the single §16 number nothing recounts was wrong: the verifier baseline read
**86**, which is §14's figure, where the true pre-round count is **98**. The round credited itself with +20
against a diff supporting +9. Measured independently by running the script against a clean `git archive HEAD`
tree, and corrected in place with the reason stated.

The gate declined to call it an integrity failure and the distinction is worth keeping: *the measurement ran,
the artifact is real, the delta was mis-stated.* That is inaccurate self-description, not a false verification
claim — but it lands on the round's own headline finding, which is why it cost the honesty axis.

Both of its conditions were closed: the baseline corrected, and the negative tests redirected to a log so
their outcomes are preserved rather than read off a console.

## Part 5 — Why 9.5 was not reached

The gate's read: **~9.2 is this file's ceiling by writing.** What more writing could close was closed —
the lane-ordering check, the general rule replacing two carve-outs, the logged tests. What remains is not
reachable here:

- **No lane has ever been taken on a real feature.** `.workflow/` does not exist; the ten exit doors, the
  four-step close, the **I9** reclaim and the no-ledger table are written and unrun.
- **Step 0 has been exercised only by agents reading it**, never by an orchestrator dispatching from it.
- **RP15** — 66 skills unloadable, GD-deferred, and already demonstrated to change an agent's technique choice.
- **No independent party has executed the verifier.** Both gates lack a shell; the counts rest on the
  author's run.

## Part 6 — The process finding worth keeping

Round 2 added the fifth criterion and did not carry it into `gated-direct-lane.md`, so the lane refused the
input it was written for until round 3's gate found it. **This project already had that lesson written down**
— *grep the seam after a cross-file fix; a routing fix on one side recurs on the other* — and it was not
applied. `execution-loop.md` is explicit that repeating an already-recorded mistake is worse than making a
novel one. One line of grep in round 2 would have saved a High finding a round later.
