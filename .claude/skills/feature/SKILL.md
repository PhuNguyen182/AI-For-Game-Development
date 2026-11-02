---
name: feature
description: "M/L feature pipeline, request to closure, with CP gates and change requests. Use for any M/L feature."
argument-hint: "<the request, in the GD's words>"
---

# /feature

- **Writer:** the main session runs this and is the only writer of the feature file.
- **Rules:** `routing.md`, `core.md`.
- **Every git write in this skill:** each commit, the CP4 merge, first checks `git branch --show-current` equals `Branch:` (from step 4 on).
  - **Lane A commit:** a lane A worktree commit instead checks `git -C <worktree> branch --show-current` equals that `Worktrees:` entry's branch.
  - **Mismatch:** else stop, `Needs GD` — another session moved the shared checkout's HEAD.
- **Feature paths (used below):** the feature root, `TestsDotnet/<Feature>/`, every path in an attempt's brief or `Changed`, with their `.meta` — never `.workflow/`.

## 0. Open
- **Slug:** kebab-case name.
- **Existing file:** `.workflow/features/<slug>.md` exists → resume at its `CP:` line. Never a second file for one feature.
- **Owner check first:** the feature file's `Session:` line or `.workflow/editor.lock` names another session, under 3 h old → no stash, no dispatch.
  - **Other session:** `AskUserQuestion`: wait (Khuyến nghị) / take over.
  - **No other session:** otherwise write your own `Session:`.
- **Resume inside step 4:**
  - **`next step: verify <agent> …`:** the return is logged: resume at its compile check; not a failed attempt.
  - **A `Log` row `in flight`:** that attempt was interrupted.
    - **Stash:** `git-expert` anchors and runs `git stash push -u -m "<slug> attempt <n> interrupted" -- <feature paths>` with the Editor closed.
    - **Attempt:** count it failed; re-dispatch with the stash ref in the brief.
    - **Lanes rows:** one `in flight` row per lane.
  - **Each `Worktrees:` entry:** its agent returned `Done` → finish it (Lanes step 4); otherwise `AskUserQuestion` → `git-expert` removes it, the answer quoted in its brief (radius 3).
  - **A foreign Editor lock:** `unity command editor status` → `AskUserQuestion` before deleting `.workflow/editor.lock`.
  - **`git branch --show-current` ≠ `Branch:`:** `git-expert` switches to it when the tree is clean and no other session is live; otherwise `AskUserQuestion`.
- **New:** copy `references/feature-template.md`.
  - **Request:** the GD's words verbatim (from a backlog item: its row and GDD section).
  - **Profile:** from `CLAUDE.md`.
  - **Backlog row:** the `.workflow/backlog.md` row → `in progress`.
  - **Bugs file:** no `.workflow/bugs.md` → create it from `/fix`'s template.
- **GD answers:** every GD answer → `GD decisions` at once; an accepted gap or risk also → `Known limitations` in the same edit.

## 1. Size — `technical-architect` (Size mode)
- **State:** `Size` + `Risk flag` in one line.
- **Backlog row:** a size other than the backlog row's → update the row.
- **S:** do it directly, delete the file; the reply closes it.
- **Questions:** `AskUserQuestion` before the spec only when the answer changes its shape (≤4 questions, one call).
- **Everything else:** the architect's `Assumptions:`, approved together at CP2.

## 2. CP1 — runs per `routing.md` → Profile defaults → CP1 + `critic`
- **No open direction question:** the GD already set it → `CP1: n/a (direction given: …)` under `GD decisions`, go to step 3.

1. **Options:** `researcher` (Options) on the open design/architecture question.
   - **Foundation question:** a foundation question (netcode, backend, ads, analytics) → `/decide` here, the GD's design pick as its constraint.
2. **Pick:** GD picks one by name (unranked options, `core.md`) → `critic` attacks it.
3. **Lock:** GD locks it, or picks again. Record the pick and accepted risks under `GD decisions`.

## 3. Spec + CP2 — `technical-architect` (Spec mode)
- **Spec form:** profile decides full spec vs acceptance criteria only.
- **Long spec:** long → `.workflow/features/<slug>.spec.md`.
- **`Open questions:`:** routed by kind:
  - **Design:** → GD.
  - **Architecture:** → the architect settles it.
  - **Technology:** → `/decide` **only** when hard to reverse, paid, or a foundation (netcode, backend, ads, analytics).
  - **Cheap reversible technology:** a cheap reversible choice (UI system, local save format, a tween library) is the architect's, using what the project already has.
- **`/decide` mid-spec:** `CP: CP2 — next step: /decide <q>`; afterwards re-dispatch the architect with the decision and its previous return.
- **CP2 `AskUserQuestion`:** approve / revise (what) / rethink direction (back to step 2 when it runs for this size and profile, else re-size at step 1).
- **Build mode question:** `Lanes:` not `serial only` → second question in the same call: Build mode serial (Khuyến nghị) / lanes, stating the cost:
  - **Compile cost:** lane A loses the per-agent compile check.
  - **Editor cost:** the GD closes and reopens the Editor once for the merge.
  - **Mirror cost:** a mirror pass is provisional until Edit Mode agrees.
