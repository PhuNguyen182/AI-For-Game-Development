---
name: feature
description: "Run an M/L feature from request to closure: size, CP1 (per profile), spec + CP2, a feature branch, serial build (optional lanes) with compile check and UTF tests per agent, optional review and QA, CP4. Also handles change requests and abandonment."
argument-hint: "<the request, in the GD's words>"
---

# /feature

The main session runs this and is the only writer of the feature file. Rules: `routing.md`, `core.md`.
**Every git write in this skill** (each commit, the CP4 merge) first checks `git branch --show-current` equals `Branch:` (from step 4 on) — a lane A worktree commit instead checks `git -C <worktree> branch --show-current` equals that `Worktrees:` entry's branch; else stop, `Needs GD` — another session moved the shared checkout's HEAD.
**Feature paths** (used below): the feature root, `TestsDotnet/<Feature>/`, every path in an attempt's brief or `Changed`, with their `.meta` — never `.workflow/`.

## 0. Open
- Slug = kebab-case name. `.workflow/features/<slug>.md` exists → resume at its `CP:` line. Never a second file for one feature.
- **Owner check first:** its `Session:` line or `.workflow/editor.lock` names another session, under 3 h old → no stash, no dispatch; `AskUserQuestion`: wait (Khuyến nghị) / take over. Otherwise write your own `Session:`.
- **Resume inside step 4:**
  - `next step: verify <agent> …` → the return is logged: resume at its compile check; not a failed attempt.
  - A `Log` row `in flight` → that attempt was interrupted: `git-expert` anchors and runs `git stash push -u -m "<slug> attempt <n> interrupted" -- <feature paths>` with the Editor closed; count it failed; re-dispatch with the stash ref in the brief. Lanes: one `in flight` row per lane.
  - Each `Worktrees:` entry: its agent returned `Done` → finish it (Lanes step 4); otherwise `AskUserQuestion` → `git-expert` removes it, the answer quoted in its brief (radius 3).
  - A foreign Editor lock → `unity command editor status` → `AskUserQuestion` before deleting `.workflow/editor.lock`.
  - `git branch --show-current` ≠ `Branch:` → `git-expert` switches to it when the tree is clean and no other session is live; otherwise `AskUserQuestion`.
- New → copy `references/feature-template.md`; Request = the GD's words verbatim (from a backlog item: its row and GDD section); Profile from `CLAUDE.md`; the `.workflow/backlog.md` row → `in progress`. No `.workflow/bugs.md` → create it from `/fix`'s template.
- Every GD answer → `GD decisions` at once; an accepted gap or risk also → `Known limitations` in the same edit.

## 1. Size — `technical-architect` (Size mode)
- State `Size` + `Risk flag` in one line; a size other than the backlog row's → update the row. S → do it directly, delete the file; the reply closes it.
- Ask before the spec only when the answer changes its shape (≤4 questions, one call). Everything else → the architect's `Assumptions:`, approved together at CP2.

## 2. CP1 — runs per `routing.md` → Profile defaults → CP1 + `critic`
- No open direction question (the GD already set it) → `CP1: n/a (direction given: …)` under `GD decisions`, go to step 3.
1. `researcher` (Options) on the open design/architecture question. A foundation question (netcode, backend, ads, analytics) → `/decide` here, the GD's design pick as its constraint.
2. GD picks one by name (unranked options, `core.md`) → `critic` attacks it.
3. GD locks it, or picks again. Record the pick and accepted risks under `GD decisions`.

## 3. Spec + CP2 — `technical-architect` (Spec mode)
- Profile decides full spec vs acceptance criteria only. Long → `.workflow/features/<slug>.spec.md`.
- `Open questions:` design → GD · architecture → the architect settles it · technology → `/decide` **only** when hard to reverse, paid, or a foundation (netcode, backend, ads, analytics); a cheap reversible choice (UI system, local save format, a tween library) is the architect's, using what the project already has. `/decide` mid-spec → `CP: CP2 — next step: /decide <q>`; afterwards re-dispatch the architect with the decision and its previous return.
- CP2 `AskUserQuestion`: approve / revise (what) / rethink direction (back to step 2 when it runs for this size and profile, else re-size at step 1). `Lanes:` not `serial only` → second question in the same call: Build mode serial (Khuyến nghị) / lanes, stating the cost — lane A loses the per-agent compile check, the GD closes and reopens the Editor once for the merge, a mirror pass is provisional until Edit Mode agrees. Answer → `Build mode:` and `GD decisions`. A multiplayer feature approved → `Multiplayer: yes` in `CLAUDE.md`.

