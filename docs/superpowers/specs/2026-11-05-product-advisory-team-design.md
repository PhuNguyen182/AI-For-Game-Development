# Product advisory team — design

Status: approved via plan · 2026-11-05 · Size L (framework architecture), route `/feature`, feature file `.workflow/features/game-production-agent.md`

## Intent
The framework has 23 agents and none owns game design quality, product completeness or earning ability. `/plan-game` takes the GDD as given, CP1 runs only for L work, or hard-core M with the risk flag (off for hyper-casual), `playtest-tester` checks a game against its GDD but not whether it is good, and monetisation exists only as vendor choice (`cto`) and SDK wiring (`sdk-platform-engineer`).

This design adds three advisers and three workflows, so the human decision-maker gets challenged and informed on design, product and money, and each kind of work triggers its own route.

## Goals
- Better decisions on product quality, features, completeness and earning ability.
- A separate route per kind of work: design, monetisation, product review, and the existing production pipeline.
- Advice the main GD can check: every number shows where it came from.

## Non-goals
- Replacing the main GD's judgement of fun. Agents cannot feel a game.
- Vendor choice or SDK integration; those stay with `cto` and `sdk-platform-engineer`.
- Automated data pipelines. Data arrives as a file pack (see Data pack).
- User acquisition and marketing. The monetisation role covers economy, ads, IAP and pricing only, so the team cannot answer LTV against CPI.

## Anti-goals (failure even if it technically works)
- Confident revenue or retention numbers with no evidence behind them.
- Advisers blocking the pipeline or adding cost to S work.
- Three voices converging on one agreeable answer that hides a real conflict.
- Advice that pushes dark patterns or breaks store policy or the project's compliance setting.

## Decided by the main GD
- **Scope:** design, product and monetisation are all in; no single-workflow trial before deciding on the rest.
- **Authority:** advisory only. Notes appear at CP2 and CP4 for the main GD to read before approving; nothing blocks.
- **Discussion form:** each agent reads independently, the main session merges and shows conflicts, the main GD responds, and the main session follows up with the relevant agent, keeping its context.
- **Test game:** a game with real players and real data, not `aga001-night99`. Name and data channel are supplied later.
- **Naming:** the human decision-maker is `main GD`. The bare term `GD` is retired for that role. Vietnamese replies keep Bạn/Tôi as pronouns.
- **MO scope:** monetisation only.
- **Storage:** advice goes into memory, off git, in SQLite, queried when needed, under Zero-Mem principles.

## Agents
All three: `model: opus`, tools `Read, Grep, Glob, WebSearch, WebFetch, Skill`, no shell, no writes, preload `agent-protocol`. Each earns a separate agent under `framework-docs/agent-template.md` by a distinct activation condition; advisers are not gates. A fresh context also keeps each read free of the other advisers' opinions.

| Agent | Owns | Not for |
|---|---|---|
| `product-owner` | Goals, priority, the "finished enough" bar per milestone | Mechanics (`game-designer`), revenue maths (`monetization-designer`) |
| `game-designer` | Core loop, progression, difficulty, FTUE, intended player feeling | Revenue decisions, implementation |
| `monetization-designer` | Economy sources and sinks, ad placement, IAP ladder, pricing, revenue model | Vendor choice (`cto`), SDK work (`sdk-platform-engineer`) |

The name `game-designer` is written in full, never abbreviated, so it cannot collide with `main GD`.

## Skills
- **`advisory-protocol`** (preloaded by all three): evidence labels, return fields, the never-decide rule.
- **Method skills** (one preloaded per agent): `product-quality-bar`, `game-design-lens`, `monetization-modeling`. Each holds the checklist of what that role inspects.
- **Workflow skills:** `/product-review`, `/design`, `/monet`.

## Evidence labels
Every number in an adviser's return carries one label:

| Label | Requires |
|---|---|
| `measured` | Data pack file, date range and build version |
| `benchmark` | URL, retrieval date, tier per `source-credibility-grading` |
| `assumption` | The stated reasoning, and what would replace it |
| `proposed` | A candidate's new value: price, placement, sink. A design choice, not an estimate |

A computed figure inherits its weakest input's label: LTV from one assumed input and four measured ones is `assumption`. `proposed` values are excluded from that propagation: a figure built on measured data and a proposed price keeps the `measured` label and names the proposed value. An unlabelled number invalidates the return; the main session sends it back. This rule is the core defence against the first anti-goal.

