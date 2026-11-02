# Comparison: batch T3.7, attempt 1

Base `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`. Comparator is not the author. Read-only on tracked files. Line numbers are the current working-tree `SKILL.md`.

## Verdict
**Fail.** 9 of 15 skills fail.

| Failing skill | Findings | Kind |
|---|---|---|
| `unity-lighting` | F1 | Check lost; author's claim refuted |
| `unity-post-processing` | F2, F6b | New step is circular; elliptical bullet |
| `unity-urp-rendering` | F3a | Ask fix differs from inventory; order lost |
| `unity-hdrp-rendering` | F3b | Ask fix differs from inventory; order lost |
| `unity-collections` | F3c | Order lost |
| `unity-entities-graphics` | F3d | Order lost |
| `shader-authoring` | F4 | Option list detached from its condition |
| `unity-mathematics` | F5a, F5b | Shifted qualifier; possibility became fact |
| `vfx-particle-authoring` | F6a | Orphan reference |

Clean: `render-pipeline-urp-hdrp`, `compute-shader-vfx`, `unity-burst-compiler`, `unity-job-system-and-burst` (one cosmetic note below), `unity-ecs-architecture`, `unity-physics`.

## Findings

### F1 `unity-lighting` SKILL.md, after line 67
- **Check:** 1, criteria; test of the author's claim (`token-survival.md`: "step 12 keeps the measurement").
- **Base (:64):** `- Verified on: <device/tier, bake and frame time — or "not run">`
- **Current:** line deleted. Step 12 is `Attach a measurement to any performance claim: bake time, frame time or memory on the claimed tier`.
- **Why it fails:** refuted. Step 12 fires only when a performance claim is made. Base's field asked every lighting output for a device or tier with bake and frame time. A bake with no claim now has no device or tier check. `Bake:` keeps bake time only. Frame time and device/tier appear nowhere else, and no reference holds them. This is the loss pattern from T3.6 F3, and the author added the matching step for `unity-post-processing` but not here.
- **Fix:** insert after line 67:
```
13. **Device or tier:** verify on one, and name it with the bake time and frame time measured.
```

### F2 `unity-post-processing` SKILL.md:54
- **Check:** 1, criteria; batch brief "Circular checks".
- **Base (:45):** `- Verified: <tier/device captured; Profiler data behind any perf claim, or "not run">`
- **Current:** `10. **Verify on the tier and device captured:** name the tier and device, and cite the Profiler data behind any performance claim.`
- **Why it fails:** the title says verify on whatever was captured, so any capture passes. Same defect as T3.6 F4. Base's obligation is a capture on the tier in question; step 2 already names it "the target tier".
- **Fix:** replace line 54 with:
```
10. **Tier and device:** verify on the target tier, and name the tier and device captured; cite the Profiler data behind any performance claim.
```

### F3 `Missing input` moved last with nothing left at the origin
- **Check:** 5, ask fix; 1, required order.
- **Why it fails:** in Base each ask sits inside the step that needs the value, before the work that depends on it. Now the ask is only in the last step, after every step that uses the value. URP is worst: Base asks in step 1 ("every later step applies to one asset"); the ask now follows step 10, the device capture. HDRP's step 8 and 9 now precede its ask.
- **Inventory:** `unity-urp-rendering:21` says `"Tier unstated → Missing input step"; adds that step`. `unity-hdrp-rendering:30` says `"Scope unstated → Missing input step"; adds that step`. Both require the pointer at the origin, and the author added only the step. The inventory's `Strict` rows for `unity-collections:20` and `unity-entities-graphics:23` name only the step, but the order loss is the same.
- **Precedent:** the committed `osa-optimized-scrollview-adapter:42` (`**Unstated:** step 14.`) and `ugui:35` (`... unstated:** step 13.`).
- **Meaning of the moved text:** kept in all four. No assumption branch, matching Base. `never infer`, `guessing picks the wrong container` and the input lists all survive. Only the position fails.

| Id | Location | Base | Replacement: insert after the named line |
|---|---|---|---|
| F3a | `unity-urp-rendering` after :30 | `Ask which tier a change is for when unstated.` (:21) | `   - **Tier a change is for unstated:** step 11.` |
| F3b | `unity-hdrp-rendering` after :46 | `scope unstated → ask` (:30) | `   - **Platform scope unstated:** step 10.` |
| F3c | `unity-collections` after :27 | `if any is unstated, ask` (:20) | `   - **Any of the three unstated:** step 10.` |
| F3d | `unity-entities-graphics` after :33 | `Not stated → ask; never infer from a URP asset being present.` (:23) | `   - **Any of the four not stated:** step 14.` |

