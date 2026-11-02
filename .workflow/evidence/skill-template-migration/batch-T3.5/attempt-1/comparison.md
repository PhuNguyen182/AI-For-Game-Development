# Comparison: batch T3.5, attempt 1

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`.
- **Verdict:** fail. Failing skills: `flexalon-layouts`, `unitask-async-programming`, `osa-optimized-scrollview-adapter`, `litmotion-tweening`, `vcontainer-dependency-injection`, `ui-toolkit`, `unity-scriptableobject-architecture`.
- **Other 7 skills:** every Base criterion kept or moved as listed below: `ugui`, `mobile-safe-area`, `unity-localization-text`, `dotween-tweening`, `odin-inspector`, `r3-reactive-extensions`, `messagepipe-event-messaging`. Kept lines are not listed.

## Findings

Line numbers: Base at the Base sha, current in the working tree. Every replacement `SKILL.md` line is under 200 chars and keeps its step number.

| Skill | Check | Base text | Current text | Why it fails | Exact fix |
|---|---|---|---|---|---|
| `flexalon-layouts` | 1, 2 (`Verified` line deleted; check lost) | `:56` "Verified: <Profiler numbers vs budget, or \"not run\">" | `SKILL.md:63` "**Report:** frame time and allocations." | The comparison against the budget lived only in that line. No step and no reference holds it (`grep -i budget` over the skill folder: 0 hits). Author's note covers the measuring, not the verdict. "Not run" is the envelope's. | Replace `SKILL.md:63`: ``    - **Report:** frame time and allocations vs budget.`` |
| `flexalon-layouts` | 2, 5 (new permission contradicts a kept field) | `:27` "Confirm the edition and version installed ... Unstated → ask."; `:50` "Edition & version: <confirmed, not assumed>" | `SKILL.md:68` "**Otherwise:** proceed on a stated assumption."; `:81` keeps "<confirmed, not assumed>" | The inventory class was applied as written, but the template's assumption branch allows what the kept Output field forbids. Base never allowed assuming the edition. This is the spec's Strict form: no assumption branch. | Delete `SKILL.md:68`. |
| `unitask-async-programming` | 1, 2 (`Verification` line deleted; check lost) | `:33` "Verification: <how an allocation or timing claim was confirmed, or \"not applicable\">" | absent; no `references/` folder exists | Author calls it generic. Refuted: the subject (allocation and timing claims) is domain-specific and named only there. The skill's H1 sells "Allocation-Free", and step 4 is about timing. `dotween-tweening` step 11 keeps its counterpart as a step. Brief: a domain limit in that line becomes a step. | Add after `SKILL.md:45`: ``10. **Allocation or timing claim:** report how it was confirmed, or "not applicable".`` |
| `osa-optimized-scrollview-adapter` | 6, 8 (invented claim in reference and header) | Fence `pooling-and-performance.md:24` uses `_Params` and states no owner | `references/pooling-and-performance.md:24` "The host class declares `_PreMadeViews` and `_Params`"; `scripts/PreMadeRowsAdapterMembers.cs:3` "a _Params field" | Base never says the host declares `_Params`. `item-interaction-and-decorators.md:20` uses it in the same method with no declaration, and `core-classes-and-lifecycle.md:17` puts the params type on the base `OSA<MyParams, ...>`. An agent that obeys adds a field shadowing the base member. The vendored source is not in this repo, so the inherited member itself was not read. | Replace `PreMadeRowsAdapterMembers.cs:3`: ``// Needs in the host class: a _PreMadeViews list of pre-made row roots, and the project's MyItemViewsHolder type.`` The reference fix is the next row. |
| `osa-optimized-scrollview-adapter` | 6 (reference names no adapt target) | Fence named no location | `references/pooling-and-performance.md:24` has no adapt target, while `scripts/PreMadeRowsAdapterMembers.cs:2` has one, and the file is correctly absent from `## Scripts` | Brief "Moved-code wording": the reference must say the adapt target. The reference is the only route to this file. T3.3 and T3.4 use a nested `**Adapt into:**` bullet. `<Feature>/<Name>Adapter.cs` also misses the folder rule: `core-classes-and-lifecycle.md:12` makes the adapter a MonoBehaviour, and `naming-convention.md` sends those to `Views/`. | In `references/pooling-and-performance.md:24` delete the final sentence, "The host class declares ... marking it unverified." Add after it: ``  - **Adapt into:** the project's OSA adapter class (derives `OSA<TParams, TItemViewsHolder>`), or `Assets/_Project/Scripts/<Feature>/Views/<Name>Adapter.cs` when none exists; the file holds class members only, and `_PreMadeViews` and `MyItemViewsHolder` are project code; the file keeps a 4-line header marking it unverified.`` Replace `PreMadeRowsAdapterMembers.cs:2`: ``// Adapt into: the project's OSA adapter class (derives OSA<TParams, TItemViewsHolder>), or Assets/_Project/Scripts/<Feature>/Views/<Name>Adapter.cs when none exists (members only)`` |
| `litmotion-tweening` | 2 (dropped condition) | `:33` "UniTask/R3/UniRx availability, Unity version or hot-path volume unstated → read `docs/tech-stack.md` and the manifest; still unknown → `Blocked`" | `SKILL.md:50`-`:51` "**Unstated:** UniTask/R3/UniRx availability, ..." then "**Read:** `docs/tech-stack.md` and the manifest." | The split cut the condition from its action. "Read" now stands unconditional, and "Unstated" has no action. | Replace `SKILL.md:50` and `:51` with one line: ``   - **UniTask/R3/UniRx availability, Unity version or hot-path volume unstated:** read `docs/tech-stack.md` and the manifest.`` |
| `litmotion-tweening` | 6 (reference target imprecise; folder off the layout) | Fence named no location | `references/litmotion-animation-component.md:26` "Adapt into a new Client script"; `scripts/CustomAnimationComponents.cs:2` `<Feature>/Animation/CustomAnimationComponents.cs` | The two texts disagree, and the reference names no path. `Animation/` is no folder in the `naming-convention.md` layout, and its namespace segment `.Animation` collides by name with `UnityEngine.Animation`. These are UI-bound components, so `Views/`. | In `references/litmotion-animation-component.md:26` delete the final sentence, "Adapt into a new Client script; ... unverified." Add after it: ``  - **Adapt into:** `Assets/_Project/Scripts/<Feature>/Views/CustomAnimationComponents.cs`; fill the `Play()` placeholder first; the file keeps a 3-line header marking it unverified.`` Replace `CustomAnimationComponents.cs:2`: ``// Adapt into: Assets/_Project/Scripts/<Feature>/Views/CustomAnimationComponents.cs (Client code; fill the Play() placeholder first)`` |
| `flexalon-layouts` | 6, 8 (reference target imprecise; folder; invented header clause) | Fence named no location | `references/custom-layouts.md:19` "Adapt into a new Client script"; `scripts/HelixStackLayout.cs:2` "(Client code, one new file per custom layout)"; `SKILL.md:34` `<Feature>/HelixStackLayout.cs` | The reference names no path. `custom-layouts.md:5` makes `LayoutBase` a MonoBehaviour, and `naming-convention.md` sends those to `Views/`. "One new file per custom layout" is a rule Base never states. | In `references/custom-layouts.md:19` delete the final sentence, "Adapt into a new Client script; ... unverified." Add after it: ``  - **Adapt into:** `Assets/_Project/Scripts/<Feature>/Views/HelixStackLayout.cs`; the file keeps a 3-line header marking it unverified.`` Replace `HelixStackLayout.cs:2`: ``// Adapt into: Assets/_Project/Scripts/<Feature>/Views/HelixStackLayout.cs (Client code)`` Replace `SKILL.md:34`: ``- **[HelixStackLayout.cs](scripts/HelixStackLayout.cs):** adapt into `Assets/_Project/Scripts/<Feature>/Views/HelixStackLayout.cs` → a complete `LayoutBase` subclass that stacks children along Y and rotates each about Y.`` |
| `vcontainer-dependency-injection` | 2 (shared scope) | `:17` "`LifetimeScope.EnqueueParent(parent)` (optionally `LifetimeScope.Enqueue(builder => ...)`) *before* `SceneManager.LoadSceneAsync(...)`" | `SKILL.md:33` "**Order:** the enqueue call goes *before* ..." | Base's "before" covers both calls. "The enqueue call" follows the `Enqueue` bullet and binds to it alone, so `EnqueueParent`, the required call, loses the order. | Replace `SKILL.md:33`: ``     - **Order:** `EnqueueParent` and the optional `Enqueue` go *before* `SceneManager.LoadSceneAsync(..., LoadSceneMode.Additive)`.`` |
| `ui-toolkit` | 2 (title widening; orphan reference) | `:10` "read at Unity 6.5 / 6000.5; best-practice guide validated on 6.0; UI Test Framework `com.unity.ui.test-framework@1.0`). Defaults quoted in references were read at that version" | `SKILL.md:16` "**Validated on:** the best-practice guide on 6.0; UI Test Framework ..."; `:17` "read at that version" | The title now says the test framework pin was validated, which Base never says. "That version" repeats Base's "read at" (6.5), yet now follows a bullet naming 6.0 and 1.0. | Replace `SKILL.md:16` and `:17` with three lines: ``  - **Best-practice guide:** validated on 6.0.`` ``  - **UI Test Framework:** `com.unity.ui.test-framework@1.0`.`` ``  - **Defaults quoted in references:** read at Unity 6.5 / 6000.5; re-check on the installed Editor.`` |
| `unity-scriptableobject-architecture` | 2 (orphan reference) | `:23` "using the Read-when column" | `SKILL.md:29` "using the Read-when column of the References list." | The table is gone, so no column and no "Read when" label exists; the target is each bullet's trigger. | Replace `SKILL.md:29`: ``2. **Pick the pattern from the requirement:** using each reference's trigger under `## References`.`` |