## Data pack
The interface between "however the numbers are obtained" and the agents, so the later channel decision changes no agent.

- **Location:** `.memory/advisory/data/<period>/`, git-ignored with the advisory store (revenue is business-sensitive).
- **Contents:** `manifest.md` (source, date range, filters, build versions) plus aggregated CSVs.
- **PII:** aggregated data only. `check_pack.py` default-denies: a header word outside an allowlist vocabulary, or an identifier-shaped value (email, IP, phone, UUID, long digit, hex or letter-digit runs), fails the pack. It never prints a value or an unknown word. The main session runs it before any agent reads the pack. (Redesigned after review round 2: a denylist missed new identifier names every round.)
- **Absent:** agents still run. No figure can be `measured`, and no return may conclude anything about revenue. `/monet` then shows scenarios with no recommendation and ends with what to measure.

## Advisory store
The main GD ordered advice kept in memory, off git, in SQLite, under Zero-Mem principles: deterministic, stdlib only, no LLM organising or rewriting.

- **Files:** `.memory/advisory/advisory.db` and `.memory/advisory/data/`, ignored outside the `Framework repo only` block and in `.xerjignore`. Not in `.memory/.index/`, which is rebuilt.
- **CLI:** `.claude/skills/mem/scripts/adv.py`: `ingest`, `q`, `get`, `list`, `decide`, `useful`, `export`, `lint`. It refuses to write unless `git check-ignore` confirms its path is ignored, and refuses secret shapes.
- **Capture:** SubagentStop hook `advisory-capture.ps1` stores an adviser's return verbatim. Findings split into rows on a fixed heading, each with a decision and a usefulness mark.
- **Traces:** game projects commit `.memory/traces/`, so `mem.py capture` replaces adviser `brief` and `agent` turns, and assistant text between `<!-- advisory:begin -->` and `<!-- advisory:end -->`, with a pointer. An unterminated begin strips to the end of the turn.
- **Tracked files:** GDD, `docs/monetization-plan.md`, feature files and backlog hold decisions, design parameters and targets, plus `adv:<id>` references. Never an observed figure. `pre-commit.ps1` blocks a staged `measured` label or advisory marker.
- **Cost:** the DB is per-machine: not shared with teammates and lost with the disk unless `adv export` runs.

## Workflows

### `/product-review [scope]`
Trigger: milestone exit, before soft launch, or "the game does not feel finished".
1. **Inputs:** `CLAUDE.md`, GDD, backlog, `DEBT.md` and known limitations, data pack, playtest evidence.
2. **Actual game evidence:** no playtest evidence → offer a `playtest-tester` run first. Declined → the report is labelled "docs and code only" and makes no claim about feel.
3. **Independent reads:** dispatch all three in parallel with the same brief, none seeing another's output.
4. **Merge:** the main session dedupes and ranks by severity. A conflict stays a conflict: both positions and the cost of each. Never averaged.
5. **Discuss:** `AskUserQuestion` for what enters the backlog and what to probe. Follow-ups continue the same agent, or fall back to a fresh dispatch with its earlier return in the brief. Maximum 2 follow-up rounds, counted by the main session in the advisory DB; no hook enforces this.
6. **Output:** findings in the advisory DB with decisions; accepted items as `.workflow/backlog.md` rows sized by `technical-architect`, citing `adv:<id>`.

### `/design <question>`
Trigger: a new mechanic, loop, progression or FTUE with its direction undecided, or "this part of the game is boring".
1. **Frame:** `game-designer` states the intended player feeling, the loop effect and what makes the problem hard.
2. **Precedents:** `researcher` (Options, `design-precedent-sweep`).
3. **Pick:** the main GD picks; options unranked, under the `core.md` exception this feature widens.
4. **Detail:** `game-designer` drafts the GDD section and acceptance criteria for the pick.
5. **Attack:** `critic`. `monetization-designer` also reads independently when economy, ads or IAP are touched.
6. **Lock:** the main GD locks or picks again; the main session writes the GDD at `CLAUDE.md` → GDD path.
7. **Hand-off:** `/plan-game` re-plan or `/feature`, which records `CP1: n/a (direction given: /design <date>)`.