### F4 `shader-authoring` SKILL.md:28-31
- **Check:** 2, plain words; batch brief "Dropped condition", "Orphan reference".
- **Base (:16):** `Both hold: where per-instance variation is wanted at scale, report the conflict and let a measurement choose between material variants (small fixed palette), GPU instancing (many instances of one mesh), or keeping the block (low count).`
- **Current:** `**Both hold:** ... let a measurement choose.` followed by three sibling bullets: `**Material variants:** a small fixed palette.`, `**GPU instancing:** many instances of one mesh.`, `**Keeping the block:** low count.`
- **Why it fails:** "choose" lost its object, and the three options lost their link to the measurement and to "at scale". As siblings they read as standalone facts. Step 4 is cited by `technical-artist.md:58`, so the number and title stay.
- **Fix:** replace lines 28-31 with:
```
   - **Both hold:** where per-instance variation is wanted at scale, report the conflict and let a measurement choose between these options:
     - **Material variants:** a small fixed palette.
     - **GPU instancing:** many instances of one mesh.
     - **Keeping the block:** low count.
```

### F5 `unity-mathematics`
- **F5a, SKILL.md:43. Check:** 5, ask fix; batch brief "Shifted qualifier". Base (:27): `Layer or seed origin unstated → ask before writing.` Current ends `main session `AskUserQuestion`, before writing.` The inventory keeps "before writing", but it now trails the main-session clause, so a dispatched agent's `Blocked` no longer carries it. Replace line 43 with:
```
9. **Missing input:** before writing, layer or seed origin unstated → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.
```
- **F5b, SKILL.md:40. Check:** 2, plain words; batch brief "Invented claim". Base (:25): `SIMD codegen, FloatMode and transcendental precision can still differ across platforms`. Current title: `Still differing across platforms:`, which states as fact what Base states as a possibility. Replace line 40 with:
```
   - **Can still differ across platforms:** SIMD codegen, `FloatMode` and transcendental precision.
```

### F6 Orphan references (batch brief "Orphan reference": repeat the noun)
| Id | Location | Base | Current | Replacement line |
|---|---|---|---|---|
| F6a | `vfx-particle-authoring` SKILL.md:33 | `A second authored version for that tier is a legitimate outcome` (:22); "that tier" = a tier without it | `**Second authored version for that tier:** ...`, directly under `**Broad Android:**`, its nearest wrong reading | `   - **Second authored version for a tier without support:** a legitimate outcome; decide it up front.` |
| F6b | `unity-post-processing` SKILL.md:49 | `before post-processing = tonemapped and graded; after = not` (:27) | `**After post-processing:** the effect is not.` | `   - **After post-processing:** the effect is not tonemapped or graded.` |

### Cosmetic, not a failure
- **`unity-job-system-and-burst` SKILL.md:61:** trailing space after `in either direction:**`. Delete it. The only trailing space in the batch.

### Fix check
All replacements above were applied to scratch copies with an exact-match assertion on each target line. `verify.ps1 -File` on each copy, references alongside: `verify-layer: OK (0 warning(s))`. Copies removed. No tracked file edited.

## The brief's named tests

| Test | Result |
|---|---|
| Deleted `Verified` lines | 6 hold; `unity-lighting` fails (F1); `unity-post-processing` step 10 fails (F2). Table below. |
| `Missing input` meaning | Pass in all: conditions, inputs, `never infer`, `a person decides`, `guessing...` kept, no assumption branch added. Position fails in four (F3); `before writing` shifted (F5a). |
| `render-pipeline-urp-hdrp` step 9 | Pass. Line 41 keeps "never pick it", the parenthetical and "a person decides". Number 9 stays. No anchor cites it. |
| `Companion` bullets | Pass. Each keeps its when: `render-pipeline-urp-hdrp:17` "once it is approved" with `:18` ownership; `unity-urp-rendering:20` "reviews a finished Render Graph feature"; `shader-authoring:18` "turns existing HLSL into a Shader Graph custom node". All keep "if installed". |
| `unity-post-processing:18-19` plugin bullet | Pass. "wins on conflict" and the `VolumeManager.instance.stack` exception kept. |
| `unity-lighting` Never split | Pass. `:74-75`: "in new SRP work" on both bullets, each replacement on its own type, "obsolete" on both. |
| `unity-mathematics` seed bullet | Pass. `:47` identical in scope to Base :31; "in Core" still qualifies only `UnityEngine.Random`. |
| Burst thresholds | Pass, word by word: all three `FloatMode` conditions, `Strict` default on unstated tolerance, "scoped per target, never per assembly", `CompileSynchronously = true`, precedence order, scalar fallback, `[NoAlias]` one-sentence guarantee, `DisableSafetyChecks` condition. |
| Jobs thresholds | Pass: `TempJob`/`Persistent`/`Temp` lifetimes, `IJobParallelFor` preference, `IJobParallelForTransform` "only", `[BurstCompile]` scope and entry-point exception, `Dispose(JobHandle)` condition, `WaitForJobGroup`, all three `Never` bullets. |
| Numbers elsewhere | Pass: 16 KiB, Entities 1.4, Unity 6.3 and 6.4, `@17.3`, `@17.5`, `@17.6`, `@1.8`, `@6.6`, `@1.3`, `@3.5`, 64 / 32 / 64-256, "about a hundred", "ten thousand", six face renders, 2022.3 LTS. |

