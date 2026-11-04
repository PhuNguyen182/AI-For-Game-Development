# Skill template migration: spec

Author: `technical-architect`, attempt 1/1. M0 figures measured by the main session, replacing the architect's estimates.

## Measured (M0, 2026-11-02, fresh `claude -p /context`, 1M window)
| Source | Rows | Tokens capped | Tokens uncapped |
|---|---|---|---|
| Project | 126 | ~5.8k | ~10.0k |
| Plugin (unity) | 27 | ~0.6k | ~4.6k |
| claude.ai sync | 14 | ~0.8k | ~3.3k |
| Built-in | 17 | ~2.7k | ~2.7k |
| Plugin (superpowers) | 15 | ~0.5k | ~1.0k |
| Plugin (supabase) | 2 | ~0 | ~0.6k |
| **Total reported by `/context`** | 201 | **9.9k (1.0%)** | **22.1k (2.2%)** |

- **Name-only rows:** 109 capped (63 Project), 0 uncapped. No row is short by nature.
- **Project extras:** `project-audit` and `review-gate` are the two rows beyond the 124 folders.
- **Projection at ≤120 chars:** Project ~5k, total ~17k against a ~10k budget, so ~7k over. An estimate until M1.
- **200k window:** budget ~2k; no target fits. Not measured yet.

## Acceptance criteria
- **AC1 Descriptions:** all 124 have `description` + `when_to_use` ≤120 chars, double-quoted. Whole-layer count 0 for over-120, banned phrase and no-`Use`.
- **AC2 Drop fix:** on a 1M window with this machine's plugin set, a fresh `claude -p /context` shows zero rows `< 20` tokens, except rows deliberately name-only under the chosen lever. The Skills row stays at least 5% under the effective budget. Depends on Q1; with no lever this closes as an accepted gap.
- **AC3 200k recorded:** the same command on a 200k model is written to `Known limitations` with its row counts. No pass target.
- **AC4 Format:** whole-layer count 0 for `Latent concerns`, envelope bullets, reference or script table, hardcoded script path, script not named, list item over 200, body over 8,000, untitled item.
- **AC5 Moved code:** zero references hold a 15+ line fence (25 blocks in 23 files). Each moved file meets "Moved code" below.
- **AC6 Cited anchors:** every inventory row resolves to the same subject at the end. No `$HookContracts` failure. No skill folder or cited reference renamed or deleted.
- **AC7 No lost criteria:** each batch passes the comparator against `Base:`.
- **AC8 "ask":** every hit is classified and resolved per "Ask fix" below.
- **AC9 Sections:** each skill follows the template. The 22 without `## Steps` are classified pipeline, standard or method, or gain `## Steps`.
- **AC10 Promotion:** the promoted checks fail on a planted violation.
- **AC11 Regression:** `.claude/hooks/tests/run.ps1` and `test_mem.py` match their pre-edit baselines. Whole-layer verify prints `verify-layer: OK (21 warning(s))` with no `file(s):` line, except `body > 8000` for skills named at CP4.
- **AC4/AC11 amendment (T3.4):** the 8,000 is soft and the GD's rule forbids trimming a criterion to fit. A body may pass it when a comparator requires a real-money or consent check restored; each one is listed at CP4 for the GD to accept.
- **AC12 Docs:** `Docs owed` is complete.

