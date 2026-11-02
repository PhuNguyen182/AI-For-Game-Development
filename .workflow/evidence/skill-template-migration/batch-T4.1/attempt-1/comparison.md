# Comparison: batch T4.1, attempt 1

**Verdict: fail.** Failing: `feature`, `fix`, `release`, `csharp-standards`. Passing: `agent-protocol`, `qa`, `review`, `qa-standards`, `code-review-method`.

Base: `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`. T4.1 files last written 14:24, unchanged during this comparison.

## Findings
| # | Skill | Check | Base text | Current text | Why it fails |
|---|---|---|---|---|---|
| 1 | `feature` | Criteria, plain words | "the configured MCP's test-run tool, polling its status tool until the run reports a result (`unity test` refuses a project open in an Editor)" | `feature/SKILL.md:92` "the configured MCP's test-run tool."; the rest at `build-checks.md:11` | Line 91 points to the reference for "commands". Polling is a stop condition, not a command, and an MCP run needs no `unity` command, so this path has no reason to open the reference. An early read gives a result-less `Tests` row. |
| 2 | `feature` | Criteria, required order | "commit each worktree … → `git-expert` merges … → `Needs GD: reopen the Editor`, wait for the import → compile check → commit the `.meta` files … → the Edit Mode run compared" | `feature/SKILL.md:117-122`: unordered bullets, the arrows gone | Required order lost in form. Only line 121 still says what follows what. |
| 3 | `fix` | Reach | "Compile check as in `/feature` step 4", commands inline there | `fix/SKILL.md:44` same words; commands now at `feature/references/build-checks.md` | `/fix` does not have `feature` loaded and now needs two hops, the second one unnamed. |
| 4 | `release` | Plain words | Description: "then ask before tag, push or submit" | No sentence. T2 reworded the description. | The ban holds only by structure: the `AskUserQuestion` in the `Finish` heading, the tag + push option, `release/SKILL.md:54` for store submission, and `core.md`. The stated order "gate first, then ask" is gone from the skill. |
| 5 | `csharp-standards` | Invented claim | Fence only: `[SerializeField] private float cooldown` | `code-style-and-layout.md:8` "`[SerializeField]` goes before the access modifier." | Base never stated this as a rule. The token `[SerializeField] private` on the same line already keeps the fact. |

## Exact fixes
**1. `.claude/skills/feature/SKILL.md:92`, replace with:**
```
  - **Editor open:** the configured MCP's test-run tool, polling its status tool until the run reports a result (`unity test` refuses a project open in an Editor).
```
**1b. `.claude/skills/feature/references/build-checks.md:11`:** delete the line (`- **Configured MCP:** ...`), so the fact is said once. Line 91's "commands per" then holds for the one remaining bullet.

**2. `.claude/skills/feature/SKILL.md:117`, replace with:**
```
4. **Merge once, after lane B's last agent, in this order:**
```
**3. `.claude/skills/fix/SKILL.md:44`, replace with:**
```
- **Compile check:** as in `/feature` step 4; commands in `feature` → build-checks.md.
```
**4. `.claude/skills/release/SKILL.md`, insert before line 49:**
```
- **Tag, push, submit:** none of them runs before this `AskUserQuestion`.
```
The line does not trip `ask-check` (`AskUserQuestion` has no word boundary after `Ask`). The allowlist row `release/SKILL.md|then ask before tag` stays unused, because the sentence was in the description.

**5. `.claude/skills/csharp-standards/references/code-style-and-layout.md:8`, replace with these two lines (one line would be 208 chars):**
```
- **Sample:** [AbilityRunner.cs](../scripts/AbilityRunner.cs).
  - **Shows:** `public sealed class`, `private const`, `[SerializeField] private`, a `private` field, a `public` expression-bodied property, a `private` method.
```