### `/monet <question>`
Trigger: a change to ads, IAP, pricing or economy with its direction undecided, or a revenue problem. A vendor question goes to `/decide`. A change with a stated value is sized normally.
1. **Baseline:** `monetization-designer` reads current monetisation, GDD economy and the data pack.
2. **Candidates:** 2–4, each with its change, simulator parameters and a retention risk.
3. **Simulate:** the main session runs `simulate.py` on the returned parameters and sends the output back to the same agent. Output: low/base/high cumulative ARPU at D30 and D90, plus daily currency balance. No pack → scenarios only, no recommendation.
4. **Independent read:** `game-designer` on the player effect of every candidate.
5. **Lean:** the main GD leans to one candidate or rejects all.
6. **Attack:** `critic` on that one: assumptions, store policy, compliance.
7. **Pick:** the main GD locks or picks again.
8. **Output:** `docs/monetization-plan.md` with design parameters, success metric, measurement window and rollback threshold, no observed figures. Build goes to `/feature`; a real-money change carries the risk flag.

### Production pipeline — changes to existing skills
- **`/plan-game`:** after sizing, `product-owner` proposes order and each milestone's "finished" bar. Unclear core loop or monetisation in step 1 → offer `/design` or `/monet` alongside the existing question.
- **`/feature` CP2 and CP4 (M/L):** `product-owner` always; `game-designer` when player-facing; `monetization-designer` when economy, ads or IAP are touched. Notes appear beside the approval question.
- **Notes are not gates:** they consume no attempts or rounds, and a declined note is recorded once in the feature's decisions and not raised again at that point. `round-cap.ps1` exempts the three advisers from dispatch checks before it reads the ledger, because those checks would otherwise block a note on a past-cap feature.
- **`/feature` step 2:** when CP1 runs for this size and profile, an open game-design question routes to `/design`, recording `CP: CP1 — next step: /design <q>`; architecture questions stay in CP1. When CP1 is off, a design question goes to the main GD as today, with `/design` offered as an option.
- **Milestone exit:** closing a milestone's last feature offers `/product-review` once.
- **S work and `/fix`:** unchanged.

## Routing additions (`routing.md`)
Inserted above `Change to an open feature`, so they win over sizing:

| Input | Route |
|---|---|
| Mechanic, loop, progression, difficulty or FTUE, direction undecided | `/design` |
| Ads placement, IAP, pricing or economy, direction undecided; revenue problem | `/monet` |
| Product health, completeness, milestone exit | `/product-review` |

A plain question uses the existing `Question` row: one adviser, read-only. `routing.md` → Dispatch also gains an exception to "agents see only the brief and the disk" for adviser follow-ups.

## Simulator
`simulate.py` in `monetization-modeling`, Python stdlib only, deterministic, no randomness. Input JSON: low, base and high sets of a retention curve, ad impressions per DAU per placement, eCPM, IAP conversion and ARPPU, currency sources and sinks; each value with its label. Bands come only from those three sets, never invented percentages. Output JSON carries the propagated labels. It is arithmetic over inputs, not a prediction, and the report must say so.

## `CLAUDE.md` template
Add rows: `KPI targets` (per milestone, or unset) and `Data pack` (path, or none). Unset KPI targets → `product-owner` treats its targets as `assumption` and says so.

## Rename: `GD` → `main GD`
First step, its own commit, because later files should be written in the new term. 344 occurrences in 86 files. A blind replace silently breaks the round cap, so:

| Old | New | Machine use |
|---|---|---|
| `## GD decisions` | `## Main GD decisions` | Parsed: `round-cap.ps1:161`, `verify.ps1:55`, `hooks/tests/run.ps1`. Also written per the message at `round-cap.ps1:339` and `routing.md:60` |
| `Needs GD` | `Needs main GD` | Printed only: `agent-protocol`, hook block messages |
| `Next: gd`, bare route token `gd` | `Next: main-gd`, `main-gd` | Printed only: `agent-protocol`, agents, `playtest-scenario-execution`, `ci-pipeline-failure-triage`, `git-safety-anchor` |
| `--by GD` | `--by "main GD"` | `bugs.py:318,956,1015`, `test_bugs.py`, `hooks/tests/run.ps1:750` |
| prose `the GD` | `the main GD` | none |

- **Back-compat:** `round-cap.ps1` accepts both headings, because game repos hold open feature files with the old one. `bugs.py` replay stores `by` verbatim, so old journals need no compat, and new writes accept only the new form.
- **Do not touch:** `GDD`, `%gd` in `git-recovery`, `.memory/`, closed `.workflow/features/` files, `.workflow/DEBT.md`, `.workflow/evidence/`, journal history.
- **Left to the builder:** internal variable names such as `$gd`.