## Tasks, in order
- **T0, main session:** M0. Done.
- **T1, `general-purpose`, `model: opus` (`verify.ps1` blocks every future edit):** baselines, anchor and "ask" inventories, token-survival tool, skill→batch table, classification of the 22, untitled-item check.
- **T2, `general-purpose`, `model: sonnet` (bulk mechanical work, `lean-skills` precedent):** description pass on all 124. A distinctive symbol held only in the description moves to the body. Comparator, commit, then M1.
- **T2b, main session:** apply the Q1 lever, then M2. This commit closes the reported bug before any body rewrite.
- **T3.1–T3.7, `general-purpose`, `model: sonnet` (same reason):** domain body batches, including moved code and "ask" fixes.
- **T4.1–T4.2, `general-purpose`, `model: opus` (hook contract holders, highest blast radius):** the 14 pipelines, `agent-protocol`, `csharp-standards`, `qa-standards`, `code-review-method`. They run last. `/release`'s cited step table stays. `feature` (12,677 chars) moves facts to references here; `iap-server-receipt-ledger` (8,746) does so in T3.4.
- **Comparator after every batch, `general-purpose`, `model: opus`, read-only by brief (a missed loss is silent and permanent):** never the batch's author.
- **T5, `general-purpose`, `model: opus` (same reason as T1):** promotion, `run.ps1` fixtures in a temp layout, docs owed.
- **Then:** CP3, gate offer, CP4. A large diff uses `review-gate`.

## Execution
- **Lanes:** `serial only`: mirror not adopted; `.claude/skills/` is no lane A path; `verify-on-edit.ps1` exits on worktree writes. Cost: wall-clock.
- **Parallel reading:** a read-only comparator may run beside the next writer.
- **Batches:** ≤16 skills, grouped by owning agent so skills that cite each other share a batch. T1 writes the exact table.
- **Budget:** each batch is one task with 4 attempts; a re-dispatch covers only the failing skills. Then `technical-architect` root-causes once, the owner gets one more dispatch, then stop.
- **Forward feed:** the same lost-criterion cause twice goes into all later batch briefs.
- **Commit:** per `/feature` step 4, after the batch's comparator passes.
- **Replaces compile check and test run:** `verify.ps1 -File` on each changed file prints no skill-format WARN, plus whole-layer exit 0.

## Cited anchors
- **Inventory:** T1 writes `.workflow/evidence/skill-template-migration/anchors.md` before any skill edit.
- **Scope searched:** `.claude/` (hooks included), `framework-docs/`, `README.md`, `CLAUDE.md`, `.memory/notes/`.
- **Patterns:** `(?i)\bsteps?\s+\d+`; `` `skill` → heading-or-file ``; `.claude/skills/<x>/references/<y>` paths; `$HookContracts`.
- **Row:** citing file:line | cited skill | anchor | subject at `Base:`.
- **Numbers:** a skill with any inbound or self citation keeps its step numbers.
- **New steps:** `Missing input` and `Final check` go after the last step.
- **Splits:** a step split under "fact per bullet" becomes nested titled bullets under the same number.
- **Headings:** a cited heading keeps its exact text.
- **Unavoidable renumbering:** the same attempt updates every citer and its inventory row.

## Comparator
- **Base:** `git show <Base sha>:<path>`, never moving `HEAD`.
- **Mechanical net:** `.workflow/evidence/skill-template-migration/token-survival.ps1`, local, not committed. Extracts backticked tokens, numbers with units, bold titles, URLs and link targets from each skill's `Base:` files; reports any absent from its current folder. Each must be explained.
- **Reading pass:** an independent read-only agent walks every `Base:` SKILL.md line in order.
- **A criterion is:** any line carrying a threshold, condition, ban, required order, output field, routing target, version caveat or exception.
- **Dispositions:** kept; moved to `file:line`; cut, naming a template class (Framing, Meta line, Common knowledge, Authoring note, Foreign output field, envelope field, guardrail restating step N).
- **Automatic finding:** a "Common knowledge" cut that held a number, version or gotcha.
- **Report:** `.workflow/evidence/skill-template-migration/batch-<n>/attempt-<k>/comparison.md`, only cuts, moves and resolved tokens.
- **Accounting:** the comparator is the batch's test run; a fail costs one attempt, not a review round.

## Moved code
- **Type:** an adapt file; the template offers only run or adapt.
- **Reference:** links `../scripts/x` and keeps its facts and short snippets.
- **SKILL.md:** lists the file only when usable without the reference.
- **Header:** what it shows; `Adapt into: <target path>`; `Unverified: not compiled or run (no Unity project in this repo).`
- **Content:** identical to the block at `Base:`; the comparator diffs it. Never trim a block to dodge the threshold.
- **Trap:** `git-unity-repo` `.gitattributes` sample becomes `unity.gitattributes`, because a file named `.gitattributes` goes live in that folder.
- **Trap:** `csharp-standards` review checks "all four references"; the link from `code-style-and-layout.md` keeps its sample reachable.

