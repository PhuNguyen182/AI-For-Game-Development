---
name: feature
description: "Run an M/L feature from request to closure: size, CP1 direction (L), spec + CP2, Core first, serial client build with a compile check after each agent, review, QA, CP4. Also handles change requests and abandonment."
argument-hint: "<the request, in the GD's words>"
---

# /feature

The main session runs this and is the only writer of the feature file. Rules: `routing.md`, `core.md`.

## 0. Open
- Slug = kebab-case name. `.workflow/features/<slug>.md` exists → resume at its `CP:` line. Never a second file for one feature.
- New → copy `references/feature-template.md`; paste the GD's words verbatim; Profile from `CLAUDE.md`. No `.workflow/bugs.md` → create it from `/fix`'s template.
- Every GD answer → `GD decisions` at once; an accepted gap or risk also → `Known limitations` in the same edit.

## 1. Size — `technical-architect` (Spec mode, size only)
- State `Size` + `Risk flag` in one line. S → do it directly, delete the file; the reply closes it.
- A point that changes what gets built is unclear → one `AskUserQuestion` (≤4 questions). Otherwise list it as an assumption.

## 2. CP1 — L only (and when the profile turns `critic` on)
1. `researcher` (Options) on the open design/architecture question.
2. GD picks one by name → `critic` attacks it.
3. GD locks it, or picks again. Record the pick and accepted risks under `GD decisions`.

## 3. Spec + CP2 — `technical-architect` (Spec mode)
- Profile decides full spec vs acceptance criteria only.
- `Open questions:` design → GD · architecture → the architect settles it · technology → `/decide` **only** when hard to reverse, paid, or a foundation (netcode, backend, ads, analytics); a cheap reversible choice (UI system, local save format, a tween library) is the architect's, using what the project already has.
- CP2 `AskUserQuestion`: approve / revise (what) / rethink direction (back to step 2).

## 4. Build — serial, one Editor holder at a time
Order, skipping roles the tasks omit:
`csharp-engineer` → `netcode-engineer` | `backend-engineer` → `technical-artist` → `gameplay-engineer` → `ui-engineer` → `unity-performance-engineer` (only when a budget is at risk). `sdk-platform-engineer` takes any slot.
- Third-party package / DLL / `.unitypackage` → `security-reviewer` first.
- Brief per `routing.md` → Dispatch, plus earlier returns' `Public contract:` / `Message contract:`.
- **Compile check after every implementer:** `unity command script recompile` → poll `unity command script recompile_status` until `completed` → `unity command console status` (compile-failure flag) / `unity command console get --level error`. No Editor → `unity pipeline list` (Safe Mode?) and grep `Editor.log` for `error CS`. Errors → same agent, next attempt.
- Log each return under `Log`: agent, `Changed`, `Verified`, `Limitations`, `Needs GD` (tell the GD at once).

## 5. Review — automatic for M/L or the risk flag
`/review` on the feature diff. Request changes → back to the author; the stop rule applies.

## 6. CP3 — L only
`technical-architect` (CP3) → GD approves, or the named drift goes back to step 4.

## 7. QA
`/qa <slug>`. Profile default QA is the floor. Each defect → `/fix` with the bug id.

## 8. CP4 — `AskUserQuestion`
Show: each acceptance criterion → evidence | gap · open bugs · limitations · what did not run.
Options: close / fix gaps first / accept named gaps (cost stated). Close → `Status: Closed`; accepted gaps into the feature's `DEBT.md`.

## Change request (feature past CP2)
- Halt new dispatches. `technical-architect` rates it: **Minor** → edit spec + criteria, continue · **Major** → CP2 again (CP1 if the direction moves).
- Rework list → step 4. Work already reviewed and unchanged keeps its verdict.

## Abandon
GD drops it → `Status: Abandoned`, why, last verified state. Open bugs → `Won't fix`.
