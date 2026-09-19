# Safe Mode, Recycling, and Allocation Guidance

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php).
Covers: SKILL.md §4 — "Leave Safe Mode on unless the platform forces otherwise", "Never leave a non-autokilled tween's reference unmanaged".

## Safe Mode

`DOTween.Init`'s `useSafeMode` (default `true`, per
[getting-started.md](getting-started.md)) makes tweens "slightly slower
but safer, allowing DOTween to automatically take care of things like
targets being destroyed while a tween is running." Leave it on by default
— the cost is small and the failure mode it prevents (a tween throwing or
corrupting state because its target GameObject was destroyed mid-tween) is
exactly the kind of silent-until-it-isn't bug this project's Correctness
boundaries expectations exist to prevent.

**Platform caveat**: on iOS, Safe Mode only works correctly with
"Strip Assemblies" stripping level or "Slow and Safe" Script Call
Optimization — confirm the project's actual iOS build settings before
relying on Safe Mode there; a mismatched setting silently reduces the
protection Safe Mode is supposed to provide.

## Recycling

`SetRecyclable(bool)` (per tween) and `DOTween.Init`'s `recycleAllByDefault`
(project-wide) control whether a killed tween is pooled for reuse rather
than discarded, avoiding a GC allocation on the next tween of the same
shape. The trade-off: a recycled tween's C# reference is **reused for a
different future tween** once pooled, so holding onto a reference to a
recyclable tween past its kill is a use-after-recycle bug waiting to
happen. The documented pattern is to null the reference in `OnKill`:

```csharp
myTweenReference = transform.DOMoveX(4, 1).SetRecyclable(true);
myTweenReference.OnKill(() => myTweenReference = null);
```

Enable `recycleAllByDefault` project-wide only once this discipline is
actually applied everywhere a tween reference is held past its own
creation — enabling it without that discipline turns an occasional GC
allocation into an occasional silent logic bug, which is worse.

## Capacity and the Editor report

`DOTween.showUnityEditorReport` surfaces a max-capacity-reached report to
help size `DOTween.SetTweensCapacity(...)` correctly, but "will slightly
slow down your performance while inside Unity Editor" — treat it as an
Editor-only tuning aid to switch on temporarily, not a setting to leave
enabled, per `verification-standards.md`'s rule on labelling Editor-only
diagnostics as such.

## Allocation guidance: generic `DOTween.To()` vs Shortcuts vs LitMotion

The generic `DOTween.To(getter, setter, ...)` form (per
[tweeners-shortcuts-and-generic.md](tweeners-shortcuts-and-generic.md))
allocates the getter/setter closures on every call; a Shortcut still
allocates the underlying `Tweener`/`Sequence` object itself unless
recycling is engaged for that tween. This is a fundamentally different
allocation model from `litmotion-tweening`'s struct-based `MotionHandle`,
which is designed for genuinely zero per-motion allocation without
opting into a recycling scheme at all.

**This difference is a real input to the choice this project asks you to
make explicitly** — see
[coexistence-and-migration.md](coexistence-and-migration.md): a
high-frequency, high-volume tweening need (hundreds of simultaneously
tweened instances, a hot path) is a legitimate reason to prefer LitMotion
specifically for the allocation profile, independent of which library
otherwise governs a given module. Never assume DOTween's allocation cost
is negligible for such a case without profiling it, per
`performance-and-algorithms.md`'s Verification section.