## Cuts

| Cut | Class | Skills, Base line |
|---|---|---|
| `Known limitations: <...>` in `Output` | Envelope field; every one is `<...>`, no domain limit inside | All 15 |
| "On request only" line | Meta line per batch brief; all identical, no named domain trigger | render :35, urp :50, hdrp :50, shader :42, vfx :53, compute :42, lighting :67, post :48, jobs :53, ecs :58, entities :54, physics :53 |
| `Verified` family in `Output` | Envelope field, once its check is in a step | Table below |

No "Common knowledge" cut in the batch.

| Skill, Base line | Base field | Check now held by | Result |
|---|---|---|---|
| urp :47 | `Verified on: <quality tier and device class captured>` | Step 10, `:52` | Holds |
| hdrp :47 | `Verified on: <Asset and hardware tier captured, or "not run">` | Step 9, `:48` | Holds |
| shader :39 | `Platforms verified: <each target actually captured>` | Step 9, `:38` (anchor) | Holds |
| vfx :50 | `Verified: <in-engine capture: tier, background — or "not run">` | Step 10, `:45` | Holds |
| lighting :64 | `Verified on: <device/tier, bake and frame time — or "not run">` | Step 12 covers claims only | **Fails, F1** |
| post :45 | `Verified: <tier/device captured; Profiler data ...>` | New step 10, `:54`, circular | **Fails, F2** |
| ecs :54 | `Verified via: <Hierarchy / Systems window — what was confirmed>` | Step 12, `:49-53` | Holds |
| math :42 | `Verification: <precision check, or n/a>` | Step 8, `:42` | Holds |

Kept as domain fields, confirmed in `Output`: burst `Compilation verified`, `Measurement`; jobs `Measurement`; entities `Batching measured`; ecs `Measurement`; compute `Platform support`, `Cost`.

## Moves

| Skill | Base | Now |
|---|---|---|
| `unity-urp-rendering` | Step 1 tier ask (:21) | `:54` step 11; pointer owed (F3a) |
| `unity-hdrp-rendering` | Step 7 scope ask (:30) | `:49` step 10; pointer owed (F3b) |
| `unity-collections` | Step 1 ask and reason (:20) | `:42-43` step 10; pointer owed (F3c) |
| `unity-entities-graphics` | Step 2 ask and `never infer` (:23) | `:56-57` step 14; pointer owed (F3d) |
| `render-pipeline-urp-hdrp` | Step 9 retitled (:21) | `:40-41`, same number, inventory class Strict |
| `shader-authoring` | Step 10 retitled (:22) | `:39-40`, same number, inventory class Strict |
| `unity-mathematics` | Step 9 retitled (:27) | `:43`, same number, inventory class Strict |
| `unity-mathematics` | Step 3 "Same file." (:21) | `:30` names `vector-and-matrix-types.md`; correct |

Step numbers: all Base numbers keep their subjects in all 15; new steps only after the last. Anchored `shader-authoring` 3, 4, 9 and `compute-shader-vfx` 10 match `anchors.md:109-112`.

## Tokens
`token-survival.ps1` rerun: `TOTAL 15 skill(s), 1383 tokens, 49 missing`, same per-skill counts as the author. Split confirmed by recount: 25 + 14 + 10.

- **25 deleted by rule:** confirmed. 12 skills × `Latent concerns` and `Future remediation`, plus `Known limitations` in render :35.
- **14 description symbols:** confirmed resolved in body or references by grep: `ScriptableRenderPass`, `VolumeProfile`, `VolumeComponent`, `NativeQueue`, `float4x4` in references; the rest in the body. One author detail is off: compute "mesh deformation" is 0 in the body, only in the description. `Mesh` and "deformation" are each in the body, so no loss.
- **10 bold titles:** confirmed, wording kept. Two of them carry findings on other grounds: `unity-collections` (F3c), `unity-mathematics` (F5a).

## Other checks
- **Anchors:** every `anchors.md` row for these skills resolves; each cited `csharp-standards` heading is still named on its citing line. References are untouched.
- **Ask:** `ask-check.ps1 -Skills <15>`: `3 hit(s), 3 allowlisted, 0 open`. Fragments `nobody asked for` and `which asks Core whether` still match. Class versus fix: F3a, F3b, F5a above.
- **Moved code:** none in this batch; none of the 15 has a `scripts/` folder.
- **Sections:** all 15 are domain skills with `## Steps`. `unity-lighting` keeps `## Which asset owns which setting` and its data table; step 1's "table above" still resolves.
- **Scope:** frontmatter identical to `HEAD` in all 15. `git status` shows only the 15 `SKILL.md` files under `.claude/skills/`. No added knowledge besides the findings above.
- **Verify:** `verify.ps1 -File` on all 15: `OK (0 warning(s))`. Whole layer: `verify-layer: OK (21 warning(s))`, exit 0.
