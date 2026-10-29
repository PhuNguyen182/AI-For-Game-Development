---
name: design-precedent-sweep
description: "Find how shipped games solved a design or architecture problem: shipping team's own account first, 2-4 distinct mechanisms, each with trade-off and assumptions, unranked. Use for every options-mode question."
user-invocable: false
---

# Design Precedent Sweep

Not for: finding a package, technique or service to adopt (`technology-scouting-sweep`), grading a source (`source-credibility-grading`), attacking the option the GD picks (`critic`), deciding (GD; `cto` for a technology foundation).
Sources: GDC Vault https://gdcvault.com, Game Developer postmortems https://www.gamedeveloper.com.

## Steps
1. **Restate the question as the problem plus the constraint that makes it hard** — "200 units path to a target at 60 fps on low-end Android", not "flow fields". A solution name returns that solution and hides the others.
2. **Read the project first** — the feature file, the GDD section it cites, `docs/tech-stack.md`. What the project already does is an option of its own (`Status quo`), with its own trade-off.
3. **Search the shipping team's own account first** — GDC talk, postmortem, studio tech blog, engine-vendor case study naming the studio. Then named-author teardowns of the shipped game. Forums only corroborate a caveat. Grade each per `source-credibility-grading` → Precedent claims.
4. **A precedent is a named, shipped title** — studio, year, platform. "Many games do X", a prototype, a jam game or an unreleased title is not one; keep it only as a labelled note.
5. **Mechanism comes from the developers or a teardown, never from playing or guessing** — a teardown's account is marked `inferred`.
6. **2–4 options, each a distinct mechanism** — three variants of one approach are one option with variants. Only one mechanism found across shipped games → that is the finding; say so.
7. **Write what the precedent assumed, then where this project differs** — scale, genre, platform tier, team size, online or not. Facts only; no verdict.
8. **Stop at saturation** (three consecutive queries returning only collected precedents) **or at 15 queries** — at the cap, list what was not searched.
9. **List options alphabetically by mechanism** and say the order is not a ranking.

## Never
- Rank, score, recommend or call an option "best" or "standard" — the choice is the GD's.
- Cite a talk or postmortem whose page you did not open, or attribute a mechanism its developers did not describe.
- Turn the sweep into a package search; a package found on the way goes under `Leads`, unscreened.

## Output
```
## Precedent Sweep — <problem + hard constraint>
- Searched as: <phrasing; assumption if ambiguous>
- Order: alphabetical by mechanism — not a ranking
### <Mechanism>
- Precedent: <title — studio, year, platform>
- Mechanism: <one line — stated by developers | inferred from teardown>
- Trade-off: <what it cost them, in their words where reported>
- Assumes: <conditions in their game>
- Differs here: <project constraint that does not match — or "none found">
- Source: <URL> — <tier>, retrieved <date>, published <date>
### Status quo (if the project already has one)
- Mechanism / Trade-off / Differs here
- Leads: <packages or techniques seen, unscreened> | none
- Sweep status: SATURATED / STOPPED AT CAP — <not searched>
```

## Example
- "List the ten games that use ECS for crowds" → declined: one mechanism with ten examples is one option; the sweep returns ECS crowds, GPU-instanced crowds with baked animation, and LOD-impostor crowds, each with one precedent that names its cost.
