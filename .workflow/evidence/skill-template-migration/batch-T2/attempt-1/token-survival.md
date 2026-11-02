# Token survival explanations (T2 attempt 1)

Run: token-survival.ps1 -Base bdf5c9ec -Skills <all 124>. Initial result: 87 missing, all from SKILL.md line 3 (description). The script tokenises slash/dot compounds as one token, so 74 of 87 are compounds whose every part survives in the new description or elsewhere in the skill folder (checked per part, exact case).

## Genuinely lost symbols, moved to body
- ad-mediation-monetization-platform: AppLovin -> added to Step 3 (mediation judging line).
- netcode-architecture-decision: LiteNetLib -> added to Step 3 Custom bullet.
- netcode-for-entities: DOTS -> added to Docs line (Needs ECS (DOTS)).
- unity-animation: AnimatorController -> added to Docs line (Mecanim).

## Lost, not moved: generic words, not distinctive symbols
- build-fault-triage: logs (from logs/logcat; logcat kept).
- decide: netcode, backend (from netcode/backend; plain words, ADR/netcode routing words live in the cto flow).
- release: analytics (from analytics/IAP; IAP kept).
- source-generator-authoring: hashing (from equality/hashing; equality kept).
- unity-2d-physics, unity-3d-physics: GameObjects (plain noun; Rigidbody2D/Rigidbody keep the scope).
- zstring-zero-allocation-strings: TextMeshPro (abbreviation TMP kept in the description).
- netcode-for-entities: ICommandData/IInputComponentData compound; ICommandData kept, IInputComponentData survives in references.

## All other entries
Slash/dot compounds split into parts that all still exist in the skill folder (description or body/references), e.g. MathF/Math, DOMove/DOFade, SetEase/SetLoops/SetUpdate, LoadAssetAsync/InstantiateAsync/LoadSceneAsync, NavMeshSurface/Modifier, Parallel.ForEach, UnityEngine.UIElements, BuildPipeline.BuildPlayer/BuildReport. No further action.

- ui-toolkit: UnityEngine.UIElements compound was lost whole; added to the Docs line.