## 4. Build — serial, one Editor holder at a time
Start: `git-expert` creates the local branch `feature/<slug>` from the current branch → `Branch:`, `Base:` (another session's `Session:` live under 3 h → `AskUserQuestion` before any branch switch: the checkout is shared). Order, skipping roles the tasks omit:
`csharp-engineer` → `netcode-engineer` | `backend-engineer` → `technical-artist` → `gameplay-engineer` → `ui-engineer` → `unity-performance-engineer` (only when a budget is at risk). `sdk-platform-engineer` takes any slot.
- Third-party package / DLL / `.unitypackage` → `security-reviewer` first. A package, SDK or service added, removed or upgraded → `docs/tech-stack.md` in the same commit.
- Brief per `routing.md` → Dispatch with `Feature: .workflow/features/<slug>.md`, plus earlier returns' `Public contract:` / `Message contract:`, the agent's `Assemblies:` (the asmdefs it is named creator of) and `Tests:` rows; the last implementer's brief also carries `Docs owed:`.
- **Before every dispatch:** `CP: build — next step: <agent> attempt <n>/<budget>` and a `Log` row `in flight`. **On its return:** replace the row, then `next step: verify <agent> attempt <n> (compile, tests, commit)`. Attempts count per task across re-dispatches (`routing.md` → Stop rule).
- **Layout:** new code goes under `<feature root>/<Feature>/` (`CLAUDE.md` → Feature root, default `Assets/_Project/Scripts/`; `csharp-standards` → naming-convention.md → Folders). Each asmdef is created by the creator `Assemblies:` names; the compile check confirms the assembly exists (`script eval` resolves a feature type in it).
- **Tests:** each implementer writes the UTF tests its `Tests:` rows name, in the same change as the code.
- **Compile check after every implementer:** `unity command script recompile` → poll `unity command script recompile_status` until `completed` → `unity command console status` (compile-failure flag) / `unity command console get --level error`. `up_to_date` does not prove the edits compiled — confirm a changed type exists (`script eval`). No Editor → `unity pipeline list` (Safe Mode?) and grep `Editor.log` for `error CS`. Errors → same agent, next attempt; errors only in files outside this attempt's `Changed` → not an attempt, `Needs GD` (another session's work).
- **Test run after the compile check**, filtered to the agent's test assemblies, mode per assembly: Editor open → the configured MCP's test-run tool, polling its status tool until the run reports a result (`unity test` refuses a project open in an Editor); no such tool → `Needs GD: close the Editor` → `unity test <project> --mode EditMode|PlayMode -- -assemblyNames <assembly>` (it imports, compiles and writes the NUnit report) → `Needs GD: reopen it`; that costs the GD one close/reopen per implementer — say so at the first one. More than zero executed (`unity-test-framework` step 11). Only for an agent with `Tests:` rows; none (technical-artist, the Lanes stub pass) → `Tests: n/a` in its `Log` row. A failing or missing test → same agent, next attempt. Record each result in the feature file's `Tests` table.
- **Commit** after each implementer's compile check and test run pass — the main session, per `git-commit` (the `core.md` exception), on `feature/<slug>` — first `git branch --show-current` must equal `Branch:`, else stop, `Needs GD` (another session moved HEAD): stage only this feature's paths; another session's files stay out. Never push. Then `next step:` the next agent.
- Log each return under `Log`: agent, `Lane`, `Changed`, `Verified`, `Attempts n/N`, `Limitations`, `Needs GD` (tell the GD at once). Refresh `Session:` at every CP or Log write.

