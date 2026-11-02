# Comparison: scoped re-read of the 81 fixes (AC7, drift D1)

Base: `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`. Tree: `385794a` plus the working tree. Reader did not write these fixes or the reports. Read-only on tracked files.

**Verdict: fail.** 6 findings across 6 lines; 75 of the 81 fixes pass, and `verify-layer/SKILL.md` and the `No envelope` line pass. No loss of a condition, limiter, threshold or order was found. The 6 are: 1 dropped scope word, 1 added claim, and 4 lines where "the file" reads as the adapt target instead of the sample.

## Findings
Lines are working-tree lines. All replacements stay within budget: `feature` 114 chars, `backend-build-vs-buy` 120 chars.

| # | file:line | Base text | Current text | Why it fails | Exact replacement |
|---|---|---|---|---|---|
| R1 | `.claude/skills/feature/SKILL.md:3` (T2) | "...CP4. Also handles change requests and abandonment." | `M/L feature pipeline, request to closure, with CP gates and change requests. Use for any M/L feature.` | Meaning, closed list. The fix kept one of Base's two "also handles" items and dropped the other, with 19 chars spare. `## Abandon` still exists at `SKILL.md:169`, but this listing is what names the skill, and `routing.md` never names abandoning a feature; its nearest row is "Change to an open feature". | `description: "M/L feature pipeline, request to closure, with CP gates, change requests and abandonment. Use for any M/L feature."` |
| R2 | `.claude/skills/backend-build-vs-buy/SKILL.md:3` (T2) | "Per-component build-vs-buy for backend ... managed (UGS, PlayFab, Nakama, Firebase) vs custom, with exit cost. Use when choosing backend services." | `Backend build-vs-buy: matchmaking, cloud save, hosting, leaderboards; UGS, PlayFab, Nakama, Firebase. Use to pick one.` | Added claim, orphan word. "One" follows the vendor list, so it says the outcome is one vendor. Base never says that: its first word is "Per-component", and the body splits by component (step 1, `SKILL.md:17`) and decides per row (`SKILL.md:37`). | `description: "Backend build-vs-buy: matchmaking, cloud save, hosting, leaderboards; UGS, PlayFab, Nakama, Firebase. Use when choosing."` |
| R3 | `.claude/skills/consent-att-init-order/references/google-ump.md:20` (T3.4) | None: the fence comment "Client startup" named no location. | `...or `Assets/_Project/Scripts/Platform/StartupConsentFlow.cs` when the project has none; the file holds class members only, and `_firebaseBootstrap`, ... are project code.` | Orphan reference, in a hardest-read site. The fix replaced the text up to the first `;` and left this tail. "The file" now follows the fallback path, so it reads as a target file holding only members. That is what T3.4 ruled cannot exist alone and what the brief forbids ("never a new file that holds only members"). | ``  - **Adapt into:** the one bootstrap class that owns SKILL.md step 3's sequence, or `Assets/_Project/Scripts/Platform/StartupConsentFlow.cs` when the project has none; the sample holds class members only, and `_firebaseBootstrap`, `_lifetimeToken`, `RequestAttThen`, `ApplyFirebaseConsent`, `ApplyAdConsentSignals`, `InitializeAds` and `OnStartupFailed` are project code.`` |
| R4 | `.claude/skills/osa-optimized-scrollview-adapter/references/pooling-and-performance.md:25` (T3.5) | None: the fence named no location. | `...or `Assets/_Project/Scripts/<Feature>/Views/<Name>Adapter.cs` when none exists; the file holds class members only, and `_PreMadeViews` and `MyItemViewsHolder` are project code; the file keeps a 4-line header marking it unverified.` | Same defect, twice in one line. `:24` says "not a standalone file", which softens the first "the file" only. The second tells the adapter to keep a header that says "no Unity project in this repo", which is false in a game project. | ``  - **Adapt into:** the project's OSA adapter class (derives `OSA<TParams, TItemViewsHolder>`), or `Assets/_Project/Scripts/<Feature>/Views/<Name>Adapter.cs` when none exists; the sample holds class members only, and `_PreMadeViews` and `MyItemViewsHolder` are project code; the sample keeps a 4-line header marking it unverified.`` |
| R5 | `.claude/skills/flexalon-layouts/references/custom-layouts.md:20` (T3.5) | None: the fence named no location. | ``  - **Adapt into:** `Assets/_Project/Scripts/<Feature>/Views/HelixStackLayout.cs`; the file keeps a 3-line header marking it unverified.`` | Same orphan. The only file named on the line is the adapt target, so the adapted code is told to keep the "Unverified" header. | ``  - **Adapt into:** `Assets/_Project/Scripts/<Feature>/Views/HelixStackLayout.cs`; the sample keeps a 3-line header marking it unverified.`` |
| R6 | `.claude/skills/litmotion-tweening/references/litmotion-animation-component.md:27` (T3.5) | None: the fence named no location. | ``  - **Adapt into:** `Assets/_Project/Scripts/<Feature>/Views/CustomAnimationComponents.cs`; fill the `Play()` placeholder first; the file keeps a 3-line header marking it unverified.`` | Same orphan as R5. | ``  - **Adapt into:** `Assets/_Project/Scripts/<Feature>/Views/CustomAnimationComponents.cs`; fill the `Play()` placeholder first; the sample keeps a 3-line header marking it unverified.`` |

