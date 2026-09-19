# DOTween vs LitMotion — Standing Choice, Never an Assumption

Source: this project's own `litmotion-tweening` skill (see its
[migration-and-rx-integration.md](../../litmotion-tweening/references/migration-and-rx-integration.md)),
and the allocation-model comparison in
[safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md).
Covers: SKILL.md §4 — "Never assume DOTween governs new tweening work just because this skill was invoked".

## The project maintains two tweening skills, deliberately

This project has both a `dotween-tweening` skill (this one) and a
`litmotion-tweening` skill, covering two different tweening engines with
different allocation models, ecosystems, and feature surfaces. **Neither
is the standing default for new work** — which one governs a given
feature is a project/module-level decision, not something either skill's
own documentation should assume on the requester's behalf.

## What to check before writing a new tween

In order:

1. **Does the module/feature being touched already use one of the two?**
   Follow existing convention in that area rather than introducing a
   second tweening library into the same feature. Mixing both inside one
   screen/system for no reason is exactly the kind of avoidable complexity
   KISS in `coding-principles.md` warns against.
2. **Is there a project-wide convention already established** (a Tech
   Spec, an architecture decision, an existing pattern followed
   consistently across features)? Follow it.
3. **If genuinely neither applies — a new module, no prior art, no stated
   convention — ask the GD/Tech Lead which engine governs this work
   before writing tween code**, rather than defaulting to whichever skill
   happened to be invoked first. This mirrors the general "ask rather than
   guess" pattern both tweening skills already use for their own
   ecosystem-availability questions (e.g. `litmotion-tweening`'s own
   UniTask/R3/UniRx-availability guardrail) — a tweening-engine choice is
   the same category of decision: it's cheap to ask now and expensive to
   discover mid-feature that two engines quietly coexist with no shared
   convention.

## When DOTween is the better fit even in a LitMotion-default area

Per [safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md),
raise this rather than silently picking DOTween anyway:

- DOTween Pro's visual Sequence editor or TMP shortcuts are genuinely
  needed for designer/artist iteration without a recompile.
- The feature specifically needs a DOTween-only capability with no
  LitMotion equivalent — e.g. `DOPath`'s waypoint path system (LitMotion
  has no built-in path tween; its own migration notes say to combine with
  Unity Splines instead), or `SetSpeedBased()` (also unsupported in
  LitMotion).

## When LitMotion is the better fit even in a DOTween-default area

- The tween is genuinely hot-path/high-volume (many simultaneous
  instances, a per-frame-created tween) and the allocation difference in
  [safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md)
  actually matters there — confirmed by profiling, not assumed.
- The work needs LitMotion-specific integration already established
  elsewhere in the project (its R3/UniRx `ToObservable()` bridge, its
  Burst/Job System path).

## Porting between the two

`litmotion-tweening`'s own
[migration-and-rx-integration.md](../../litmotion-tweening/references/migration-and-rx-integration.md)
carries a DOTween → LitMotion API mapping table (`transform.DOMove` →
`LMotion.Create(...).BindToPosition(...)`, `SetLoops`/`SetUpdate`/`SetLink`
equivalents, and what has no LitMotion equivalent at all — `SetSpeedBased()`
and `DoPath()`). There is currently no reverse (LitMotion → DOTween)
mapping documented anywhere in this project; porting that direction needs
manual translation using this skill's own reference files
([tweeners-shortcuts-and-generic.md](tweeners-shortcuts-and-generic.md),
[settings-and-callbacks.md](settings-and-callbacks.md),
[sequences.md](sequences.md)) as the target-side vocabulary.
