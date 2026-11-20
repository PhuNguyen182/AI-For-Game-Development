---
name: plan-game
description: "GDD to production backlog: milestones, S/M/L features, risk flags, the records backlog. Use to plan production."
argument-hint: "<GDD path or text>"
---

# /plan-game

## 1. Read
- **Sources:** the GDD and `CLAUDE.md` (profile, platforms, multiplayer).
- **Unclear basics:** unclear core loop, target session length or monetisation → one `AskUserQuestion` (≤4 questions), offering `/design` or `/monet` to settle it.

## 2. Milestones
- **Default order:** **Prototype** → **Vertical slice** → **Content** → **Soft launch** → **Launch**.
- **Prototype:** core loop playable, greybox.
- **Vertical slice:** one polished loop, real art, perf on target device.
- **Soft launch:** analytics, ads/IAP, live-ops.
- **Hyper-casual:** may merge Prototype and Vertical slice.

## 3. Features — `technical-architect` (Size mode), one brief for the whole list
- **Per feature:** name · milestone · size S/M/L · risk flag · depends on · first agent.
- **Order:** core systems first in each milestone.

## 3b. Order and bar — `product-owner`
- **Brief:** the feature list, GDD, `Workflow: /plan-game`, `Advisory-Thread: plan-<milestone>`.
- **Returns:** a proposed order within each milestone, and each milestone's "finished" bar (`product-quality-bar`).
- **Effect:** advice only; core systems still come first, and the main GD approves at step 5.

## 4. Write the backlog — `records.py backlog` (skill `records`)
- **Per feature, in plan order:** `records.py backlog add`, stdin `{"feature", "milestone", "size", "risk", "depends_on"}`; it prints `BL-####`.
  - **Numbers:** the id's number is the plan's `#`; `depends_on` lists those numbers.
- **Check first:** `backlog search "<feature>"` before each `add`; a re-plan updates the row (`backlog update <BL-id>`).
- **Status values:** todo | in progress (`/feature <slug>`) | done | dropped (`backlog set-state <BL-id> "<status>" --note N`).
- **View:** `records.py backlog render` prints the `| # | Feature | Milestone | Size | Risk | Depends on | Status |` table for step 5.

## 5. Approve — `AskUserQuestion`
- **Options:** Approve / reorder (which) / cut scope (which).
- **Next feature:** then offer the next feature — the first `todo` whose dependencies are `done` — and start it with `/feature`, its row and GDD section as the Request.
- **Row status:** `/feature` keeps the row's status current.

## Re-plan
- **GDD changed:** GDD changed → re-run steps 3–5 on the changed part only.
- **Features in progress:** when the GDD changed, features in progress go through `/feature`'s change request.