## Verification
| What | How | Needs test game? |
|---|---|---|
| Layer integrity | `/verify-layer` | no |
| Rename | `hooks/tests/run.ps1` and `test_bugs.py` green, including new old-format cases; a grep finds bare role `GD` only on the back-compat list | no |
| Simulator | Golden output; label propagation test; `proposed` excluded | no |
| Data pack check | Rejects a `user_id` header; accepts an aggregated pack | no |
| Advisers not blocked | `hooks/tests/run.ps1`: adviser dispatch on a past-cap feature and with a corrupt ledger passes; `code-reviewer` still blocked | no |
| Store and leak | `adv.py` tests; `test_mem.py` fixture leaves no figure in a trace; `pre-commit` blocks a staged `measured` label | no |
| Follow-ups | One throwaway spike: `SendMessage` continuation, SubagentStop firing, transcript shape | no |
| Workflows | Each run once on the test game | yes |

**Usefulness test:** at the end of each pilot run the main GD marks every finding useful or not. Under half useful in a workflow → revise that workflow's method skill before further use.

Until the test game and data pack arrive, the feature can only close with the three pilot runs in `Known limitations`. `/monet` cannot be validated on revenue before that.

## Calls made by the author, open to correction
- Name `monetization-designer` for "MO", read as the monetisation role.
- Build order: rename → agents and shared skills → `/product-review` → `/design` → `/monet` → pipeline hooks into `/plan-game` and `/feature`.
- `opus` for all three, because the work is judgement. Token cost per run is not measured.
- Data pack format and PII check.
- Advisers write nothing: a hook stores returns, and the main session writes every other file, matching `routing.md` → State.
- The 2-round follow-up cap, a new cap of its own.
- `proposed` label, simulator bands from three input sets, routing row position and the `/design` behaviour when CP1 is off.
- The usefulness test and its 50% line.
- No commit of this document until the main GD orders it (`core.md`).

## Built differently (CP3, 2026-11-06)
Accepted as built at CP3; the sections above keep the original intent, and these lines win where they differ.

- **Capture:** also any agent whose brief carries `Advisory-Thread:` (critic, researcher).
- **Scrub:** also any agent return carrying `Advisory-Return:`, and `mem.py` replaces any non-user line holding a measured label (open bracket, `measured`, colon).
- **Pre-commit:** also blocks a staged `.memory/advisory/` file; exact framework files that define the label are exempt.
- **Data pack:** TSV accepted beside CSV; the check is default-deny (header vocabulary plus id-shaped values), redesigned after review round 2. The header denylist named under "Left to the builder" is retired.
- **adv.py:** a ninth command, `rounds <thread>`, derives the follow-up count from stored returns; ingest redacts PII and is idempotent per agent, agent id and body.
- **Brief markers:** `Workflow:`, `Advisory-Thread:`, `Data-Period:`, `Target:`.
- **Labels:** a design parameter cited by path (GDD, config) needs no label.
- **routing.md:** a `## Advisers` section states the CP2/CP4 note rule.
- **core.md:** the unranked-options exception also covers a `/monet` lean without a data pack.
- **Files:** `/monet` writes simulator inputs under `.memory/advisory/sim/`.
- **/monet hand-off:** records `CP1: n/a (direction given: /monet <date>)`; a tuning-only route via `live-ops-content-pipeline`; an after-launch re-run against the rollback threshold.
- **/product-review:** an unlabelled return is sent back once; a second failure leaves it invalid per `advisory-protocol`.
- **Simulator schema:** IAP is `purchases_per_dau × revenue_per_purchase`; currency is `net_per_active_day` plus a 30-day balance per retained player; outputs add ARPDAU, active days, `retention_last_day` and `extrapolated_past_day`, which marks figures past the last retention day as `assumption`.
- **/plan-game 3b:** the milestone "finished" bar is advice in the store; where it is written down is open for the next edit.
- **Usefulness rule:** under half of an adviser's findings in a run marked useful revises that adviser's method skill, in all three workflows.
- **Branch:** `feature/game-production-agent`, which the main GD created, not the plan's `feature/product-advisory-team`.

## Left to the builder
- Exact return field names in `advisory-protocol`.
- Checklist content of the three method skills, within their roles above.
- Simulator JSON schema and the exact header denylist.
- Skill frontmatter and the wording of the routing rows.
