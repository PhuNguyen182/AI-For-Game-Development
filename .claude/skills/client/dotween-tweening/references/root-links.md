# Root Links — DOTween

Source: the documentation page below, as provided for this skill.
Covers: the whole skill — provenance for every file in this folder.

| Root | Holds | Source |
|---|---|---|
| Documentation (single page, anchored sections) | Every topic this skill is built from — Init, Tweeners, Shortcuts, Sequences, Settings/Callbacks, Path Tweens, Control Methods | [DOTween Documentation](https://dotween.demigiant.com/documentation.php) |
| Downloads | Free vs Pro distribution, current Editor compatibility | [DOTween Downloads](https://dotween.demigiant.com/download.php) |
| Get Started | Install/setup walkthrough | [DOTween Get Started](https://dotween.demigiant.com/getstarted.php) |
| UniTask DOTween integration | `UNITASK_DOTWEEN_SUPPORT`, `.ToUniTask()`/`.WithCancellation()`/`AwaitForComplete` family | [UniTask](https://github.com/Cysharp/UniTask) (its own README's DOTween integration section) |

DOTween is free and distributed primarily through the **Unity Asset Store**
as "DOTween (HOTween v2)" (its predecessor engine's name lives on in the
package title), with **DOTween Pro** as a separate one-time-fee asset
layered on top. There is no official Unity Package Manager/git-URL
distribution from Demigiant itself — community-maintained UPM mirrors
exist but are not the canonical source; confirm which distribution the
project actually uses before assuming a particular asmdef/folder layout.
After importing (or updating) the package, **Tools > Demigiant > DOTween
Utility Panel > Setup DOTween...** must be run once to generate/refresh the
per-module wrapper scripts described in
[getting-started.md](getting-started.md) — a shortcut that "doesn't exist"
after import is usually this step never having been run, not a missing
package.

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Install, `DOTween.Init`, Modules panel, Free vs Pro, supported types, nomenclature | [getting-started.md](getting-started.md) | [Documentation](https://dotween.demigiant.com/documentation.php) |
| `DOTween.To` (generic), Shortcuts concept, non-UI component shortcuts, Punch/Shake/ToAlpha/ToArray/ToAxis/virtual tweens | [tweeners-shortcuts-and-generic.md](tweeners-shortcuts-and-generic.md) | [Documentation](https://dotween.demigiant.com/documentation.php) |
| Unity UI (4.6+) shortcuts, UI Toolkit `VisualElement`, TextMeshPro (Pro) shortcuts, `DOTweenTMPAnimator` | [ugui-and-tmp-shortcuts.md](ugui-and-tmp-shortcuts.md) | [Documentation](https://dotween.demigiant.com/documentation.php) |
| `DOTween.Sequence()`, Append/Insert/Join/Prepend, nested sequences | [sequences.md](sequences.md) | [Documentation](https://dotween.demigiant.com/documentation.php) |
| `Set*` options, chained callbacks, global settings | [settings-and-callbacks.md](settings-and-callbacks.md) | [Documentation](https://dotween.demigiant.com/documentation.php) |
| Play/Pause/Kill/etc. instance and static filtered control | [control-methods.md](control-methods.md) | [Documentation](https://dotween.demigiant.com/documentation.php) |
| `DOPath`/`DOLocalPath`, `PathType`/`PathMode`, `SetOptions`/`SetLookAt` | [path-tweens.md](path-tweens.md) | [Documentation](https://dotween.demigiant.com/documentation.php) |
| Safe Mode, recycling, capacity/editor report, allocation guidance | [safe-mode-recycling-and-performance.md](safe-mode-recycling-and-performance.md) | [Documentation](https://dotween.demigiant.com/documentation.php) |
| Coroutine waits, `AsyncWaitForCompletion`, UniTask's `UNITASK_DOTWEEN_SUPPORT` | [async-and-unitask-integration.md](async-and-unitask-integration.md) | [Documentation](https://dotween.demigiant.com/documentation.php), [UniTask](https://github.com/Cysharp/UniTask) |
| Whether DOTween or LitMotion governs new work, DOTween→LitMotion migration pointer | [coexistence-and-migration.md](coexistence-and-migration.md) | This project's own `litmotion-tweening` skill |

## Disclosed gaps

DOTween's Manual is a single long anchored page; each fetch during
authoring returned a bounded excerpt rather than the whole page at once, so
sections were assembled from several targeted fetches rather than one pass.

| Area | Issue |
|---|---|
| Exact per-parameter default values (e.g. `DOTween.Init`'s three defaults, `SetLoops`' default `LoopType`) | Confirmed at the level the fetched excerpts state; re-check an exact default against the installed version's IntelliSense/source before depending on it precisely. |
| Full non-UI shortcut catalogue (AudioMixer, AudioSource, Camera, Light, LineRenderer, Rigidbody/Rigidbody2D, SpriteRenderer, TrailRenderer) | The section header list was confirmed; individual method signatures beyond Transform/Material were not each independently quoted — check the live page for a specific one before citing its exact parameters. |
| `TweenCancelBehaviour` and other UniTask-side DOTween enum specifics | UniTask's own README excerpt confirmed `.ToUniTask()`, `.WithCancellation()`, and the `AwaitForComplete`/`AwaitForPause`/`AwaitForPlay`/`AwaitForRewind`/`AwaitForStepComplete` family, but not a full enumeration of every cancel-behavior option — confirm against UniTask's source/README before citing an exact enum member. |
| DOTween Pro's exact feature boundary vs free DOTween | Confirmed: visual Sequence editor, extended TextMeshPro shortcuts, path gizmo editor are Pro-only. A feature not explicitly called out as Pro-only in this skill's files is assumed free-tier, but wasn't exhaustively cross-checked against a Pro changelog. |
