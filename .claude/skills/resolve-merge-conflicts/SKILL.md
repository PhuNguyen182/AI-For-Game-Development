---
description: Resolve an in-progress git merge across C# code, prefabs, scenes, ScriptableObjects, Addressables config and text — merging every feature from both branches on a major conflict, picking the standards-compliant side on a cosmetic one, and rewiring every asset reference
argument-hint: "[optional notes on which feature areas to prioritize]"
allowed-tools: Bash, PowerShell, Read, Grep, Glob, Edit, Git
---

# Resolve a git merge conflict across code and Unity assets

`$ARGUMENTS`: optional notes on priority areas — otherwise resolve everything reported as conflicted. Requires an in-progress merge (`.git/MERGE_HEAD` present); if there isn't one, stop and say so rather than inventing conflicts to resolve. Covers C# (`.cs`), Unity serialized YAML (`.prefab`/`.unity`/`.asset`/`.controller`/`.mat`), Addressables config, `.meta` files, plain text/docs, and binary assets. Reason in English (`language-and-comments.md`); the final report to the user is in Vietnamese.

**1 — Establish context**: get `HEAD` (ours), `MERGE_HEAD` (theirs) and the merge-base; list conflicts via `git diff --name-only --diff-filter=U`. For every conflicted path, read all three versions (`git show :1:<path>` base, `:2:<path>` ours, `:3:<path>` theirs) before touching the working-tree conflict markers — the markers alone don't tell you what each side *intended*.

**2 — Classify each file**: C#; Unity serialized YAML (detect by a `%YAML` header, not `.meta`); Addressables config (`AddressableAssetSettings*.asset`, group assets under `Assets/AddressableAssetsData`); `.meta`; plain text/docs; binary (texture/model/audio/fbx — no textual diff possible). Route into the matching step below.

**3 — Classify conflict scope**: diff each side against the merge-base for that hunk. If either side's change does something the other's doesn't — a new method, member, event hookup, `Game.Core.*` rule, prefab child/component, ScriptableObject field, Addressables entry — it's a **big** conflict. If the divergence is purely stylistic (formatting, ordering, an equivalent construct) with identical behavior, it's **small**. Never assume equivalence without reading both diffs against the base.

**4 — Resolve big conflicts (mandatory, feature-preserving)**: combine both branches so every feature-bearing addition from either `ours` or `theirs` still exists after the merge — this is an H requirement, never picked around. Only when two features genuinely collide on the exact same line/field (both changed the same call in incompatible ways) does that specific span become a real small-scope decision (Step 5) — everything else in the file still merges additively. When a collision is a true contradiction in intent, not just code shape, say so and flag it for `technical-architect` rather than guessing which side "wins".

**5 — Resolve small/cosmetic conflicts**: when a span differs only in form, pick whichever side already matches `.claude/standards/client/coding-principles.md` and `.claude/standards/client/code-style-and-layout.md` (explicit access modifiers, Allman braces, `this.` qualification, modern null/pattern operators, no inline statement bodies, named temporaries over chained calls), citing the clause, and fix the losing side up rather than leaving it non-compliant. If neither side is compliant, write the compliant form fresh.

**6 — Unity serialized assets**: check `git config merge.unityyamlmerge.driver` and `.gitattributes` for a `merge=unityyamlmerge` mapping; if configured, resolve via `git mergetool` on that file instead of hand-editing YAML — Unity's driver understands `fileID`/`m_CorrespondingSourceObject` structure a text merge doesn't. If unconfigured or it fails, resolve by hand applying Steps 3–5 at the GameObject/component/field level: every component and serialized field either branch added must survive; a genuine same-field value clash is the actual small conflict. Never invent a new `fileID` — reuse whichever one a branch already assigned.

**7 — `.meta` files**: never hand-edit or regenerate a GUID. Keep whichever GUID the resolved asset content and every other reference in the repo actually point to (`grep -r "<guid>"` to confirm before choosing). If both branches created a *different* asset at the same path with a different GUID, that's a real content clash — keep both assets under distinct paths and rewire references (Step 9), never silently drop one.

**8 — Addressables/config lists**: merge entry-by-entry — every entry either branch added, with its address, labels, and group intact, must be present. A duplicate address or group-schema mismatch surfaced by the merge is fixed now, not deferred.

**9 — Reference-wiring pass (mandatory)**: for every touched prefab/scene/ScriptableObject, grep it for every `fileID`/`guid` it references and confirm the target still exists in the merged result. Cross-check against the pre-merge `ours`/`theirs` state for every reference each side had, both directions — a component one branch added referencing an object the other branch added is the case most likely to go missing.

**10 — Verify**: `grep -rn "^<<<<<<<\|^=======\|^>>>>>>>"` across resolved paths must return nothing. Compile-check the C# (Unity CLI batch-mode / `dotnet build`, per `shell-preference.md`/`unity-tooling-preference.md`). For touched Unity assets, open the project and read the Console for missing-script/missing-reference errors the merge introduced. Apply the same review lens as `/review-code-risks` to the resolved `.cs` files.

**11 — Stage and report, never auto-commit**: `git add` only the files actually resolved, never a broad add-all. Report, per file: which side's feature(s) were combined, which side's style won a cosmetic conflict and why (clause cited), every reference rewired, and what verification actually ran. Ask before `git commit`/`git merge --continue` — that's the user's call.

## Guardrails

Never resolve a conflict by discarding either branch's feature to make the merge look clean — the user's own H requirement, a gate failure per `effort-allocation.md` if dropped silently. Never hand-edit a `.meta` GUID or invent a `fileID`. Never run `git checkout --ours`/`--theirs` on a whole file without first confirming neither side carries something the other lacks. Never commit or push automatically. Never claim reference-wiring or compile verification you didn't actually run.
