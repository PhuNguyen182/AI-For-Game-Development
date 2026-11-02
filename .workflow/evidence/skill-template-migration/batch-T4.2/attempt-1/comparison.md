# Comparison: batch T4.2, attempt 1

**Verdict: fail.** Failing: `investigate-device-crash`, `verify-layer`. Passing: `decide`, `new-project`, `plan-game`, `plan-test-coverage`, `resolve-merge-conflicts`, `review-code-risks`, `save-workmemory`.

Base: `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`. Read-only. No tracked file edited; the fixes below are not applied and not run.

## Findings
| # | Skill | Check | Base text | Current text | Why it fails |
|---|---|---|---|---|---|
| 1 | `investigate-device-crash` | Ask | `:13` "Ambiguous or fallback → confirm with the GD before pulling logs." | `SKILL.md:25` same words | An approval before an action in a main-session pipeline. The regex misses it on the word "confirm". Spec class "Main-session pipeline" and `core.md` ("Ask only via `AskUserQuestion`") both require the tool, and the same skill's other two asks (`:13`, `:20`) were converted. No behaviour change. |
| 2 | `verify-layer` | Plain words, shifted qualifier | `:31` "Fix the file, not the check — unless the check encodes the wrong rule; then say so." A closing line with no scope, under the whole table. | `SKILL.md:22` `4. **Failures:** fix the file, not the check — ...` | The title adds a limit Base never had. Soft checks warn, and the "check encodes the wrong rule; say so" exit applied to them too. The over-budget exception already has its own bullet (`:20`). |

## Exact fixes
**1. `.claude/skills/investigate-device-crash/SKILL.md:25`, replace with:**
```
   - **Ambiguous or fallback:** confirm with the GD via `AskUserQuestion` before pulling logs.
```

**2. `.claude/skills/verify-layer/SKILL.md:22`, replace with:**
```
4. **Fix target:** fix the file, not the check — unless the check encodes the wrong rule; then say so.
```

## Rulings asked for
- **`Status: Done | Blocked` in three Output fences: keep, all three.**
  - **`review-code-risks`:** no dispatched run exists. `code-reviewer.md:29`: "never invoke `review-code-risks` (its report is for the GD)". `code-review-method/SKILL.md:33` reads only `risk-patterns.md`. `project-audit.js:99` names the "lens" to `code-reviewer`, with its own `FINDINGS` schema. `resolve-merge-conflicts:68` applies the lens, no report.
  - **`plan-test-coverage`:** no agent runs it. `build-release-engineer.md:23` borrows its case format only.
  - **`investigate-device-crash`:** `fix/SKILL.md:26`, `routing.md:9`, `crash-anr-investigator.md:17` and `device-test-walkthrough` point or route to it; none dispatches it with an envelope.
  - **Corrections:** `batches.md:148` (owner `code-reviewer`) and the reason at `ask-inventory.md:74` ("`code-reviewer` loads this skill") are false. The `Missing input` step at `review-code-risks:26` stays: the inventory requires it, and its dispatched branch is harmless.
  - **Why keep:** each skill states "Final report to the GD", so no envelope exists to own the field. The brief's removal list names `Verified` and `Known limitations` only, and "Keep exactly" covers every output field. `investigate-device-crash:21` cites `Status: Blocked` (a correct result); cutting the field orphans it.
  - **Cost of each error:** keep and later dispatched → one duplicate line. Cut → the Done/Blocked outcome is lost from every GD report.
  - **Template conflict, for T5 (docs owed):** `framework-docs/skill-template.md:80` is absolute. Add after it: `- **No envelope:** a report the main session gives the GD has no envelope; its `Output` may keep a `Status:` line.`
- **`Verified on real device: yes` removed: holds, same force.** `investigate-device-crash:43` is unconditional, inside the step that writes the report, and carries the same claim. No other file reads the literal (grep over `.claude`, `framework-docs`, `README.md`). The lowercase form changes nothing. The Blocked case reads as it did at Base.
- **`investigate-device-crash` step 2 "confirm with the GD": an ask.** Finding 1.
- **`resolve-merge-conflicts`: pass.** Every clause of steps 1–12 and all four `Never` items located.
  - **Big and small:** `:32`–`:38` and `:39`–`:40`, including "the rest of the file still merges additively" and "never guess a winner".
  - **Preamble merged into step 11:** Base's "every 'ask' below" covered one sentence, step 11, the only "ask" at Base. `:76` holds both branches; `:12`–`:13` hold the report split.
  - **Once per operation:** `:76`; the carry-through and its "no big-scope decision" condition at `:77`.
  - **Step 10 title:** `Verify the resolution` keeps number and subject. Its one citer (`:43`) uses the number. The rename is not required by the hook: `round-cap.ps1:204` needs a `BUG-####` and no digit prefix. Harmless.
  - **Grep pattern, UnityYAMLMerge command, flags, exit codes:** byte-equal.
  - **`allowed-tools` (note only):** `Read, Grep, Glob, Edit`, no shell, while steps 1, 6, 10, 11 need git and Bash. Same at Base; frontmatter frozen. Candidate row for `.workflow/framework-backlog.md`; not written here.