## Named items tested

- **`Verified`/`Verification` lines (7 skills):**
  - **`ui-toolkit`, `dotween-tweening`, `unity-localization-text`:** `<evidence, or "not run">`, no domain content; envelope. Pass.
  - **`osa-optimized-scrollview-adapter`:** survives at `SKILL.md:63`-`:64`, including "not measured". Pass.
  - **`litmotion-tweening`:** survives at `SKILL.md:58`-`:62` with the 0 GC alloc check. "Not yet run" is the envelope's `Not verified`, as T3.4 ruled. Pass.
  - **`flexalon-layouts`, `unitask-async-programming`:** findings above.
- **`osa` steps 2 and 14:** all four inputs and the reason stay at step 2, `:42` points to step 14, step 14 is last, inventory fix applied. "Confirm" adds no fact over "Ask if unstated". Pass.
- **`ui-toolkit` step 2 as `Missing input`:** matches inventory `ui-toolkit:28`. Number and subject stay, the Panel Renderer reason stays, and the assumption branch matches Base. No other step moved. Pass.
- **`vcontainer` step 8:** the chain is complete and in Base order. "Fixed ticks", "Frame ticks" and "Teardown" only label it, and the leading `→` keeps it continuous. It agrees with the citer at `core-scene-integration/references/input-and-physics-into-core.md:12`. Pass.
- **`vcontainer` step 5:** finding above; every other clause kept.
- **`unity-localization-text` RTL split:**
  - **`Never`:** Base `:46` "RTL locales excluded" plus `:9` "no owner — known limitation" gives `SKILL.md:75`, with no added fact.
  - **Rich text:** the `richText`/`<` condition stays at `:72`-`:74`, with the argument rule and the consequence.
  - **Result:** pass.
