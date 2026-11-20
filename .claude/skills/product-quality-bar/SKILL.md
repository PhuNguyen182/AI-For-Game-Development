---
name: product-quality-bar
description: "Finished-enough bar per milestone: goals, priority, FTUE, settings, offline, store readiness. Use for product reads."
user-invocable: false
---

# Product quality bar

- **Not for:** mechanics and feel (`game-design-lens`), revenue maths (`monetization-modeling`), code quality (`/review`).
- **Sources:** `CLAUDE.md` (Profile, KPI targets, Platforms, Compliance), the GDD, the backlog, debt and known limitations.
  - **Records:** `records.py backlog render`, `debt render`, each feature root's `DEBT.csv`, `csv render limitations --feature <slug>`.

## Steps
1. **State the goal:** the milestone's purpose from the backlog; `KPI targets` unset → your targets are `[assumption: ...]` and you say so.
2. **Set the bar by milestone:**
   - **Prototype:** the core loop is playable and answers its question; polish is noise.
   - **Vertical slice:** one loop at release quality on the target device.
   - **Content:** the volume plan is credible and each item meets the slice's bar.
   - **Soft launch:** analytics events, ads or IAP, live tuning, and a crash baseline all work.
   - **Launch:** the store listing, compliance and support path are done.
3. **Walk the completeness list:** for each item, say done, missing or not applicable, with the evidence:
   - **First session:** FTUE start to first reward, first failure, first return reason.
   - **Player control:** settings, audio, language, pause, quit, restore purchases.
   - **Failure paths:** offline, interrupted session, low storage, failed load, failed purchase.
   - **Save:** continuity after restart and update.
   - **Feedback:** every action answers visibly and audibly.
   - **Store:** icon, screenshots, age rating, privacy declarations.
4. **Rank the gaps:** by player impact against cost, never by how easy they are to fix.
5. **Name what to cut:** every review proposes what the milestone can drop, not only what to add.

## Never
- **Claiming feel:** declaring a game fun or polished from docs or code; say what a playtest must settle.
- **Feature lists as progress:** counting features done as evidence of quality.

## Example
- **"Add a daily reward because retention is low":** declined as a recommendation — no evidence links it to the drop; asked for the D1 funnel and named the first-session step to measure.
