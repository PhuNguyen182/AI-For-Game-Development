# Comparison: batch T3.6, attempt 1

Base `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`. Comparator is not the author. Read-only on tracked files.

## Verdict
**Fail.** 8 of 14 skills fail.

| Failing skill | Findings | Kind |
|---|---|---|
| `unity-audio-mixer` | F1 | Shifted qualifier, orphan reference |
| `unity-addressables` | F2 | Rule weakened to scope |
| `spine-animation` | F3 | Check lost; author's claim refuted |
| `unity-camera-fundamentals` | F4 | Moved check became circular |
| `unity-navmesh-navigation` | F5 | Guardrail restates step 6 |
| `unity-animation` | F6a | Orphan reference |
| `unity-2d-spriteshape` | F6b, F6c | Orphan references |
| `unity-tilemap` | F6d | Orphan reference |

Clean: `unity-input-system`, `unity-3d-physics`, `unity-2d-physics`, `unity-cinemachine-authoring`, `unity-2d-sprite`, `unity-3d-mesh`.

## Findings

### F1 `unity-audio-mixer` SKILL.md:16-17
- **Check:** 2, plain words.
- **Base (:10):** `The Manual publishes no Duck Volume parameter table and states several Editor slider bounds only by convention; never invent those numbers, read them in the Inspector.`
- **Current:** `**Duck Volume:** the Manual publishes no parameter table, and states several Editor slider bounds only by convention.` / `**Those numbers:** never invent them; read them in the Inspector.`
- **Why it fails:** in Base, "Duck Volume" qualifies only the table; the slider bounds are general. The title now scopes them to Duck Volume, so the ban on inventing a bound no longer visibly covers other sliders. "Those numbers" has no noun in its own bullet.
- **Fix:** replace lines 16-17 with:
```
  - **Duck Volume:** the Manual publishes no parameter table for it.
  - **Editor slider bounds:** the Manual states several only by convention.
  - **Duck Volume parameters and slider bounds:** never invent those numbers; read them in the Inspector.
```

### F2 `unity-addressables` SKILL.md:15
- **Check:** 1, criteria (ban); 8, invented scope.
- **Base (:9):** `Addressables calls stay in Client code; Core takes resolved data (`csharp-standards`).` A standalone sentence after the `Not for` list.
- **Current:** `**Not for:** Core code (Addressables calls stay in Client code; Core takes resolved data, per `csharp-standards`).`
- **Why it fails:** it weakened. Every other `Not for` bullet routes a concern to an owner, so this reads as "Core work on Addressables belongs to `csharp-standards`", not as a ban on the call. The rule is now a parenthetical, and "Core code" as a scope is a claim Base never made. No step or `Never` bullet holds it.
- **Fix:** delete line 15. Add after line 51, as the last `## Never` bullet:
```
- **Call Addressables outside Client code:** Core takes resolved data (`csharp-standards`).
```

### F3 `spine-animation` SKILL.md, after line 71
- **Check:** 1, criteria; test of the author's claim (`token-survival.md:8`).
- **Base (:57):** `- Verified: <measurement behind any performance claim, or "not run">`
- **Current:** line deleted. The author says step 13 still requires the measurement.
- **Why it fails:** refuted. Step 13 is `Adopt on-demand loading only after a measurement`, which covers one decision. Base's line covered any performance claim, including the draw-call, batching and pooling claims steps 8, 11 and 14 invite. No other step or reference states it. Batch brief rule "Verified lines with domain content" requires a step. Steps 2 and 7 are the only cited numbers, so a new last step is safe.
- **Fix:** insert after line 71:
```
16. **Back any performance claim with a measurement:** no measurement, report "not run".
```

### F4 `unity-camera-fundamentals` SKILL.md:47
- **Check:** 1, criteria (the step added for the deleted `Verified on`).
- **Base (:51):** `- Verified on: <aspect ratios and device classes actually run>`
- **Current:** `16. **Verify on:** the aspect ratios and device classes actually run.`
- **Why it fails:** read as an instruction it is circular: verify on whatever was run. Any run satisfies it. Base's obligation was to state which aspect ratios and device classes ran, and the generic envelope `Verified` does not ask for those two axes.
- **Fix:** replace line 47 with:
```
16. **Aspect ratios and device classes:** verify on them, and name the ones actually run.
```

