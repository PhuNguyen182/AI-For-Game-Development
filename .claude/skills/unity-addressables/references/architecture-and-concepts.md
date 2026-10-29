# Architecture and Concepts

Sources (Addressables 4.0 manual): `content-build-systems.html`, `AddressableAssetsOverview.html`, `organize-addressable-assets.html`, `PackingGroupsAsBundles.html`, `AssetDependencies.html`, `optimization-tools.html`.

## Content build system (project-wide, never per group)
| Axis | Content Directory | AssetBundle |
|---|---|---|
| Dependency tracking | Per asset; shared plain assets deduplicated automatically | Per bundle; a shared plain asset is copied into each referencing bundle |
| Unload | Asset frees once its own direct dependencies free | Asset stays until its whole bundle's count reaches zero |
| Remote delivery | Local only: no remote path, no catalog update flow | Local and remote; the only system with post-launch content updates |
| Groups | Build into one directory; grouping is organizational | Map to bundles; grouping has runtime consequences |
| Editor | Needs a recent Editor | Every supported version |

Carrying both builds shared dependencies twice and inflates size while the Groups window looks correct.

## Addressing
- Address: stable name; code stops depending on file location.
- Label: shared tag; loading by label pulls every match, so a mistyped label returns nothing instead of failing.
- `AssetReference`: serialized GUID; survives rename/move where a string address breaks.
- Catalog: key-to-location map made at content-build time; a missing key fails at resolution, before any provider.
- Group: unit every Addressable belongs to; its schema sets packing and whether it is built.

## Grouping principle
- Concurrent usage: needed at the same moment (everything one level loads).
- Logical entity: one thing owns its model, textures, animations, audio; one lifetime.
- Type based: content does not cluster by level or entity (all music, all UI atlases).

## Packing modes (AssetBundle system)
| Mode | Effect and trade-off |
|---|---|
| Pack Together | One bundle per group; loading one asset loads the whole bundle, nothing unloads until every reference is gone |
| Pack Separately | One bundle per asset; finest unload and resumable downloads, but catalog overhead and many requests |
| Pack Together by Label | One bundle per label set; works only if labels already describe usage |

## Dependency duplication
- Addressable referencing another Addressable: packed by the referenced asset's own group; shared cleanly.
- One Addressable referencing a plain asset: it rides in that bundle; no cost.
- Two or more Addressables referencing the same plain asset: copied into every referencing bundle (AssetBundle system), visible only as unexplained build size.
- Fix: make the shared asset Addressable in its own group; the Analyze window reports duplicates before shipping.
