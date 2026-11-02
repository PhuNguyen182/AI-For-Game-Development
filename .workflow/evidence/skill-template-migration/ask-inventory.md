# "ask" inventory at Base

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`, read through `git show`.
- **Regex:** `\b[Aa]sk(s|ed|ing)?\b`, whole file, frontmatter included. `AskUserQuestion` is not a hit.
- **SKILL.md:** 62 hits in 45 files; 34 instruction hits in 28 files.
- **References:** 18 hits; 6 instruction hits.
- **Check:** `pwsh -NoProfile -File ask-check.ps1 [-Skills a,b]` compares live files against `ask-allowlist.txt`. A hit passes when its line holds an allowlisted fragment for that file, or names `AskUserQuestion` or `Needs-decision`.
- **Allowlist form:** `<path under .claude/skills>|<fragment>`, one per line. A fragment, not the whole line, so a reformat of a sentence that keeps its wording still matches. `unused allowlist row` in the output means the sentence is gone: confirm that was meant.
- **Rule used for examples:** an `Example` line that narrates a past ask is not an instruction; the matching step holds the instruction.
- **Rule used for descriptions:** a frontmatter hit is not an instruction; T2 may reword it and the row then shows as unused.

## Counts

| Class (spec "Ask fix") | SKILL.md | References |
|---|---|---|
| Not an instruction | 28 | 12 |
| Missing input | 5 | 0 |
| Strict | 10 | 0 |
| Lenient | 2 | 0 |
| Asks a named role | 2 | 0 |
| Main-session pipeline | 10 | 0 |
| Approval before an action | 3 | 3 |
| Recommendation to a person | 2 | 3 |
| **Total** | **62** | **18** |

## SKILL.md hits

| Skill:line | Class | Intended fix |
|---|---|---|
| `anti-cheat-strategy:18` | Not an instruction | none: on the allowlist. |
| `ci-pipeline-failure-triage:42` | Recommendation to a person | `Next:` item: keep logs as artifacts on every run, green ones too; the reason stays. |
| `ci-pipeline-failure-triage:46` | Recommendation to a person | `Next:` item naming the re-run and what it would establish. |
| `code-review-method:23` | Not an instruction | none: on the allowlist. |
| `code-search:23` | Approval before an action | `AskUserQuestion` in the main session, `Needs-decision` when dispatched, before any of the three commands. |
| `consent-att-init-order:30` | Not an instruction | none: on the allowlist. |
| `core-scene-integration:24` | Not an instruction | none: on the allowlist. |
| `crash-anr-reporting-gate:20` | Strict | `Missing input` step without the assumption branch; "Set up a while ago" stays a No. |
| `cross-platform-expansion-assessment:25` | Not an instruction | none: on the allowlist. |
| `decide:11` | Not an instruction | none: on the allowlist. |
| `decide:13` | Not an instruction | none: on the allowlist. |
| `decide:14` | Main-session pipeline | already names `AskUserQuestion`; no change needed. |
| `dotween-tweening:40` | Not an instruction | none: on the allowlist. |
| `dotween-tweening:51` | Not an instruction | none: on the allowlist. |
| `engineering-standard-adr-authoring:15` | Not an instruction | none: on the allowlist. |
| `feature:27` | Main-session pipeline | "`AskUserQuestion` before the spec only when ...", limits kept (≤4 questions, one call). |
| `feature:57` | Main-session pipeline | say so in the `AskUserQuestion` that requests it. |
| `fix:20` | Main-session pipeline | already names `AskUserQuestion`; no change needed. |
| `flexalon-layouts:27` | Missing input | "Unstated → `Missing input` step"; adds that step. |
| `git-commit:27` | Not an instruction | none: on the allowlist. |
| `git-forensics:18` | Not an instruction | none: on the allowlist. |
| `git-forensics:21` | Strict | `Missing input` step without the assumption branch; "never pick one" stays. |
| `git-forensics:29` | Not an instruction | none: on the allowlist. |
| `git-recovery:17` | Not an instruction | none: on the allowlist. |
| `git-unity-repo:23` | Asks a named role | `Needs-decision`, `Next: gameplay-engineer`, when unstated. |
| `git-unity-repo:32` | Missing input | "Unity version unstated → `Missing input` step"; adds that step. |
| `investigate-device-crash:10` | Main-session pipeline | infer what is missing; still ambiguous → `AskUserQuestion`. |
| `investigate-device-crash:12` | Main-session pipeline | disambiguate from `$1`, else `AskUserQuestion`. |
| `live-ops-content-pipeline:12` | Not an instruction | none: on the allowlist. |
| `magiconion-rpc-networking:18` | Not an instruction | none: on the allowlist. |
| `netcode-for-entities:40` | Strict | `Missing input` step without the assumption branch; the reason (code comes to depend on the guess) stays. |
| `netcode-for-gameobjects:24` | Asks a named role | `Needs-decision`, `Next: technical-architect`; "never pick silently" stays. |
| `new-project:45` | Not an instruction | none: on the allowlist. |
| `new-project:53` | Not an instruction | none: on the allowlist. |
| `osa-optimized-scrollview-adapter:26` | Missing input | "Unstated → `Missing input` step", the four inputs stay listed; step number 2 stays, the new step goes last. |
| `performance-budget-verification:45` | Not an instruction | none: on the allowlist. |
| `plan-test-coverage:12` | Main-session pipeline | None resolves → `AskUserQuestion`; "never guess scope" stays. |
| `qa:3` | Not an instruction | none: on the allowlist. |
| `qa:12` | Main-session pipeline | `AskUserQuestion` now; the yes and no branches stay. |
| `qa:13` | Main-session pipeline | `AskUserQuestion` now; recording the answer in each brief stays. |
| `release:3` | Not an instruction | none: on the allowlist. |
| `render-pipeline-urp-hdrp:21` | Strict | `Missing input` step without the assumption branch; "a person decides" stays. |
| `resolve-merge-conflicts:10` | Approval before an action | drop the quoted "ask" mapping: dispatched → `Needs-decision`, main session → `AskUserQuestion`. |
| `resolve-merge-conflicts:22` | Approval before an action | `AskUserQuestion` / `Needs-decision` before `git commit` or `--continue`; "once per operation" stays. |
| `review-code-risks:12` | Strict | `Missing input` step without the assumption branch; "never scan the whole repo" stays (`code-reviewer` loads this skill, so not main-session only). |
| `review:25` | Main-session pipeline | already names `AskUserQuestion`; "ask the author" becomes a re-dispatch of the author with the question. |
| `review:34` | Not an instruction | none: on the allowlist. |
| `secret-exposure-response:29` | Not an instruction | none: on the allowlist. |
| `secret-exposure-response:33` | Not an instruction | none: on the allowlist. |
| `shader-authoring:22` | Strict | `Missing input` step without the assumption branch, naming the reference image, comparable or parameter. |
| `shader-authoring:27` | Not an instruction | none: on the allowlist. |
| `technology-scouting-sweep:14` | Not an instruction | none: on the allowlist. |
| `technology-scouting-sweep:24` | Not an instruction | none: on the allowlist. |
| `ugui:26` | Lenient | full template `Missing input` step; "flagged assumption" becomes its assumption branch. |
| `ui-toolkit:28` | Lenient | full template `Missing input` step; "flagged assumption" becomes its assumption branch; step number 2 stays. |
| `unity-collections:20` | Strict | `Missing input` step without the assumption branch; "guessing picks the wrong container" stays. |
| `unity-entities-graphics:23` | Strict | `Missing input` step without the assumption branch; "never infer" stays. |
| `unity-hdrp-rendering:30` | Missing input | "Scope unstated → `Missing input` step"; adds that step. |
| `unity-mathematics:27` | Strict | `Missing input` step without the assumption branch; "before writing" stays. |
| `unity-urp-rendering:21` | Missing input | "Tier unstated → `Missing input` step"; adds that step. |
| `vfx-particle-authoring:56` | Not an instruction | none: on the allowlist. |
| `zstring-zero-allocation-strings:14` | Strict | `Blocked` naming the capture needed, the wording `zlinq-zero-allocation-linq` step 1 already uses. |

## Reference hits

| Skill:line | Class | Intended fix |
|---|---|---|
| `ci-pipeline-failure-triage/references/unity-batchmode-log-signatures.md:41` | Recommendation to a person | `Next:` item: the clean-run comparison. |
| `consent-att-init-order/references/google-ump.md:95` | Not an instruction | none: on the allowlist. |
| `crash-anr-fault-domain-triage/references/third-party-and-engine-escalation.md:21` | Not an instruction | none: on the allowlist. |
| `csharp-standards/references/coding-principles.md:19` | Not an instruction | none: on the allowlist. |
| `csharp-standards/references/coding-principles.md:22` | Not an instruction | none: on the allowlist. |
| `firebase-unity-sdk/references/setup-edm4u.md:31` | Not an instruction | none: on the allowlist. |
| `git-forensics/references/attribution-honesty.md:68` | Not an instruction | none: on the allowlist. |
| `git-recovery/references/history-surgery.md:26` | Recommendation to a person | `Needs GD: freeze pushes until step 5`. |
| `git-recovery/references/interrupted-and-overwritten-state.md:48` | Recommendation to a person | `Needs GD`: provider retention decides; "never assume" stays. |
| `git-unity-repo/references/routine-workflows.md:14` | Approval before an action | "merge, or `AskUserQuestion` / `Needs-decision`". |
| `git-unity-repo/references/routine-workflows.md:26` | Approval before an action | `AskUserQuestion` / `Needs-decision` first; the `core.md` citation stays. |
| `git-unity-repo/references/routine-workflows.md:44` | Not an instruction | none: on the allowlist. |
| `git-unity-repo/references/routine-workflows.md:56` | Approval before an action | `AskUserQuestion` / `Needs-decision` first; the `core.md` citation and `/release` stay. |
| `iap-server-receipt-ledger/references/app-store-server-api.md:56` | Not an instruction | none: on the allowlist. |
| `netcode-for-gameobjects/references/core-architecture.md:16` | Not an instruction | none: on the allowlist. |
| `osa-optimized-scrollview-adapter/references/pooling-and-performance.md:20` | Not an instruction | none: on the allowlist. |
| `unity-tilemap/references/tile-palette-and-tiles.md:9` | Not an instruction | none: on the allowlist. |
| `unity-urp-rendering/references/renderer-features-and-passes.md:15` | Not an instruction | none: on the allowlist. |