## Coverage
A finding in a report can hold several text edits. "Exact text" is a script assertion against the tree; "removed text" asserts that text the report replaced or deleted is gone. Result: 98 of 98 present, 21 of 21 absent. Each site was then read in place against `git show <Base>:<path>`.

| Batch | Report findings | Sites checked | Exact text | Removed text | Failing |
|---|---|---|---|---|---|
| T2 | 16 | 16 | 16 | 0 | R1, R2 |
| T3.1 | 2 | 2 | 4 | 1 | none |
| T3.2 | 10 | 10 | 10 | 2 | none |
| T3.3 | 5 | 5 | 9 | 1 | none |
| T3.4 | 10 | 10 | 14 | 2 | R3 |
| T3.5 | 11 | 11 | 16 | 5 | R4, R5, R6 |
| T3.6 | 9 | 9 | 10 | 3 | none |
| T3.7 | 11 | 11 | 11 | 3 | none |
| T4.1 | 5 | 5 | 5 | 2 | none |
| T4.2 | 2 | 2 | 2 | 2 | none |
| **Total** | **81** | **81** | **97** | **21** | **6** |

Beyond the 81, all passing:
- **`stateless-state-machines:20`:** `Bug shape`, the T4.1 text (feature log row 13b). Exact text is the 98th assertion.
- **T3.7 cosmetic note:** the `unity-job-system-and-burst` trailing space is gone.
- **`verify-layer/SKILL.md`:** every row and steps 2-4 walked against `verify.ps1`.
- **Template `No envelope` line:** `framework-docs/skill-template.md:81` equals the T4.2 report's text, under `Envelope fields`. All three `Status:` fences it covers belong to skills whose report goes to the GD.

## The checks the brief named
- **Adapt targets vs `naming-convention.md`:**
  - **`Views/`:** `HelixStackLayout`, `<Name>Adapter` (the folder holds `LayoutBase` and `OSA<,>`, both MonoBehaviours) and `CustomAnimationComponents` (a UI-bound `Slider` component) all pass.
  - **`Platform/StartupConsentFlow.cs`:** a feature-root file for a `UnityEngine` class; passes.
  - **`<Feature>/Server/<SdkWrapper>.cs`:** matches the `dotnet-concurrency-and-async` step 1 wording; passes.
- **Added steps:** `unity-lighting` 13, `unitask-async-programming` 10, `unity-camera-fundamentals` 16, `spine-animation` 16 and `unity-post-processing` 10 each state only their Base `Output` field. Each is last in its list. "Target tier" is `unity-post-processing` step 2's own term.
- **`iap-server-receipt-ledger` step 3:** "grant from that verified response" is in the folder at `app-store-server-api.md:19`.
- **`iap-server-receipt-ledger` step 8:**
  - **"Report it in `Limitations`":** Base's `Output` held this limit under `Known limitations`, and its UGS reference pointed there; `Limitations` is the envelope's name for that field.
  - **"Scheduled":** restored, so step 6's citation resolves.
  - **"Per the backend reference":** the Reversal rows are in both backend references.
- **`consent-att-init-order` step 3(d):** the subject is restored and the skip stays limited to `SetConsent` + collection. The target's defect is R3 only.
- **`firebase-unity-sdk` step 6, `secret-and-supply-chain-scan` step 3, `crash-anr-reporting-gate` step 8, `git-commit` step 5:** same meaning as Base; pass.

## Judged, not findings
- **`feature/SKILL.md:117` "in this order":** it also sits above the `Failure` and `Earlier merge` bullets, which are conditions, not steps. Nobody would run them as steps.
- **`technology-scouting-sweep` description drops "technique":** "every research-mode question" keeps the scope, `researcher.md:27` names the skill, and the body keeps "technique" at `SKILL.md:57`.
- **`ad-mediation-monetization-platform` 9, `analytics-telemetry-platform` 8 "re-opens this decision":** the brief's prescribed form. It reads Base's "trigger" as a re-decision trigger, the wording Base's sibling skills use.
- **`core-tests-without-unity` "gitignored here":** not in Base, but true at `.gitignore:47`, and the brief requires the stored form to be stated.

## Out of scope
Neither line is a fixed site or a comparator's text; owner is the main session.
- **`iap-server-receipt-ledger/SKILL.md:69`:** still says "a `Known limitations` line", now that `Output` has no such field, while `:64` says `Limitations`. Base's wording.
- **`csharp-standards/references/code-style-and-layout.md:10`:** the same "the file keeps a 3-line header" wording as R5. Author text; T4.1 fix 5 replaced only `:8`-`:9`.

## Not verified
- **Routing:** R1, R2 and the other T2 lines are judged by reading the listing text; no prompt was run against a real listing.
- **Moved code:** adapt files remain uncompiled (no Unity project here).
- **Replacements:** not applied, so R1 to R6 have not been through `verify.ps1`. Whole-layer `verify.ps1` on the current tree: exit 0, 21 warnings.
