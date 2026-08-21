# Root Links — LitMotion v2 Documentation & Source Index

Source: the repository, documentation, and API index pages listed below, on
the official LitMotion GitHub repository and its docfx documentation site.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to **LitMotion v2** (latest tagged release
`v2.0.2`). The documentation site is unversioned in its URLs — there is no
version segment to pin — so a page's content simply reflects whatever `main`
currently ships. Where v1 behavior differs, the page says so explicitly, and
[migration-and-rx-integration.md](migration-and-rx-integration.md) carries the
v1→v2 delta. Consult the live site or repository for anything not covered
here; the library adds features between releases.

| Root | Holds | Source |
|---|---|---|
| GitHub repository | README, source code, releases, issues | [annulusgames/LitMotion](https://github.com/annulusgames/LitMotion) |
| Documentation site | Conceptual/how-to articles (English) | [LitMotion Docs](https://annulusgames.github.io/LitMotion/articles/en/) |
| API reference | Generated docfx type/member reference | [LitMotion API](https://annulusgames.github.io/LitMotion/api/) |
| Source — core runtime | `LMotion`, `MotionBuilder`, `MotionHandle`, adapters, options | [Runtime](https://github.com/annulusgames/LitMotion/tree/main/src/LitMotion/Assets/LitMotion/Runtime) |
| Source — extensions | `LitMotion.Extensions` `BindTo*` methods, by category folder | [Runtime/Extensions](https://github.com/annulusgames/LitMotion/tree/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions) |
| Source — Animation package | `LitMotionAnimation`, `LitMotionAnimationComponent`, built-in components | [LitMotion.Animation/Runtime](https://github.com/annulusgames/LitMotion/tree/main/src/LitMotion/Assets/LitMotion.Animation/Runtime) |
| Benchmark repository | The performance-comparison project referenced from the README/overview | [annulusgames/TweenPerformance](https://github.com/annulusgames/TweenPerformance) |

## Article index (English)

Every page below lives under `https://annulusgames.github.io/LitMotion/articles/en/<slug>.html`, and its raw Markdown source at `https://raw.githubusercontent.com/annulusgames/LitMotion/main/docs/articles/en/<slug>.md`.

| Slug | Distilled in |
|---|---|
| `installation`, `quick-start`, `package-structure`, `supported-types`, `faq` | [getting-started.md](getting-started.md) |
| `basic-concepts`, `binding`, `motion-control` | [motion-builder-and-handle.md](motion-builder-and-handle.md) |
| `motion-configuration`, `motion-settings` | [motion-settings.md](motion-settings.md) |
| `sequence`, `punch-and-shake` | [sequence-and-vibration.md](sequence-and-vibration.md) |
| `custom-binding-extension-method` | [component-bindings.md](component-bindings.md) |
| `text-animation`, `textmesh-pro-character-animation` | [text-and-tmp-animation.md](text-and-tmp-animation.md) |
| `await-motion-in-coroutine`, `await-motion-in-async-await`, `convert-to-disposable`, `exception-handling`, `manual-motion-dispatcher`, `play-motion-in-editor`, `avoid-dynamic-memory-allocation`, `litmotion-debugger` | [async-lifecycle-and-debugging.md](async-lifecycle-and-debugging.md) |
| `custom-adapter` | [custom-adapters.md](custom-adapters.md) |
| `litmotion-animation-overview`, `litmotion-animation-installation`, `litmotion-animation`, `litmotion-animation-script`, `custom-animation-component` | [litmotion-animation-component.md](litmotion-animation-component.md) |
| `integration-r3`, `integration-unirx`, `integration-unitask`, `integration-zstring`, `migrate-from-dotween`, `migrate-from-leantween`, `migrate-from-primetween`, `migrate-from-v1`, `design-philosophy`, `whats-new-in-v2` | [migration-and-rx-integration.md](migration-and-rx-integration.md) |

Every other link in this folder resolves under one of the roots above, each
verified to resolve at the time this skill was authored.