- **Build mode answer:** answer → `Build mode:` and `GD decisions`.
- **Multiplayer:** a multiplayer feature approved → `Multiplayer: yes` in `CLAUDE.md`.

## 4. Build — serial, one Editor holder at a time
- **Start:** `git-expert` creates the local branch `feature/<slug>` from the current branch → `Branch:`, `Base:`.
  - **Shared checkout:** another session's `Session:` live under 3 h → `AskUserQuestion` before any branch switch: the checkout is shared.
- **Order:** skipping roles the tasks omit:
  - **Chain:** `csharp-engineer` → `netcode-engineer` | `backend-engineer` → `technical-artist` → `gameplay-engineer` → `ui-engineer` → `unity-performance-engineer`.
  - **`unity-performance-engineer`:** only when a budget is at risk.
  - **`sdk-platform-engineer`:** takes any slot.
- **Third-party content:** third-party package / DLL / `.unitypackage` → `security-reviewer` first.
- **Tech stack:** a package, SDK or service added, removed or upgraded → `docs/tech-stack.md` in the same commit.
- **Brief:** per `routing.md` → Dispatch with `Feature: .workflow/features/<slug>.md`.
  - **Brief additions:** earlier returns' `Public contract:` / `Message contract:`, the agent's `Assemblies:` (the asmdefs it is named creator of) and `Tests:` rows.
  - **Last implementer:** the last implementer's brief also carries `Docs owed:`.
- **Before every dispatch:** `CP: build — next step: <agent> attempt <n>/<budget>` and a `Log` row `in flight`.
- **On its return:** replace the row, then `next step: verify <agent> attempt <n> (compile, tests, commit)`.
- **Attempts:** attempts count per task across re-dispatches (`routing.md` → Stop rule).
- **Layout:** new code goes under `<feature root>/<Feature>/` (`CLAUDE.md` → Feature root, default `Assets/_Project/Scripts/`; `csharp-standards` → naming-convention.md → Folders).
  - **Asmdefs:** each asmdef is created by the creator `Assemblies:` names; the compile check confirms the assembly exists (`script eval` resolves a feature type in it).
- **Tests:** each implementer writes the UTF tests its `Tests:` rows name, in the same change as the code.
- **Compile check after every implementer:** commands, the `up_to_date` trap and the no-Editor path per [build-checks.md](references/build-checks.md).
  - **Errors:** errors → same agent, next attempt.
  - **Foreign errors:** errors only in files outside this attempt's `Changed` → not an attempt, `Needs GD` (another session's work).
- **Test run after the compile check:** filtered to the agent's test assemblies, mode per assembly; commands per [build-checks.md](references/build-checks.md).
  - **Editor open:** the configured MCP's test-run tool, polling its status tool until the run reports a result (`unity test` refuses a project open in an Editor).
  - **No such tool:** `Needs GD: close the Editor` → `unity test` → `Needs GD: reopen it`.
  - **Editor cost:** that costs the GD one close/reopen per implementer — say so at the first one.
  - **Executed count:** more than zero executed (`unity-test-framework` step 11).
  - **Which agents:** only for an agent with `Tests:` rows; none (technical-artist, the Lanes stub pass) → `Tests: n/a` in its `Log` row.
  - **Failing test:** a failing or missing test → same agent, next attempt.
  - **Results:** record each result in the feature file's `Tests` table.
- **Commit:** after each implementer's compile check and test run pass — the main session, per `git-commit` (the `core.md` exception), on `feature/<slug>`.
  - **Branch check:** first `git branch --show-current` must equal `Branch:`, else stop, `Needs GD` (another session moved HEAD).
  - **Staging:** stage only this feature's paths; another session's files stay out.
  - **Push:** never push.
  - **Next agent:** then `next step:` the next agent.
- **Log:** log each return under `Log`: agent, `Lane`, `Changed`, `Verified`, `Attempts n/N`, `Limitations`, `Needs GD` (tell the GD at once).
- **Session line:** refresh `Session:` at every CP or Log write.

### Lanes — only when `Build mode: lanes`
1. **Stubs:** `csharp-engineer` writes the `Contracts:` stubs, the Core/DataModels asmdefs and, with the mirror, the feature's `TestsDotnet/<Feature>/` csprojs in the main checkout.
   - **Stub commit:** compile check → commit the stubs, asmdefs and csprojs with their `.meta` (`git-commit`).
   - **Branching:** lane A worktrees branch from that commit; lane B builds against the stubs.
