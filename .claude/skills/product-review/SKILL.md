---
name: product-review
description: "Independent reads by product-owner, game-designer, monetization-designer; conflicts shown, gaps to backlog. Use at milestone exit."
argument-hint: "[scope or milestone]"
---

# /product-review

- **Writer:** the main session runs this; rules in `advisory-protocol`.
- **Not for:** code audits (`/review`), test evidence (`/qa`), one quick question (one adviser under `routing.md` → Question).

## 1. Prepare
- **Thread:** a kebab-case `Advisory-Thread:`, e.g. `milestone-2-exit`.
- **Inputs:** `CLAUDE.md`, the GDD, `records.py backlog render`, `debt render`, each feature root's `DEBT.csv`, `csv render limitations --feature <slug>` per open feature.
  - **Render output:** goes in the brief: advisers have no shell.
- **Data pack:** a pack under `.memory/advisory/data/` → `check_pack.py` first; failed → name the problems and stop using that pack. None → `Data-Period: none`.
- **Past advice:** `adv q "<scope words>"`, and bring earlier decisions into the brief by id.

## 2. See the actual game
- **Playtest evidence exists:** cite its paths in the brief.
- **None:** `AskUserQuestion`: run `playtest-tester` first (Khuyến nghị) / read docs and code only.
- **Docs and code only:** the report says so in its first line and makes no claim about feel.

## 3. Independent reads
- **Dispatch:** `product-owner`, `game-designer` and `monetization-designer` in one message, read-only and parallel.
- **Same brief:** goal, `Workflow: /product-review`, `Advisory-Thread:`, `Data-Period:`, scope, inputs. No adviser sees another's return.
- **Stored check:** `adv list --thread <thread>` shows all three; a lost return per `advisory-protocol`.
- **Unlabelled number:** send that return back once.

## 4. Merge
- **Dedupe and rank:** by severity, keeping each finding's `adv:<id>`.
- **Conflict:** two advisers disagreeing stays a conflict: both positions and the cost of each. Never averaged.
- **Show:** the table between the advisory markers (`advisory-protocol` → Off-git rule).

## 5. Discuss
- **`AskUserQuestion`:** which findings enter the backlog, which to probe, by `adv:<id>`.
- **Follow-up:** continue the same agent with `SendMessage`; it unavailable → a fresh dispatch with its earlier return in the brief and the same thread.
- **Cap:** 2 follow-up rounds per adviser per thread (`adv rounds <thread>`); past it, the main GD orders another or the discussion closes.

## 6. Close
- **Decisions:** `adv decide <id> accepted|rejected|deferred --by 'main GD' --note <why>` for each finding the main GD ruled on.
- **Usefulness:** the main GD marks findings `adv useful <id> yes|no`; under half of an adviser's findings in a run marked useful → revise that adviser's method skill before the next run.
- **Backlog:** accepted items → `technical-architect` (Size mode), its brief carrying the thread's `Advisory-Thread:` line and naming findings by `adv:<id>` → `records.py backlog add` rows, each citing `adv:<id>` in its `note`, no observed figure.
