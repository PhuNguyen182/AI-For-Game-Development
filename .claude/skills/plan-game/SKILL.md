---
name: plan-game
description: "GDD to production backlog: milestones, S/M/L features, risk flags, .workflow/backlog.md. Use to plan production."
argument-hint: "<GDD path or text>"
---

# /plan-game

## 1. Read
- **Sources:** the GDD and `CLAUDE.md` (profile, platforms, multiplayer).
- **Unclear basics:** unclear core loop, target session length or monetisation → one `AskUserQuestion` (≤4 questions).

## 2. Milestones
- **Default order:** **Prototype** → **Vertical slice** → **Content** → **Soft launch** → **Launch**.
- **Prototype:** core loop playable, greybox.
- **Vertical slice:** one polished loop, real art, perf on target device.
- **Soft launch:** analytics, ads/IAP, live-ops.
- **Hyper-casual:** may merge Prototype and Vertical slice.

## 3. Features — `technical-architect` (Size mode), one brief for the whole list
- **Per feature:** name · milestone · size S/M/L · risk flag · depends on · first agent.
- **Order:** core systems first in each milestone.

## 4. Write `.workflow/backlog.md`
```
| # | Feature | Milestone | Size | Risk | Depends on | Status |
|---|---|---|---|---|---|---|
```
- **Status values:** todo | in progress (`/feature <slug>`) | done | dropped.

## 5. Approve — `AskUserQuestion`
- **Options:** Approve / reorder (which) / cut scope (which).
- **Next feature:** then offer the next feature — the first `todo` whose dependencies are `done` — and start it with `/feature`, its row and GDD section as the Request.
- **Row status:** `/feature` keeps the row's status current.

## Re-plan
- **GDD changed:** GDD changed → re-run steps 3–5 on the changed part only.
- **Features in progress:** when the GDD changed, features in progress go through `/feature`'s change request.