## Ask fix
- **Inventory:** regex `\b[Aa]sk(s|ed|ing)?\b`: 45 SKILL.md files, about 28 with an instruction. All classified; references get one pass.
- **Not an instruction:** unchanged, on the allowlist.
- **Missing input:** points to the `Missing input` step.
- **Strict ("never guess"):** as above, without the assumption branch.
- **Lenient ("flagged assumption"):** the full template step.
- **Asks a named role:** `Needs-decision`, `Next: <role>`.
- **Main-session pipeline:** names `AskUserQuestion`.
- **Approval before an action:** `AskUserQuestion` / `Needs-decision`.
- **Recommendation to a person:** a `Next:` or `Needs GD` output item.

## Promotion
- **To `Fail`, each once its count is 0:** banned phrase, no `Use` trigger, `Latent concerns`, envelope bullets, reference or script table, hardcoded script path, script not named, reference fence 15+, untitled item.
- **Stay `Warn`:** over-120, list item over 200, body over 8,000.
- **Order:** last, because `verify-on-edit.ps1` blocks on `Fail`.
- **Cleanup:** rename `Legacy` to `Soft`; drop the "when next touched" comment; fix the verify header.
- **Untitled-item check:** outside fences a list item matches `^\s*(?:-|\d+\.)\s+\*\*[^*]+:\*\*`; a non-empty line that is no heading, list item or table row is prose.

## Tests
| AC | Test | Mode | Owner |
|---|---|---|---|
| AC1 | Whole-layer verify counts | shell | T2 author, confirmed by main session |
| AC2 | M2 `/context` on 1M | shell | main session |
| AC3 | `/context` on 200k | manual: a recorded figure | main session |
| AC4 | Whole-layer verify counts | shell | T3, T4 authors, confirmed by main session |
| AC5 | Fence check plus block diff | shell + manual | batch comparator |
| AC6 | Anchor walk | manual | batch comparator; main session final walk |
| AC7 | `token-survival.ps1` plus report | shell + manual | batch comparator |
| AC8 | "ask" regex against allowlist | shell + manual | batch comparator |
| AC9 | Section walk | manual | batch comparator |
| AC10 | `run.ps1` fixtures | shell | T5 author |
| AC11 | `run.ps1`, `test_mem.py`, whole-layer verify | shell | main session |
| AC12 | Docs list walked at CP4 | manual | main session |

## Docs owed
- **`framework-docs/skill-template.md`:** Listing line if the budget changes; which checks now fail.
- **`verify.ps1` header, `verify-layer/SKILL.md`:** warn and fail statements.
- **`.memory/notes/feedback/skill-format.md`:** "no bulk pass" is now wrong.
- **`.workflow/framework-backlog.md`:** close the "Migrate skills" row.

## Out of scope
- The 21 agent and rule warnings.
- Agent and rule files, except a citer update.
- Plugin, built-in and synced skills.
- `skill-reference-template` fact tables; reference edits beyond moved code, links and "ask" fixes.
- Skill folder renames. Behaviour changes to any skill.

## Assumptions
- **Parallel writers:** the `lean-skills` precedent yields to `routing.md`.
- **Writer role:** `general-purpose`; its brief loads `agent-protocol` and `framework-docs/skill-template.md`.
- **Data tables:** tables other than `Reference|Script` may stay in SKILL.md bodies.
- **Reference scope:** "every item" format applies to SKILL.md; references follow `skill-reference-template`.
- **Tooling:** the token-survival tool stays local.
- **Reference deletion:** an unreferenced reference is flagged, not deleted, unless the comparator confirms it held nothing.
- **`/feature` step 4:** compile check and Unity test run are `n/a`, replaced as under "Execution".
- **Limit:** AC2 holds only on the 1M window and this machine's plugin set; a plugin update can re-break it.
