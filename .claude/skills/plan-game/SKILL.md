---
name: plan-game
description: "Turn a GDD into a production backlog: milestones, then features per milestone sized S/M/L with risk flags and dependencies, written to .workflow/backlog.md for GD approval. Use when starting production or re-planning from a changed GDD."
argument-hint: "<GDD path or text>"
---

# /plan-game

## 1. Read
- The GDD and `CLAUDE.md` (profile, platforms, multiplayer). Unclear core loop, target session length or monetisation → one `AskUserQuestion` (≤4 questions).

## 2. Milestones
Default: **Prototype** (core loop playable, greybox) → **Vertical slice** (one polished loop, real art, perf on target device) → **Content** → **Soft launch** (analytics, ads/IAP, live-ops) → **Launch**. Hyper-casual may merge the first two.

## 3. Features — `technical-architect` (Spec mode, size only), one brief for the whole list
Per feature: name · milestone · size S/M/L · risk flag · depends on · first agent. Core systems first in each milestone.

## 4. Write `.workflow/backlog.md`
```
| # | Feature | Milestone | Size | Risk | Depends on | Status |
|---|---|---|---|---|---|---|
```
Status: todo | in progress (`/feature <slug>`) | done | dropped.

## 5. Approve — `AskUserQuestion`
Approve / reorder (which) / cut scope (which). Then start the first feature with `/feature`.

## Re-plan
GDD changed → re-run steps 3–5 on the changed part only; features in progress go through `/feature`'s change request.
