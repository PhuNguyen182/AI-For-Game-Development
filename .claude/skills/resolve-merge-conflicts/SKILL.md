---
name: resolve-merge-conflicts
description: "Resolve an in-progress git merge across C#, prefabs, scenes, ScriptableObjects, Addressables and text: keep every feature from both sides on a major conflict, pick the standards-compliant side on a cosmetic one, rewire references."
argument-hint: "[optional notes on which feature areas to prioritize]"
allowed-tools: Bash, PowerShell, Read, Grep, Glob, Edit
---

# Resolve a git merge conflict across code and Unity assets

`$ARGUMENTS`: optional priority areas; else resolve everything conflicted. Requires `.git/MERGE_HEAD`; absent → stop and say so. Final report to the GD in Vietnamese.

1. **Context** — `HEAD` (ours), `MERGE_HEAD` (theirs), merge-base; `git diff --name-only --diff-filter=U`. Per conflicted path read all three versions (`git show :1:<path>` base, `:2:` ours, `:3:` theirs) before touching markers: markers do not show intent.
2. **Classify each file** — C#; Unity YAML (detect by `%YAML` header, not `.meta`); Addressables (`AddressableAssetSettings*.asset`, groups under `Assets/AddressableAssetsData`); `.meta`; text/docs; binary (no textual diff).
3. **Classify scope** per hunk against the base. Either side does something the other lacks (new method, member, event hookup, `Game.Core.*` rule, prefab child/component, SO field, Addressables entry) → **big**. Pure style with identical behaviour → **small**. Never assume equivalence without reading both diffs against the base.
4. **Big: feature-preserving** — combine so every feature-bearing addition from either side survives. Only a same-line/field collision with incompatible changes becomes a small-scope decision (step 5); the rest of the file still merges additively. A true contradiction of intent → flag for `technical-architect`, never guess a winner.
5. **Small: standards** — pick the side that already matches `csharp-standards` (`references/coding-principles.md`, `references/code-style-and-layout.md`), cite the clause, fix the losing side up. Neither compliant → write the compliant form.
6. **Unity YAML** — `git config merge.unityyamlmerge.driver` and `.gitattributes` `merge=unityyamlmerge` present → `git mergetool` on that file. Driver absent or `git mergetool` fails → hand-merge at GameObject/component/field level (steps 3–5): every component and serialized field either branch added survives; only a same-field value clash is the small conflict. Never invent a `fileID`; reuse the one a branch assigned.
7. **`.meta`** — never hand-edit or regenerate a GUID. Keep the GUID the resolved content and the repo's other references point to (`grep -r "<guid>"` first). Both branches created different assets at one path with different GUIDs → real clash: keep both under distinct paths and rewire (step 9).
8. **Addressables** — merge entry by entry; every entry either side added keeps address, labels and group. A duplicate address or schema mismatch is fixed now.
9. **Reference-wiring pass** — for every touched prefab/scene/SO, grep each `fileID`/`guid` it references and confirm the target exists post-merge, checking both sides' pre-merge references (a component one side added referencing an object the other added is the likeliest miss).
10. **Verify** — `grep -rn "^<<<<<<<\|^=======\|^>>>>>>>"` on resolved paths returns nothing. Compile-check C# (Unity ladder in `core.md` Tools, or `dotnet build`). For touched assets, open the project and read the Console for missing-script/reference errors. Apply the `/review-code-risks` lens to resolved `.cs`.
11. **Stage and report** — `git add` only resolved files. Report per file: features combined, which side's style won and why (clause), references rewired, what verification ran. Ask before `git commit` / `git merge --continue`.

## Never
- Discard either branch's feature to make the merge look clean.
- `git checkout --ours/--theirs` on a whole file before confirming neither side carries something the other lacks.
- Commit or push automatically.
- Claim wiring or compile verification that did not run.