### F5 `unity-navmesh-navigation` SKILL.md:55
- **Check:** 8, template (`Never` holds only what no step covers).
- **Base (:42):** `- Carve by default.`
- **Current:** `**Carve by default:** carving is only for where pathfinding must reroute (step 6).`
- **Why it fails:** it restates step 6, and its own text says so. Step 6 (`Obstruction for anything continuously moving; carving only where pathfinding must reroute`) sets the default and the condition. The Base bullet carried no consequence of its own, so the brief's "same condition and same consequence" test is met. No distinct ban exists to preserve.
- **Fix:** delete line 55. Disposition: cut, guardrail restating step 6.

### F6 Orphan references (batch brief "Orphan reference": repeat the noun)
- **Check:** 2, plain words. In each, a split made the pronoun a sibling bullet with no antecedent in its own text. Meaning is recoverable, and the fix is one word.

| Id | Location | Base | Current | Nearest wrong reading | Replacement line |
|---|---|---|---|---|---|
| F6a | `unity-animation` SKILL.md:43 | `Drift or no movement is almost always this.` (:25) | `**Drift or no movement:** almost always this.` | The movement callback bullet just above | `   - **Drift or no movement:** almost always the root-motion source.` |
| F6b | `unity-2d-spriteshape` SKILL.md:29 | `Fill, corners and collider choice all follow from it.` (:21) | `**Follow-on:** fill, corners and collider choice all follow from it.` | The `Open` bullet just above | `   - **Follow-on:** fill, corners and collider choice all follow from the Open or Closed choice.` |
| F6c | `unity-2d-spriteshape` SKILL.md:45 | `Leave it on while the art iterates.` (:27) | `**Art iterating:** leave it on.` | The manual collider edit, the last "it" in step 7 | `   - **Art iterating:** leave Update Collider on.` |
| F6d | `unity-tilemap` SKILL.md:47 | `Composite Operation/Order do nothing without that component.` (:30) | `**Composite Operation/Order:** do nothing without that component.` | Static `Rigidbody2D`, the last noun in the parent line | ``   - **Composite Operation/Order:** do nothing without a `CompositeCollider2D`.`` |

F6d's noun is confirmed by `unity-tilemap/references/tilemap-collider-2d.md:23` (`does nothing without a CompositeCollider2D`).

## The brief's named tests

| Test | Result |
|---|---|
| Deleted `Verified` lines | 8 hold, `spine-animation` fails (F3), `unity-camera-fundamentals` step 16 fails (F4). Table below. |
| `**<act>:** forbidden.` bullets | Pass. `unity-animation:70-71`, `spine-animation:74-75` read as bans under `## Never`. "its handler" became "Animation Event handler" correctly. Base gave no consequence and none was invented. |
| "Carve by default" | It restates. Delete (F5). |
| Addressables Client-code rule | It weakened. Move to `## Never` (F2). |
| Cinemachine "rename list below" | Pass. Line 17 resolves to `## Cinemachine 2 → 3 renames` at line 27. All 8 Base renames kept, with both parentheticals. Nothing cites the old paragraph. |
| `unity-2d-sprite`, `unity-tilemap` rewrites | Sprite clean; steps 1-2 citation holds at line 49. Tilemap clean except F6d. Example splits keep every clause, including `0.5-scale Variant`, `3×3`, `custom neighbour IDs start at 3`. |
| Docs splits | `unity-navmesh-navigation` clean (all 6 slugs, both APIs, ownership, Classic pages). `unity-audio-mixer` fails (F1). |
| `unity-input-system` split triggers | Pass. Lines 21-24 hold all four clauses word for word; "Any of these:" carries Base's "or"; titles add no fact. All other triggers in the 14 skills match Base verbatim by script. |

## Cuts

| Cut | Class | Skills, Base line |
|---|---|---|
| `Known limitations` in `Output` | Envelope field; every one was `<...>`, no domain limit inside | input :54, 3d-physics :51, 2d-physics :48, animation :58, audio :45, camera :53, cinemachine :51, navmesh :55, 2d-sprite :52, spriteshape :50, tilemap :56, 3d-mesh :48, spine :58, addressables :51 |
| "On request only" line | Meta line per batch brief; all 11 identical, no named domain trigger | input :56, 3d-physics :53, 2d-physics :50, animation :60, audio :47, cinemachine :53, navmesh :57, spriteshape :52, 3d-mesh :50, spine :60, addressables :53 |
| `Verified` family in `Output` | Envelope field, once its check is in a step | Table below |

No "Common knowledge" cut in the batch.