- **`new-project`: pass.** Stages 1–9 in order with exact headings. Structure fence and perf table byte-identical (script diff). `references/tech-stack-template.md` still reached at `:70`, Base form; no `## References`, same as `feature` and `fix` in this class.
- **`decide`: pass.** Stage order and headings unchanged. Gates: "never skipped", spike condition, `AskUserQuestion` at `:14`, `:20`, `:25`.
- **`plan-game`: pass.** Stage order and headings unchanged. `Re-plan` at `:37`–`:38` keeps "steps 3–5", "changed part only", and repeats the condition on the second bullet. "The first two" correctly became `Prototype and Vertical slice` at `:18`. Fence byte-identical.
- **`verify-layer`: table text byte-identical; both commands ran.** With `${CLAUDE_SKILL_DIR}` substituted: whole layer exit 0 (21 warnings), `-File` exit 0 (0 warnings). Every row is true to current `verify.ps1`, subject to the T5 gaps below. Only finding 2 fails.
- **`save-workmemory`: pass.** `$ARGUMENTS` at `:11`. Every clause moved to steps 1–5.

## T5 gaps in `verify-layer` (not findings)
- **Row missing:** the untitled-item check (`verify.ps1:135`) is in no table row.
- **`Skill format` row, envelope:** says "envelope fields in `Output`". The check (`:128`) scans the whole body for `Verified` and `Known limitations` bullets only; `Status:` is unchecked, so the three kept lines stay clean after promotion.
- **`Skill format` row, narrower than stated:** the table check (`:129`) matches only a first header cell `Reference` or `Script`; the path check (`:130`) only the skill's own folder.
- **`Fail`s in no row:** `$HookContracts` strings (`:36`); retired namespace (`:211`); state under `.claude/` (`:221`); no frontmatter, name != folder, no description (`:264`–`:266`); `.claude/commands` (`:299`).
- **`Warn` in no row:** an agent's backticked unknown name (`:257`).
- **False after promotion:** `SKILL.md:21` "fixed when next touched"; `verify.ps1:18` comment; the `(soft)` labels on `Skill format` and `Skill references`. Already docs owed.

## Tokens
- **Tool run:** 9 skills, 309 tokens, 1 missing. Matches the author's report.
- **`Android/iOS`:** confirmed. Base `SKILL.md:3` description compound, T2. Body keeps `[android|ios]` (`:12`), `Android source` (`:27`), `iOS commands` (`:32`).
- **Word comparison (own script):** per-skill Base word counts against current. Every drop traced to a rewording or expanded reference (`that skill's` → the skill name; `the first two` → names; `ask` → `AskUserQuestion`). No lost condition.

## Moves
| Skill | Base | Now |
|---|---|---|
| `investigate-device-crash` | Output `Verified on real device: yes` | Step 5 `:43`; `Not covered` stays in the fence |
| `resolve-merge-conflicts` | Preamble "every 'ask' below is `Status: Needs-decision`" | Step 11 `:76` |
| `review-code-risks` | Step 1 "Both empty → ask" | `:20` plus `Missing input` `:26` |
| `verify-layer` | Command fence | `## Scripts` `:10`–`:11` |
| `verify-layer` | Prose | Steps 2–4 `:15`–`:22` |
| `verify-layer` | Table under the H1 | Same text under new `## Checks` `:24` |
| `save-workmemory` | Prose | Steps 1–5 |
| `plan-test-coverage`, `investigate-device-crash`, `review-code-risks` | Report fence inside the last step | `## Output`, text otherwise unchanged |

## Cuts
None. No criterion cut under a template class; `Verified on real device` moved, it was not cut.

## Other checks
- **Anchors:** all rows for these skills resolve to the same subject: `investigate-device-crash` 1, 3; `new-project` 4, 5, 9; `plan-game` 3, 5; `resolve-merge-conflicts` 1, 3, 5, 6, 9, 10, 11; `risk-patterns.md`. Outbound: `git-unity-repo` step 10, `git-safety-anchor` stash row (`anchor-and-undo-recipes.md:53`), `/feature` step 4.
- **Ask:** `40 hit(s), 38 allowlisted, 2 in resolved form, 0 open`. Each inventory fix applied. Unused rows are `qa` and `release`, not this batch.
- **Moved code:** none in this batch; no reference changed.
- **Sections:** match `batches.md`: 3 pipelines keep stage headings, 6 gain `## Steps`.
- **Scope:** frontmatter equals `HEAD` on all 9. `git status` shows only these 9 plus untracked `.workflow/`.
- **Verify:** `-File` on each of the 9: 0 warnings. Largest body: `resolve-merge-conflicts` 7,788 chars.
