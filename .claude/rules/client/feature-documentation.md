# Client Track — Feature Documentation

Applies to: C# Software Engineer, Unity Engineer, UI/UX Programmer, Tech Lead – C# Unity, Tech Lead – SDK/Platform, Tech Lead – Performance, Technical Artist.

## Relationship to other rules

This file governs the documentation deliverable owed at the end of every feature or module, on top of the per-submission Implementation Note already required by `coding-principles.md`'s Handoff section. The Implementation Note is a point-in-time handoff message to Code Reviewer for one submission; the README required here is a durable, in-repo document that stays accurate for as long as the feature exists in the codebase. It does not replace the Tech Spec (what was decided, and why) or the Implementation Note (the state of one specific submission) — it documents what actually got built and how to use it.

## Scope — Complex tier only

- This requirement applies only to features Technical Architect's Triage step classifies as **Complex** (new system, cross-cutting impact, multiplayer-relevant, or genuine uncertainty — per `technical-architect`'s Triage step). A Complex-tier feature already gets the full pipeline (Advisor-Critic loop, Tech Spec, architecture diagram) — the README is the durable, in-repo record of what that pipeline actually produced.
- **Simple and Medium tier work is exempt.** A Simple-tier change (single role, no new architecture decision, brief direct notes) or a Medium-tier change (multi-role but following established patterns, no design risk) does not need a README under this rule — writing one would be bureaucratic overhead disproportionate to the change, which is exactly what KISS/YAGNI in `coding-principles.md` warns against.
- If Technical Architect reclassifies a feature's tier mid-flight (e.g. a Medium-tier request turns out to need a design decision after all and is escalated to Complex), the README requirement applies from that point forward, same as the rest of the Complex-tier process would.
- When in doubt about a feature's tier, check with Technical Architect rather than assuming — don't skip the README by guessing a feature down to Medium/Simple, and don't write one speculatively for a Simple/Medium feature that doesn't need it.

## Core requirement — one README.md per feature root folder

- Once a Complex-tier feature or self-contained module is functionally complete — all its code is written and it is being handed to Code Reviewer for final approval — its root folder must contain a `README.md`. "Feature root folder" means the top-level directory holding that feature's code (e.g. the folder containing its `Game.Core.*` code, its `Game.Client.*` integration, and/or its UI, depending on how the feature is physically organized).
- If a feature's Core and Client code live in genuinely separate physical roots (e.g. a Shared Core package folder vs. a Unity `Assets/` feature folder), each root gets its own `README.md`, and each links to the other instead of duplicating its content.
- One README per feature, at the feature's top level — not one per class or per file, and not buried several folders deep where it won't be the first thing a reader finds.
- This is a completion requirement, not a per-commit one: a feature mid-implementation doesn't need a finished README yet, but it cannot be considered done — and cannot go to Code Reviewer for final sign-off — without one.

## Required contents

Write in English (per `.claude/rules/language-and-comments.md`), in Markdown. Cover every section below; how much detail each one gets follows the same judgment call as the Comment depth policy in `.claude/rules/language-and-comments.md` — a small, single-class feature can cover every section in a sentence or two, while a feature spanning Core/Client/UI/server-authoritative layers needs the fuller treatment.

1. **Overview** — one short paragraph: what the feature does, and which Tech Spec it implements (link/reference it, don't re-explain its requirements).
2. **Architecture** — how the feature is structured: which classes/modules live in `Game.Core.*` vs. `Game.Client.*` (and `Game.Server.*` when the backend track is active), what each major class is responsible for, and how they collaborate. State the dependency direction explicitly (Client depends on Core, never the reverse), and call out anything a reader would otherwise have to reverse-engineer from the code.
3. **How it works** — the runtime behavior: what triggers the feature, its lifecycle (init/update/teardown), its key state transitions, and any invariants that matter for correctness (ordering constraints, preconditions a caller must satisfy, etc.).
4. **Public API** — the surface other features/systems are expected to call: public classes, methods, properties, events, and interfaces, each with a one-line purpose and, where usage isn't obvious from the signature alone, a short example. This is the external contract — changing anything listed here is a breaking change for its callers.
5. **Internal API** — classes/methods that exist to support the feature internally and are not meant to be called from outside it. Marking these explicitly tells other features not to reach in and couple to them (reinforces the Law of Demeter in `coding-principles.md`). If something here later needs to be called externally, promote it to the Public API section deliberately — don't let outside code quietly grow a dependency on an internal.
6. **Dependencies & integration points** — what this feature depends on (other Shared Core modules, SDKs, other features), and, if known, what already depends on it.
7. **Known limitations / assumptions** — carry these over from the feature's Implementation Note(s) so they survive in the codebase, not only in a chat handoff that eventually scrolls out of reach.

## Ownership and maintenance

- Whoever implemented the feature writes the README. When a feature spans multiple roles (e.g. C# Software Engineer for Core, Unity Engineer for Client integration, UI/UX Programmer for UI), they share one README, and each section states which layer it's describing — don't split one feature's documentation across multiple disconnected files.
- The README is a living document, not a one-time deliverable: when a later Tech Spec change modifies the feature, the owning role updates the existing README in the same submission — treat a stale README as seriously as a stale test.
- Code Reviewer checks the README's presence and accuracy against the actual code whenever a submission represents a feature-complete state (not for every incremental, in-progress commit). Missing or stale documentation on a feature-complete submission is grounds for "request changes," same as any other rule in `coding-principles.md`.

## Rules

- This rule engages only for Complex-tier features per Technical Architect's Triage classification — never for Simple or Medium tier.
- No Complex-tier feature is complete without a `README.md` at its feature root folder — this is a hard gate before final Code Review sign-off for that tier, not an optional nice-to-have.
- One README per feature root, covering Overview, Architecture, How it works, Public API, Internal API, Dependencies, and Known limitations/assumptions — every section above must be present, even if brief.
- Never duplicate the Tech Spec's requirements text into the README — link back to the Tech Spec instead of re-explaining it; the README documents what got built and how to use it, not why it was decided.
- Keep the README scoped to its own feature root — don't use it to document unrelated systems, and don't let unrelated systems' documentation live inside it.
- Treat the README as a maintained artifact: a Tech Spec change that touches a Complex-tier feature includes updating that feature's README in the same submission.