| Skill, Base line | Base field | Check now held by | Result |
|---|---|---|---|
| 3d-physics :50 | `Verification: Profiler / Memory Profiler / Physics Debug finding, or "not measured"` | Step 11, line 53-57, same three tools. "not measured" = envelope `Not verified`. | Holds |
| 2d-physics :47 | `Verified: Profiler / Physics Debug finding, or "not run"` | Step 11, line 50-51 | Holds |
| animation :57 | `Verified: Profiler capture behind any performance claim, or "not run"` | Step 13, line 63 ("any animation performance claim") | Holds |
| camera :51 | `Verified on: aspect ratios and device classes actually run` | Step 16, line 47 | **F4** |
| cinemachine :50 | `Verified in Play Mode: what ran, or "not run"` | Step 12, line 63 | Holds |
| navmesh :54 | `Verified on: Profiler evidence, or "no claim made"` | Step 11, line 47 | Holds |
| 2d-sprite :51 | `Verification: 2D Profiler counts and Usage %, or "not yet measured"` | Step 11, line 50 | Holds |
| 3d-mesh :47 | `Verification: Preview/Profiler finding, or "not yet measured"` | Step 10, line 43 | Holds |
| spine :57 | `Verified: measurement behind any performance claim, or "not run"` | Step 13 covers on-demand loading only | **F3** |
| addressables :50 | `Verified against: full content build / Play Mode Scripts only (not sufficient for handoff)` | Step 12, lines 45-46 | Holds |

## Moves
- **Across files:** none. No moved code in T3.6, per `batches.md`; 0 files found only in `scripts/`; no reference or script changed.
- **Within a file:** `unity-cinemachine-authoring` rename paragraph (:21) to its own section, lines 27-35. `unity-addressables` rule, F2.

## Tokens
Ran `token-survival.ps1`: 14 skills, 2196 tokens, 46 missing. Matches the author's report; 22 + 19 + 5 = 46.
- **22 `Latent concerns`, `Future remediation`:** confirmed, 11 skills, cut above.
- **19 description symbols:** confirmed. Frontmatter is unchanged from `HEAD`, so the slash compounds left in T2. Each part resolved by grep or reading: `PlayerInputManager` (`player-input-and-multiplayer.md`), `Time.fixedDeltaTime` (`physics-optimization.md`), `GameObject` singular (`ragdoll-physics.md`, `rigidbody-2d.md`), `StateDriven` (`multi-target-and-multi-shot.md`), `SetIndices` (`mesh-anatomy.md`), `MeshFilter` (`mesh-components.md`, SKILL.md), `InstantiateAsync`, `LoadSceneAsync` (`load-and-release.md`), groups and labels (`architecture-and-concepts.md`:11, :18), the rest in the bodies at the steps the author names.
- **5 bold titles:** confirmed; wording kept, condition moved after the colon. `unity-2d-physics` step 2, `unity-3d-mesh` steps 5, 7, 8, `spine-animation` step 1.
- **Author's claim refuted:** `token-survival.md:8`, spine step 13 (F3). **Weak:** `token-survival.md:11`, camera step 16 (F4). All other explanations stand.

## Other checks
- **Anchors:** resolve to the same subject. `unity-3d-physics` step 3, `unity-2d-sprite` steps 1-2, `spine-animation` steps 2 and 7 (cited at line 33), and every `csharp-standards` citation in `anchors.md` for these skills.
- **Carried from T2, not this author:** `unity-animation:21` "(Animator, AnimatorController)" is in `HEAD`. Not a finding.
- **Ask:** `ask-check.ps1` shows no open hit in these skills; 16 open hits belong to later batches. The only inventory row, `unity-tilemap/references/tile-palette-and-tiles.md:9`, is allowlisted and untouched.
- **Sections:** all 14 keep `## Steps`; none is in the skills-without-Steps table.
- **Scope:** frontmatter identical to `HEAD` in all 14. Only the 14 `SKILL.md` files changed. Output fences differ from Base only by the cut lines, by script.
- **Word count check:** a per-skill word comparison of Base against current, frontmatter and Output fences excluded, shows no plain-word condition lost beyond the items above.
- **`verify.ps1`:** 0 warnings on each of the 14; whole layer exit 0, and no warning line names these skills. Largest body `spine-animation`, 7,254 chars including frontmatter.
- **Checked, not a finding:** nested bullets under a conditional or rule title that do not depend on it (`spine-animation` step 14 Binary, Pooling; `unity-audio-mixer` step 11 Core rule). Base had the same shape in one numbered item, and each bullet stands alone.
