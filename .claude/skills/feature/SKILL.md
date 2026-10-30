---
name: feature
description: "Run an M/L feature from request to closure: size, CP1 (L), spec + CP2, Core first, serial build (optional worktree lanes) with compile check and UTF tests per agent, optional review and QA, CP4. Also handles change requests and abandonment."
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
- Ask before the spec only when the answer changes its shape (≤4 questions, one call). Everything else → the architect's `Assumptions:`, approved together at CP2.

## 2. CP1 — L only (and when the profile turns `critic` on)
1. `researcher` (Options) on the open design/architecture question.
2. GD picks one by name → `critic` attacks it.
3. GD locks it, or picks again. Record the pick and accepted risks under `GD decisions`.

## 3. Spec + CP2 — `technical-architect` (Spec mode)
- Profile decides full spec vs acceptance criteria only.
- `Open questions:` design → GD · architecture → the architect settles it · technology → `/decide` **only** when hard to reverse, paid, or a foundation (netcode, backend, ads, analytics); a cheap reversible choice (UI system, local save format, a tween library) is the architect's, using what the project already has.
- CP2 `AskUserQuestion`: approve / revise (what) / rethink direction (back to step 2). `Lanes:` not `serial only` → second question in the same call: Build mode serial (Khuyến nghị) / lanes, stating the cost — lane A loses the per-agent compile check, the GD closes and reopens the Editor once for the merge, a mirror pass is provisional until Edit Mode agrees. Answer → `Build mode:` and `GD decisions`.

## 4. Build — serial, one Editor holder at a time
Order, skipping roles the tasks omit:
`csharp-engineer` → `netcode-engineer` | `backend-engineer` → `technical-artist` → `gameplay-engineer` → `ui-engineer` → `unity-performance-engineer` (only when a budget is at risk). `sdk-platform-engineer` takes any slot.
- Third-party package / DLL / `.unitypackage` → `security-reviewer` first. A package, SDK or service added, removed or upgraded → `docs/tech-stack.md` in the same commit.
- Brief per `routing.md` → Dispatch, plus earlier returns' `Public contract:` / `Message contract:`, the agent's `Assemblies:` and `Tests:` rows.
- **Layout:** new code goes under `<feature root>/<Feature>/` (`CLAUDE.md` → Feature root, default `Assets/_Project/Scripts/`; `csharp-standards` → naming-convention.md → Folders). The first implementer on a layer creates that layer's asmdef and its `Tests/` asmdef from `Assemblies:`; the compile check confirms the assembly exists (`script eval` resolves a feature type in it).
- **Tests:** each implementer writes the UTF tests its `Tests:` rows name, in the same change as the code.
- **Compile check after every implementer:** `unity command script recompile` → poll `unity command script recompile_status` until `completed` → `unity command console status` (compile-failure flag) / `unity command console get --level error`. `up_to_date` does not prove the edits compiled — confirm a changed type exists (`script eval`). No Editor → `unity pipeline list` (Safe Mode?) and grep `Editor.log` for `error CS`. Errors → same agent, next attempt.
- **Test run after the compile check**, filtered to the agent's test assemblies, mode per assembly: Editor open → the configured MCP's test-run tool, polling its status tool until the run reports a result (`unity test` refuses a project open in an Editor); no such tool → `Needs GD: close the Editor` → `unity test <project> --mode EditMode|PlayMode -- -assemblyNames <assembly>` (it imports, compiles and writes the NUnit report) → `Needs GD: reopen it`; that costs the GD one close/reopen per implementer — say so at the first one. More than zero executed (`unity-test-framework` step 11). A failing or missing test → same agent, next attempt. Record each result in the feature file's `Tests` table.
- Commit per `git-commit`: stage only this feature's paths; another session's files stay out.
- Log each return under `Log`: agent, `Lane`, `Changed`, `Verified`, `Limitations`, `Needs GD` (tell the GD at once).

### Lanes — only when `Build mode: lanes`
1. `csharp-engineer` writes the `Contracts:` stubs, the Core/DataModels asmdefs and, with the mirror, the feature's `TestsDotnet/<Feature>/` csprojs in the main checkout → compile check → commit them with their `.meta` (`git-commit`). Lane A worktrees branch from that commit; lane B builds against the stubs.
2. Each lane A task (`Lanes:`) → `isolation: "worktree"`, dispatched in the same message as the next lane B agent. Brief adds: no Unity CLI or MCP call (hook `editor-lock.ps1` blocks them from a worktree); verify with `dotnet build` / `dotnet test` on the mirror, or the backend's own runner; feature docs (`README.md`, `CONTRACTS.md`) are lane B paths — lane A returns its doc entries in `Changed`, and the docs owner writes them after the merge.
3. A lane B test that exercises a lane A body → `pending merge` in the `Tests` table, not a failed attempt; it runs after the merge.
4. Merge once, after lane B's last agent: commit each worktree on its branch (`git-commit`) → `git-expert` merges with the Editor closed (`Needs GD: close the Editor`) → `Needs GD: reopen the Editor`, wait for the import → compile check → commit the `.meta` files Unity generated → the Edit Mode run compared with the mirror run (`core-tests-without-unity` step 7) and every `pending merge` test. A failure → the lane A owner, next attempt; caps unchanged. A merge needed earlier costs the GD one more Editor close — say so before asking.

## 5. Gate offer — one `AskUserQuestion`, two questions
Review? QA? Each: yes (Khuyến nghị) / no, with what skipping leaves unchecked (`routing.md` → Gates). Record the answers.
- Review yes → `/review` on the feature diff. Request changes → back to the author; the stop rule applies.
- No → `Known limitations`: "not reviewed" / "not QA'd".

## 6. CP3 — L only
`technical-architect` (CP3) → GD approves, or the named drift goes back to step 4 (+1 `rework`).

## 7. QA — only if chosen at step 5
`/qa <slug>`, the profile's recommended QA as its plan. Each defect → `/fix` with the bug id.

## 8. CP4 — `AskUserQuestion`
Show: each acceptance criterion → test id · mode · last result, or the gap (no passing test, `manual`) · open bugs · limitations · gates declined · what did not run.
Options: close / fix gaps first / accept named gaps (cost stated). A criterion without a passing test closes only as an accepted gap. Close → `Status: Closed`; each accepted gap into the feature root's `DEBT.md`.

## Change request (open feature past CP2; a closed feature takes new work instead)
- Halt new dispatches. `technical-architect` rates it: **Minor** → edit spec + criteria, continue · **Major** → CP2 again (CP1 if the direction moves).
- Rework list → step 4. Work already reviewed and unchanged keeps its verdict.

## Abandon
GD drops it → `Status: Abandoned`, why, last verified state. Open bugs → `Won't fix`.
