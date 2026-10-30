---
name: feature-docs
description: Which feature-root docs to read per task and in what order, and which to write at feature completion (README, CONTRACTS, INTEGRATION, ARCHITECTURE, DECISIONS, DEBT, NOTES). Use before changing, using, debugging or reviewing a feature.
user-invocable: false
---

# Feature docs

Live at the feature root (`<feature root>/<Feature>/`, `CLAUDE.md`, default `Assets/_Project/Scripts/`), one set per feature, covering every assembly under it. Code from before the layout: the folder holding it.

| File | Holds |
|---|---|
| `README.md` | What it does, spec link, entry points, file map, consumers |
| `CONTRACTS.md` | Public API, events, schemas, invariants callers rely on |
| `INTEGRATION.md` | How other features use it; what must not be called |
| `ARCHITECTURE.md` | Internals: components, data flow, ownership |
| `DECISIONS.md` | Decisions a reader would otherwise undo: what, why, rejected option |
| `DEBT.md` | Known workarounds, limitations, accepted gaps |
| `NOTES.md` | Edge cases and observations not yet contract or debt |

## Read
| Task | Order |
|---|---|
| Use a feature | README → INTEGRATION → CONTRACTS |
| Change one | README → CONTRACTS → ARCHITECTURE → source |
| Debug | README → CONTRACTS → bug record → source → ARCHITECTURE → DEBT → DECISIONS |
| Review / test | spec → CONTRACTS → diff (tests: + DEBT, so known debt is not filed as new) |

- DECISIONS before undoing a design that looks wrong; DEBT before filing a bug against code that looks wrong.
- Missing file = never written, not "none". Fall back to source.
- Stop once you know the entry point, the invariants, and who sees your change.
- Doc vs code disagree → report both anchors; never pick silently. Spec in hand outranks the docset; source outranks any claim about behaviour.

## Write (size M/L, or any size with the risk flag)
- `README.md` at feature completion: overview, entry points, map (each assembly, what it references, its test fixtures), consumers. Keep everything else inline there until it outgrows the README, then promote it and leave a pointer.
- `CONTRACTS.md` when code outside the root calls in, or client and server must agree.
- `DECISIONS.md` / `DEBT.md` appended in the same change that made the decision or left the limitation — any size.
- Never an empty or placeholder file. One fact, one home. A change that makes a doc stale updates it in the same change.