- **`*` tokens out of titles:** `ugui:52` `IPointer*Handler`, `litmotion:38` `BindTo*`, `vcontainer:55` `IPost*`. Each keeps its condition and subject. Pass.
- **`CustomAnimationComponents.cs`:** the file body is byte-identical to the Base fence, placeholder included, and "does not compile until filled" is true of it. Omission is correct; see the table below. The author's stated reason is not the rule's test.
- **`coexistence-and-migration.md:19`:** `litmotion-tweening` in backticks plus the file name follows the Portability rule and the `batches.md` trap. The file exists, and `litmotion-tweening/SKILL.md:29` lists it with the trigger "Porting DOTween/...". An agent reaches it in one hop. Pass.

## Moved code

| File | Fence at Base | Body vs fence | Header | Decision on `## Scripts` | Reached through |
|---|---|---|---|---|---|
| `flexalon-layouts/scripts/HelixStackLayout.cs` | `custom-layouts.md:19`, 20 lines | byte-identical | 3 lines; target finding | listed, correct: complete type | `SKILL.md:34`, `:60` |
| `litmotion-tweening/scripts/CustomAnimationComponents.cs` | `litmotion-animation-component.md:26`, 17 lines | byte-identical | 3 lines; target finding | omit is correct: the `Play()` skeleton must be filled, and the base-class choice (`:24`) and the `OnStop` restoration caveat (`:30`) are stated only in the reference | `SKILL.md:28` trigger "custom animation component" |
| `osa-optimized-scrollview-adapter/scripts/PreMadeRowsAdapterMembers.cs` | `pooling-and-performance.md:24`, 23 lines | byte-identical | 4 lines; findings | omit is correct: members only; the `else` throw trade-off is in the reference | `SKILL.md:29` |