### Lanes — only when `Build mode: lanes`
1. `csharp-engineer` writes the `Contracts:` stubs, the Core/DataModels asmdefs and, with the mirror, the feature's `TestsDotnet/<Feature>/` csprojs in the main checkout → compile check → commit them with their `.meta` (`git-commit`). Lane A worktrees branch from that commit; lane B builds against the stubs.
2. Each lane A task (`Lanes:`) → `isolation: "worktree"`, dispatched in the same message as the next lane B agent; record its path, branch and task under `Worktrees:`; `CP:` names both lanes' next steps. Brief adds: no Unity CLI or MCP call (hook `editor-lock.ps1` blocks them from a worktree); verify with `dotnet build` / `dotnet test` on the mirror, or the backend's own runner; feature docs (`README.md`, `CONTRACTS.md`) are lane B paths — lane A returns its doc entries in `Changed`, and the docs owner writes them after the merge.
3. A lane B test that exercises a lane A body → `pending merge` in the `Tests` table, not a failed attempt; it runs after the merge.
4. Merge once, after lane B's last agent: commit each worktree on its branch (`git-commit`) → `git-expert` merges into `feature/<slug>` with the Editor closed (`Needs GD: close the Editor`) → `Needs GD: reopen the Editor`, wait for the import → compile check → commit the `.meta` files Unity generated → the Edit Mode run compared with the mirror run (`core-tests-without-unity` step 7) and every `pending merge` test. A failure → the lane A owner, next attempt; caps unchanged. A merge needed earlier costs the GD one more Editor close — say so before asking.

## 5. Gate offer — one `AskUserQuestion`, two questions
Review? QA? Each: yes (Khuyến nghị) / no, with what skipping leaves unchecked (`routing.md` → Gates). Record the answers.
- Review yes → `/review` on the feature diff. Request changes → back to the author; the stop rule applies.
- No → `Known limitations`: "not reviewed" / "not QA'd".
- **Rework after this point** (review send-back, CP3 drift, a QA fix, CP4 fix-gaps): back to step 4 for the named items, then — not a new offer — `/review` on the rework diff (`Previous tree:`, the feature's next `Round:`) when review was chosen, CP3 again for L, the affected QA cases again when QA was chosen.

## 6. CP3 — L only
`technical-architect` (CP3) → GD approves, or the named drift goes back to step 4 (+1 `rework`, written in the file), then step 5's rework rule.

## 7. QA — only if chosen at step 5
`/qa <slug>`, the profile's recommended QA as its plan. Each defect → `/fix` with the bug id.

## 8. CP4 — `AskUserQuestion`
Show: each acceptance criterion → test id · mode · last result, or the gap (no passing test, `manual`) · `Docs owed` → written / missing · open bugs · limitations · gates declined · what did not run.
Options: close / fix gaps first / accept named gaps (cost stated). A criterion without a passing test closes only as an accepted gap.
- Fix gaps → step 4 with the gap criteria as tasks for their `Tests:` owner (+1 `rework`, written in the file), then step 5's rework rule, then CP4 again.
- Close → `Status: Closed`; each accepted gap into the feature root's `DEBT.md`; the backlog row → `done`; the closure commit (`DEBT.md`, the feature file, `backlog.md`; the `core.md` exception). Second question in the same CP4 call: merge `feature/<slug>` into `Base:` now via `git-expert` (Khuyến nghị) / keep the branch. Never push. Then offer the next backlog item — the first `todo` whose dependencies are `done` (`/plan-game`).

## Change request (open feature; a closed feature takes new work instead)
- Append the GD's words under `## Request` as `Change <n> (<date>)`; set `CP: CP2 — next step: rate change <n>`; halt new dispatches.
- Before CP2 → re-dispatch the architect with the change (back to step 2 if the direction moves); no counter.
- Past CP2 → `technical-architect` rates it: **Minor** → edit spec + criteria, continue · **Major** → CP2 again (CP1 if the direction moves); `CP:` stays at CP2 until approved.
- Rework list → step 4, each item a new task `<task> rev <n>` with a fresh attempt budget. Work already reviewed and unchanged keeps its verdict. The architect lists the criteria the change touches: their `Tests` rows → `stale`, re-run by their owner. A change to `Contracts:` during lanes → finish or remove the open worktrees, re-stub, branch again.

## Abandon
GD drops it → `Status: Abandoned`, why, last verified state. Open bugs → `Won't fix`. The backlog row → `dropped`. `Worktrees:` entries removed (`git-expert`). `AskUserQuestion`: delete `feature/<slug>` via `git-expert` (Khuyến nghị) / keep it, with a `DEBT.md` entry naming the dormant code.
