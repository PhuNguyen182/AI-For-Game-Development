---
name: feature-docs
description: "Feature-root docs: README, CONTRACTS, INTEGRATION, ARCHITECTURE, DECISIONS, DEBT, NOTES CSVs. Use before feature work."
user-invocable: false
---

# Feature docs

- **Location:** the docs live at the feature root (`<feature root>/<Feature>/`, `CLAUDE.md`, default `Assets/_Project/Scripts/`).
- **Scope:** one set per feature, covering every assembly under it.
- **Code from before the layout:** the folder holding it.

## Prose docs (markdown)
| File | Holds |
|---|---|
| `README.md` | What it does, spec link, entry points, file map, consumers |
| `CONTRACTS.md` | Public API, events, schemas, invariants callers rely on |
| `INTEGRATION.md` | How other features use it; what must not be called |
| `ARCHITECTURE.md` | Internals: components, data flow, ownership |
| `DECISIONS.md` | Decisions a reader would otherwise undo: what, why, rejected option |

## Ledgers (CSV, skill `records`)
| File | Table | Holds | Columns |
|---|---|---|---|
| `DEBT.csv` | `debt` | Known workarounds, limitations, accepted gaps | `id, date, kind (workaround\|limitation\|accepted-gap), text, source, accepted_by, next_step, state (Open\|Paid)` |
| `NOTES.csv` | `notes` | Edge cases and observations not yet contract or debt | `id, date, topic, text, anchor, state (Open\|Debt\|Promoted:<doc>)` |

- **Feature root:** the CLI finds the folder from the feature registry's `feature_root`.

## Read
| Task | Order |
|---|---|
| Use a feature | README → INTEGRATION → CONTRACTS |
| Change one | README → CONTRACTS → ARCHITECTURE → source |
| Debug | README → CONTRACTS → bug record → source → ARCHITECTURE → DEBT → DECISIONS |
| Review / test | spec → CONTRACTS → diff (tests: + DEBT, so known debt is not filed as new) |

- **DEBT / NOTES:** `records.py csv list debt|notes --feature <slug>`, or the CSV itself.
- **Before undoing a design that looks wrong:** read DECISIONS.
- **Before filing a bug against code that looks wrong:** read DEBT, and `records.py debt list --open` for a gap accepted with no feature.
- **Missing file:** never written, not "none"; fall back to source.
- **Stop:** once you know the entry point, the invariants, and who sees your change.
- **Doc vs code disagree:** report both anchors; never pick silently.
- **Precedence:** spec in hand outranks the docset; source outranks any claim about behaviour.

## Write (size M/L, or any size with the risk flag)
- **`README.md`:** at feature completion: overview, entry points, map (each assembly, what it references, its test fixtures), consumers.
  - **Everything else:** keep inline there until it outgrows the README, then promote it and leave a pointer.
- **`CONTRACTS.md`:** when code outside the root calls in, or client and server must agree.
- **`DECISIONS.md`:** appended in the same change that made the decision — any size.
- **`DEBT.csv` / `NOTES.csv`:** only `records.py csv add debt|notes --feature <slug>`, one row per limitation or observation, in the same change that left it — any size.
  - **Writer:** the main session (skill `records`). An agent returns each row in its `Limitations`; the main session adds it before that change's commit.
  - **Never hand-edit a CSV:** a broken one → `records.py csv doctor --feature <slug>`.
- **Promote a note:** write the fact into its doc, then `records.py csv update notes <id> --feature <slug>`, `state` `Promoted:<doc>`.
  - **Became debt:** `csv add debt`, then the note's `state` → `Debt`.
- **Empty or placeholder files:** never; the CLI never writes a header-only CSV.
- **Placement:** one fact, one home.
- **A change that makes a doc stale:** updates it in the same change.
