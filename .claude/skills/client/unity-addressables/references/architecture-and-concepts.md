# Architecture & Design Concepts

Covers SKILL.md's content-build-system and addressing decisions in depth — what to decide before writing a single load call.

## Content build system: Content Directory vs. AssetBundle

Addressables 4.0 ships two distinct content build systems; a project picks exactly one and never mixes them:

| | Content Directory | AssetBundle |
|---|---|---|
| Dependency tracking | Per-asset; duplicates automatically removed | Per-bundle; can cause redundant content |
| Unloading | Assets release as soon as their direct dependencies are freed | Assets persist until every dependent bundle is released |
| Remote delivery | Local only | Supports local **and** remote delivery |
| Group → output mapping | Groups build to a single directory by default | Groups map directly to individual bundles |
| Minimum Unity version | 6.6+ | Any version Addressables 4.0 supports |

Decision rule: new projects with no remote-content requirement, on Unity 6.6+, default to Content Directory — it is the simpler workflow with better default dependency hygiene. Any project that needs post-launch content updates, remote/CDN delivery, or supports pre-6.6 Unity must use the AssetBundle system. Mixing both in one project builds shared dependencies twice, inflating build size and risking asset duplication — this is a one-time, project-wide decision, not a per-group choice.

## Addressing model

- **Address**: a stable, human-assigned identifier for an asset (e.g. `boss1_material_main`), decoupling code from the asset's physical path.
- **Key**: what a load call actually accepts — an address, a label, or an `AssetReference`. Multiple assets can share one address as long as labels distinguish them (loading by label pulls in all matches).
- **`AssetReference`** (and its typed subclasses — `AssetReferenceGameObject`, `AssetReferenceTexture`, `AssetReferenceSprite`, etc., all built on `AssetReferenceT<TObject>`): a serializable field an Inspector can wire up without eagerly loading the asset, giving type-appropriate safety a bare string key doesn't. It tracks its own `OperationHandle` once loaded, exposes `IsValid()` to check load/release state, and distinguishes `editorAsset` (editor-only convenience) from `RuntimeKey` (the actual runtime identifier). Prefer `AssetReference` fields for anything wired in the Inspector; reserve string keys/labels for runtime-determined content.
- **Catalog**: maps addresses/keys to physical resource locations, generated at content-build time; paired with a hash file when remote content needs update-checking.

## Groups, profiles, and the API layer underneath

- **Groups** are the unit of organization every Addressable asset must belong to; they carry the schema that decides packing behavior (see below) and, for the AssetBundle system, map directly to output bundles.
- **Profiles** hold the build/load path variables (Local Build Path, Remote Build Path, Local Load Path, Remote Load Path) that build scripts consume. Never hardcode a CDN URL or local path in code — drive it from a Profile variable, and keep a separate Profile per environment (Development/Staging/Production) so switching environments is a Profile swap, not a code change.
- Under the static `Addressables` facade sits `ResourceManager`, which routes to `IResourceProvider` implementations keyed by `IResourceLocation`. This layer is rarely touched directly — its existence mainly matters for understanding that "loading by key" is really "resolve key → `IResourceLocation` → hand to the right provider," which is why a key that resolves to nothing fails at resolution, not at the provider.

## Dependency model — the most common source of silent duplication

Three ways an Addressable asset can reference other content, and the consequence of each:

1. **Explicit Addressable dependency** — another asset that is itself Addressable. Packed according to *its own* group settings (same bundle/directory, or a different one) — Unity resolves this cleanly regardless of which group either asset lives in.
2. **Non-Addressable dependency** — a plain project asset that is *not* marked Addressable but is referenced by one that is. Unity automatically bundles it alongside whatever references it. If **more than one** Addressable (in the AssetBundle system, potentially across different bundles) references the same non-Addressable asset, that asset gets duplicated into each referencing bundle — multiple copies at runtime instead of one shared instance, inflating both build size and memory.
3. **Implicit vs. explicit inclusion** — an implicit dependency (pulled in only because something references it) behaves identically to an explicit one for bundling purposes, but is easy to lose track of when auditing why a bundle is larger than expected.

Best practice: whenever a plain asset is referenced from more than one Addressable, **make it Addressable itself** and place it in its own group (or a group with the assets that share it) so Unity treats it as one explicit, shared dependency instead of silently duplicating it per referencing bundle. The Content Directory system already deduplicates shared non-Addressable assets automatically — this specific failure mode is one of the concrete reasons that system's default dependency hygiene is better, and one more reason to prefer it when remote delivery isn't required.

## Group organization strategy

Three organizing principles, not mutually exclusive — pick per-group based on what the group is for:
- **Concurrent usage**: group assets that load together, e.g. everything a specific level needs. Minimizes the number of separate loads a scene transition triggers.
- **Logical entity**: group a self-contained thing's assets together (a character's model, textures, animations, and sounds as one group).
- **Type-based**: group by asset category (all music, all UI textures) when content doesn't cluster naturally by level or entity.

On the Content Directory system, group choice mainly affects editor organization, since everything still builds into one directory. On the AssetBundle system, group choice directly determines bundle boundaries, so it also has real runtime performance/memory consequences — see `PackingGroupsAsBundles.html`-derived guidance below.

## Bundle packing strategy (AssetBundle system only)

| Mode | What it does | Trade-off |
|---|---|---|
| Pack Together | All assets in the group → one bundle | Fewer bundles, but a single load pulls in everything in that bundle even if only one asset is needed |
| Pack Separately | Each asset → its own bundle | Maximum granularity, but bundle count and per-bundle catalog/metadata overhead grows |
| Pack Together by Label | Assets sharing identical label sets → one bundle each | A middle ground organized around semantic content categories |

General sizing guidance: fewer, larger bundles minimize total memory footprint but can't be partially unloaded (an unused asset inside a still-referenced bundle stays resident) and a failed download restarts the whole bundle rather than resuming; many small bundles allow finer-grained unloading and resumable downloads but add per-bundle overhead (catalog bloat, concurrent-download limits) and raise the odds of the non-Addressable-dependency duplication problem above if shared content isn't factored out. Keep any single bundle under 4 GB regardless of platform. There is no universally-correct answer — decide per project scale and remeasure with the Build Layout Report rather than picking a mode by folklore.