2. **Lane A tasks:** each lane A task (`Lanes:`) → `isolation: "worktree"`, dispatched in the same message as the next lane B agent.
   - **Record:** record its path, branch and task under `Worktrees:`; `CP:` names both lanes' next steps.
   - **Brief adds, Editor:** no Unity CLI or MCP call (hook `editor-lock.ps1` blocks them from a worktree).
   - **Brief adds, verification:** verify with `dotnet build` / `dotnet test` on the mirror, or the backend's own runner.
   - **Brief adds, docs:** feature docs (`README.md`, `CONTRACTS.md`) are lane B paths — lane A returns its doc entries in `Changed`, and the docs owner writes them after the merge.
3. **Pending tests:** a lane B test that exercises a lane A body → `pending merge` in the `Tests` table, not a failed attempt; it runs after the merge.
4. **Merge once, after lane B's last agent, in this order:**
   - **Worktree commits:** commit each worktree on its branch (`git-commit`).
   - **Merge:** `git-expert` merges into `feature/<slug>` with the Editor closed (`Needs GD: close the Editor`).
   - **Reopen:** `Needs GD: reopen the Editor`, wait for the import.
   - **After the import:** compile check → commit the `.meta` files Unity generated.
   - **Test comparison:** the Edit Mode run compared with the mirror run (`core-tests-without-unity` step 7) and every `pending merge` test.
   - **Failure:** a failure → the lane A owner, next attempt; caps unchanged.
   - **Earlier merge:** a merge needed earlier costs the GD one more Editor close — say so in the `AskUserQuestion` that requests it.

## 5. Gate offer — one `AskUserQuestion`, two questions
- **Questions:** Review? QA? Each: yes (Khuyến nghị) / no, with what skipping leaves unchecked (`routing.md` → Gates).
- **Answers:** record the answers.
- **Review yes:** `/review` on the feature diff.
- **Request changes:** back to the author; the stop rule applies.
- **No:** `Known limitations`: "not reviewed" / "not QA'd".
- **Rework after this point:** review send-back, CP3 drift, a QA fix, CP4 fix-gaps: back to step 4 for the named items, then, not a new offer:
  - **Review again:** `/review` on the rework diff (`Previous tree:`, the feature's next `Round:`) when review was chosen.
  - **CP3 again:** CP3 again for L.
  - **QA again:** the affected QA cases again when QA was chosen.

## 6. CP3 — L only
- **Built vs spec:** `technical-architect` (CP3) → GD approves, or the named drift goes back to step 4 (+1 `rework`, written in the file), then step 5's rework rule.

## 7. QA — only if chosen at step 5
- **Run:** `/qa <slug>`, the profile's recommended QA as its plan.
- **Defects:** each defect → `/fix` with the bug id.

## 8. CP4 — `AskUserQuestion`
- **Show:**
  - **Criteria:** each acceptance criterion → test id · mode · last result, or the gap (no passing test, `manual`).
  - **Docs:** `Docs owed` → written / missing.
  - **Open items:** open bugs · limitations · gates declined · what did not run.
- **Options:** close / fix gaps first / accept named gaps (cost stated).
- **Gap rule:** a criterion without a passing test closes only as an accepted gap.
- **Fix gaps:** step 4 with the gap criteria as tasks for their `Tests:` owner (+1 `rework`, written in the file), then step 5's rework rule, then CP4 again.
- **Close:** `Status: Closed`; each accepted gap into the feature root's `DEBT.md`; the backlog row → `done`.
  - **Closure commit:** the closure commit (`DEBT.md`, the feature file, `backlog.md`; the `core.md` exception).
  - **Merge question:** second question in the same CP4 call: merge `feature/<slug>` into `Base:` now via `git-expert` (Khuyến nghị) / keep the branch.
  - **Push:** never push.
  - **Next item:** then offer the next backlog item — the first `todo` whose dependencies are `done` (`/plan-game`).

## Change request (open feature; a closed feature takes new work instead)
- **Record:** append the GD's words under `## Request` as `Change <n> (<date>)`; set `CP: CP2 — next step: rate change <n>`; halt new dispatches.
- **Before CP2:** re-dispatch the architect with the change (back to step 2 if the direction moves); no counter.
- **Past CP2:** `technical-architect` rates it:
  - **Minor:** edit spec + criteria, continue.
  - **Major:** CP2 again (CP1 if the direction moves); `CP:` stays at CP2 until approved.
- **Rework list:** step 4, each item a new task `<task> rev <n>` with a fresh attempt budget.
- **Reviewed work:** work already reviewed and unchanged keeps its verdict.
- **Touched criteria:** the architect lists the criteria the change touches: their `Tests` rows → `stale`, re-run by their owner.
- **`Contracts:` change:** a change to `Contracts:` during lanes → finish or remove the open worktrees, re-stub, branch again.

## Abandon
- **GD drops it:** `Status: Abandoned`, why, last verified state.
- **Open bugs:** `Won't fix`.
- **Backlog row:** the backlog row → `dropped`.
- **Worktrees:** `Worktrees:` entries removed (`git-expert`).
- **Branch:** `AskUserQuestion`: delete `feature/<slug>` via `git-expert` (Khuyến nghị) / keep it, with a `DEBT.md` entry naming the dormant code.