## Decision: the move to `build-checks.md`
**Safe; do not restore,** with fixes 1 and 3 applied. The spec prescribes the move ("`feature` moves facts to references here").
- **Moment of need:** `feature/SKILL.md:88` and `:91` link the reference at the exact step, and line 88 names the `up_to_date` trap and the no-Editor path. Resume line 23 leads to the compile check.
- **Compaction:** the whole body survives (next section), so the link does too. A dropped `Read` of the reference can be repeated.
- **Moved intact:** every command, `up_to_date`, `script eval`, `unity pipeline list`, `Editor.log`, `error CS`, the `unity test` form and its parenthetical are present.
- **Stayed in the body:** foreign errors, Editor cost, zero-executed, which agents, failing test, results table.

## `feature` against 5,000 tokens
**Fits in full on the installed CLI; it would not fit on a literal token count.**
- **Measured body:** 14,195 chars, confirming the author's figure. After fixes 1, 2: about 14,300.
- **Actual cut (installed CLI 2.1.316, read from its bundled JS):** `function jfr(e,n){if(pc(e)<=n)return e;let r=n*4-nXn.length;return e.slice(0,r)+nXn}`, called with `Afr=5000`; combined budget `s8e=25000`. The cut is at about 20,000 chars. `feature` is under it, so nothing is truncated whatever `pc` estimates.
- **Estimated tokens by the CLI's chars×4 budget:** about 3,550 of 5,000.
- **Real tokens:** about 5,570, from a median 2.55 chars per token across `.md` single-`Read` turns in this project's subagent transcripts (opus-5-5, line-number prefixes included; approximate).
- **If a later CLI counted real tokens:** the cut falls near char 12,750, about `feature/SKILL.md:155`. `## Change request` and `## Abandon` would be lost, and neither is cited as critical to resume. Nothing in step 0 to step 8's merge question would go.
- **Not a finding today.** `feature` still warns `body > 8000`: list it at CP4 (AC11).
- **Combined budget:** older invoked skills drop first past 25,000 estimated tokens. Unchanged from Base.

## Hook strings: pass
Walked `.claude/hooks/round-cap.ps1`. `verify.ps1 -File` passes on all `$HookContracts` strings.

| Hook reads | Emitted at |
|---|---|
| `Round:` | `review:16`, `:57`; "each on its own line" kept at `review:15` |
| `Tree:` / `Previous tree:` | `review:21`, `:23`, `:57` |
| `Mode: audit` / `workflow` / `test-code` | `review:19`, `review:32`, `qa:29` |
| `Feature:` (unguarded in `review`, `feature`) | `review:18`, `feature:79`, `qa:12`, `qa:22`, `fix:19` |
| `Bug:` / `Target:` | `review:18`, `fix:19`; `release:22`, `:35` for the scan |
| `Verify: BUG-####` | `agent-protocol:52`, `qa:31`, `fix:51`, `release:22` |
| `Repro: BUG-#### reproduces \| gone` | `agent-protocol:52` |
| `Verdict:`, `Request changes`, `Blocked`, `Not signed off` | `review:43`, `:61`, `code-review-method:70`, `qa:41`; agent files untouched |
| `round-<n>-<first 12 chars of Tree>`, `rounds.json` keys (unguarded) | `review:22`, `:17`, `:34` |
| `Rounds:`, `Review rounds:` (unguarded in skills) | `review:17`, `:33`, `fix:47` |
| `- Status: Open`, `- Size:`, `- Rounds:`, `## GD decisions`, `- Stop rule:`, `- Fix rounds:`, `- Review rounds:`, statuses | `feature-template.md`, `bugs-template.md`, `bug-lifecycle.md`: not modified |

**Author's `Get-Marker` concern: not a risk for T4.1.**
- **T4.1 lines:** no line in any T4.1 skill matches `^[\s*_>-]*(Mode|Feature|Bug|Target|Round|Tree|Verify|Verdict|Repro)[*_]*:`. The titles `Round line`, `Target line`, `Tree line`, `Audit line`, `Feature paths`, `Bug verification brief` all fail the pattern on the extra word.
- **Preloaded skills:** they cannot reach `$brief`. The hook takes the first `type:user` transcript line. In 264 of 264 subagent transcripts that line is the brief; preloads follow as `isMeta` lines. One brief holds a literal `<command-name>` in its text and is not a preload.
- **Agent files:** `- **Mode:**`, `- **Round:**`, `- **Target:**` exist in agent files at Base and go to the system prompt.