- **Method:** script compared each fence's raw bytes with the file after its header; both LF. The only difference is the file's trailing newline.
- **Fences left:** no 15+ line fence in the three references; verify reports none.

## Moves

| Base | Current |
|---|---|
| `unity-localization-text:46` "RTL locales excluded" | `SKILL.md:75` |
| `osa:57` Profiler evidence or "not measured" | `SKILL.md:63`-`:64` |
| `litmotion:53` Profiler alloc check | `SKILL.md:61` |
| `ui-toolkit:3` `UnityEngine.UIElements` (description) | `SKILL.md:15` |
| Fence facts for three samples | sample bullets in the three references |

## Cuts

| Skill | Base text | Class |
|---|---|---|
| All but `mobile-safe-area`, `unity-localization-text` | "On request only, add `Latent concerns` and `Future remediation` ..." | brief "Remove or move" |
| All 14 | `Known limitations: <...>` in `Output` | envelope field |
| `ui-toolkit`, `dotween-tweening`, `unity-localization-text` | `Verified: <evidence, or "not run">` | envelope field |

## Tokens

- **Run:** `TOTAL 14 skill(s), 3162 tokens, 50 missing`, 0 found only in `scripts/`. It matches the author's count: 24 deleted by rule, 13 description symbols, 12 bold titles, 1 link. Each is resolved.
- **`Latent concerns`, `Future remediation` (24):** deleted by rule; confirmed.
- **Description slash compounds (13):** each part found in the body or the named reference. One author detail is wrong and harmless: `UIDocument` is at `ui-toolkit` step 8, not step 9, and `Renderer` is steps 2 and 8.
- **Bold titles (12):** arrow or sentence tail became `Title:`, wording kept; confirmed.
- **Link (1):** see above.
- **Author's report, refuted:** the `unitask` line ("generic verification") and the `flexalon` line (Profiler verdict "still" in step 11), both findings above.

## Other checks

- **Anchors:** every `anchors.md` row for these skills resolves to the same subject: `litmotion` step 9; `mobile-safe-area` steps 4, 5, 6, 9; `odin` step 7 and the two `csharp-standards` citations; `ugui` steps 3, 5; `unitask` steps 2, 3, 5; `vcontainer` step 8; the `ui-toolkit` file citations.
- **Ask:** `ask-check.ps1` shows no open hit in these 14 skills. Each of `ugui:26`, `ui-toolkit:28`, `osa:26`, `flexalon:27` has its inventory fix; `flexalon` has the finding above. Allowlisted lines stay.
- **Sections:** all 14 are class "Steps", in template order; the 4 skills without `references/` have no `## References`, and none has an empty section.
- **Scope:** frontmatter equals `HEAD` in all 14. Reference edits are only the moved code and the one link.
- **Verify:** `verify.ps1 -File` on each of the 14 `SKILL.md` and 4 references: 0 warnings. Whole layer: `verify-layer: OK (21 warning(s))`, exit 0, no `file(s):` line. Replacement text was checked by reading, not by a re-run.
