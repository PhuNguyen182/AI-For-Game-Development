---
name: decide
description: "Technology decision by cto on sourced candidates. Use for vendors, packages, netcode/backend, or what exists for X."
argument-hint: "<the capability or decision, as concrete behaviour>"
---

# /decide

## 1. Research — `researcher` (Research mode), never skipped
- **Brief:** the capability as behaviour ("research physics" is too vague), constraints from `CLAUDE.md`, `docs/tech-stack.md` and the manifest, paid allowed?
- **Existing coverage:** `Already in project:` covers it → report that; replacing it needs the GD's ask.

## 2. Spike — only when the GD asks, or a number is the blocker
- **GD question:** Ask the GD (`AskUserQuestion`): spike (cost, time) / decide provisionally.
- **Spike brief:** `rd-engineer`: the question, the decision waiting on it, threshold, device.
- **Device:** Device lock applies.

## 3. Decide — `cto`
- **Brief:** the candidate set whole, what depends on it, cost/scale constraints, spike evidence.
- **Product consequence:** (cost, scope, timeline) → `cto` returns `Needs GD` → `AskUserQuestion` framed for a non-engineer.

## 4. Record
- **Tech stack:** `docs/tech-stack.md`: the row for the area, with version and the decision's path.
- **Feature in flight:** → its file's `GD decisions`.
- **Standard:** sets a standard → GD approves (`AskUserQuestion`) → skill `engineering-standard-adr-authoring` writes the ADR in `docs/adr/`.
- **Report:** the call, why in product terms, reversibility, what would make it stale.