**Other batches, committed, only if quoted into a brief ahead of the real marker:**
- **`stateless-state-machines/SKILL.md:20`:** `- **Bug:** a bug reduces to ...` would shadow a real `Bug:` (first match wins, then fails `^BUG-\d{4,}`). Fix: `   - **Bug shape:** a bug reduces to "in two states at once".`
- **`odin-inspector/SKILL.md:36`, `secret-exposure-response/SKILL.md:22`:** `- **Verify:**` is harmless; the regex needs `BUG-\d{4,}`.

## Questions from the dispatch
- **`review:50` "re-dispatch the author with the question":** same meaning, kept, per `ask-inventory.md`. The main session can only reach an agent by dispatch at Base too. One edge: `routing.md` counts "re-dispatches of the same task" as attempts; a question is not the same task, so I read it as uncharged. No text change.
- **`release` table:** verbatim by diff.
- **`build-checks.md` lead-in:** not a finding. "Synthesized from ..." is the `skill-reference-template.md` form, also in 4 Base references. The second sentence is true of `fix:44`.
- **Title `Built vs spec` (`feature:138`):** not invented; `routing.md` says "CP3 built vs spec".
- **Title `routed by kind` (`feature:56`):** not invented; it names the design / architecture / technology split and adds no fact.

## Moves
- **`feature/SKILL.md` step 4 → `feature/references/build-checks.md`:** compile commands, `up_to_date`, no-Editor path, `unity test` form. The MCP polling returns to the body under fix 1.
- **`code-style-and-layout.md` fence → `csharp-standards/scripts/AbilityRunner.cs`:** body byte-identical (`cmp`), 15 lines; 3-line header meets the brief; target `Views/` per the brief.
- **`csharp-standards` table → `## References` bullets:** triggers kept.

## Cuts
None in any SKILL.md body. Every Base line of the 9 skills was walked: kept, or moved as above, except the findings.

## Resolved tokens
- **Tool output:** 625 tokens, 1 missing.
- **`analytics/IAP` (`release`):** explanation confirmed. T2 description compound; both parts are in table row 7, which is verbatim.
- **`feature` tokens in the reference:** confirmed present in `build-checks.md`.
- **`csharp-standards` fence:** holds no extractable token; confirmed by the byte comparison.

## Other checks
- **Exact by diff:** `agent-protocol` envelope; tables in `code-review-method`, `qa-standards`, `release`.
- **Frontmatter:** all 9 equal `HEAD`.
- **Headings:** `feature`, `fix`, `qa`, `review`, `release` equal Base.
- **Order:** `code-review-method` 1–9 and `Lanes` 1–4 keep number and subject.
- **Anchors:** all rows for these skills resolve to the same subject, including `Mode`, `Asset names` (`csharp-standards/SKILL.md:11`), "A claim is verified only when", "A finding has", `release` rows.
- **Ask:** scoped run: 5 hits, 4 allowlisted, 1 resolved, 0 open. Unused rows `release/SKILL.md|then ask before tag` and `qa/SKILL.md|when the GD asks` are frontmatter, per the inventory.
- **Sections:** match the `batches.md` classes.
- **`verify.ps1 -File`:** no skill-format WARN; `feature` shows only `body > 8000`.

## Outside this batch
- **Foreign commits on the branch:** `2ffcce1` (14:35), `6bd65f4` (14:39) and `e791c78` (14:41), not T4.1, for the Game Engineer output style and its `README.md` section. Another session is live in the shared checkout: stage only T4.1's paths.
- **Whole-layer verify moved during this run:** exit 1 twice (1, then 4 failures, on `README.md` citing the gitignored `.claude/settings.local.json`), then exit 0, `verify-layer: OK (21 warning(s))`, after `e791c78`. No failure named a T4.1 file. Re-run it before the T4.1 commit.
