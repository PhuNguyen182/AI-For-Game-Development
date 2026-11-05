---
name: advisory-protocol
description: "Adviser rules: evidence labels, data pack, Advisory-Return format, never decide. Use for any advisory read."
user-invocable: false
---

# Advisory protocol

- **Not for:** the return envelope itself (`agent-protocol`), storage commands (`mem`).
- **Applies to:** `product-owner`, `game-designer`, `monetization-designer`, and the three workflows that dispatch them.

## Scripts
- **[check_pack.py](scripts/check_pack.py):** run `<python> -I "${CLAUDE_SKILL_DIR}/scripts/check_pack.py" <pack folder>` → exit 0 clean, 1 problems, 2 cannot check.

## Evidence labels
- **Rule:** every number in a return carries one label, written right after the number.

| Label | Form | Requires |
|---|---|---|
| Measured | `[measured: <pack file>, <date range>, <build>]` | A row in the data pack |
| Benchmark | `[benchmark: <url>, <retrieved date>, <tier>]` | A source graded per `source-credibility-grading` |
| Assumption | `[assumption: <reasoning>]` | The reasoning, and what would replace it |
| Proposed | `[proposed]` | A candidate's new value: a design choice, not an estimate |

- **Computed figures:** a computed figure takes its weakest input's label: assumption is weaker than benchmark, benchmark than measured.
- **Proposed values:** stay out of that rule; name them beside the figure.
- **Unlabelled number:** invalidates the return; the main session sends it back.
- **Design parameters:** a value in the GDD or the project's config is cited by path and needs no label.

## Data pack
- **Location:** `.memory/advisory/data/<period>/`, git-ignored.
- **Contents:** `manifest.md` (source, date range, filters, build versions) plus aggregated CSV or TSV files.
- **Gate:** the main session runs `check_pack.py` before any brief names a pack; a failed pack reaches no agent.
- **No pack:** no figure can be `measured`, and no return may conclude anything about revenue; state what to measure instead.

## Brief markers
- **Who:** the main session writes these lines; the capture hook and `adv.py` read them.
- **Workflow line:** `Workflow:` then `/product-review`, `/design`, `/monet` or `/feature`.
- **Thread line:** `Advisory-Thread:` then a kebab-case topic; follow-ups keep it.
- **Other agents:** any agent whose brief carries the thread line is captured off git too (`critic`, `researcher`).
- **Period line:** `Data-Period:` then the pack's folder name, or `none`.
- **Target line:** `Target:` then what is being read, when the read has one.

## Return
- **Shape:** the `agent-protocol` envelope, then this exact line and the findings:

```
Advisory-Return: v1

### F<n> [Critical | High | Medium | Low] <title>
Evidence: <what you read, each number labelled>
Player effect: <what the player feels or does differently>
Business effect: <retention, revenue or scope consequence> | none
Recommendation: <one action>
Cost: <what acting costs, and what skipping costs>
Settled by: <the test, data or decision that would settle it>
```

- **Heading:** `### F<n>` numbers from 1; `adv.py` splits findings on it, so each gets a decision.
- **Nothing found:** write what you tested against, with no `### F` heading.
- **Severity:** Critical breaks the stated goal; High needs rework of a decided part; Medium is an unpriced cost; Low changes nothing now.

## Off-git rule
- **Rule:** advice and observed figures live in the advisory store, never in git.
- **Capture:** a hook stores each return verbatim; never copy a return into a file.
- **Tracked files:** GDD, `docs/monetization-plan.md`, feature files and backlog hold decisions, design parameters and targets, plus `adv:<id>` references. Never an observed figure.
- **Main session text:** findings shown to the main GD go between these two lines, each alone on its line, so the trace keeps a pointer instead:

```
<!-- advisory:begin -->
<!-- advisory:end -->
```

- **`AskUserQuestion`:** its text reaches traces, so it names findings by `adv:<id>` and holds no observed figure.
- **Lost return:** after each dispatch `adv list --thread <thread>` must show it. Missing → tell the main GD, keep the text out of files.

## Never
- **Deciding:** adviser output is advice; only the main GD decides, and nothing here blocks a pipeline.
- **Reading another adviser:** a first read never sees another adviser's opinion; that independence is why these are separate agents.
- **Judging fun:** an agent cannot feel a game; state what the evidence shows and what a playtest would settle.
- **Dark patterns:** recommending pressure on minors, hidden costs, or anything that breaks store policy or `CLAUDE.md` → Compliance.
- **Player data:** quoting one player's row; packs hold aggregates only.

## Example
- **"Retention will rise about 5% with this change":** declined — no label and no source; wrote `D7 11.2% [measured: retention.csv, 2026-10, 1.4.0]`, stated the change as a hypothesis, and named the A/B test that settles it.
