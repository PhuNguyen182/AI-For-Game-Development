---
name: resolve-merge-conflicts
description: "Merge, rebase, cherry-pick, stash conflicts in C#, Unity YAML, Addressables. Use when a conflict is in progress."
argument-hint: "[optional notes on which feature areas to prioritize]"
allowed-tools: Read, Grep, Glob, Edit
---

# Resolve a git conflict across code and Unity assets

- **Input:** `$ARGUMENTS`: optional priority areas; else resolve everything conflicted.
- **Precondition:** requires unmerged paths (`git diff --name-only --diff-filter=U` non-empty); none → stop and say so.
- **Report, dispatched agent:** the `agent-protocol` envelope.
- **Report, main session:** to the GD in Vietnamese.

## Steps
1. **Context:**
   - **Operation:** name it from `git rev-parse --git-dir`:
     - **`MERGE_HEAD`:** merge.
     - **`rebase-merge/`, or `rebase-apply/` without `rebase-apply/applying`:** rebase.
     - **`rebase-apply/` with `rebase-apply/applying`:** `git am`, same stage meaning as cherry-pick.
     - **`CHERRY_PICK_HEAD`:** cherry-pick.
     - **`REVERT_HEAD`:** revert.
     - **None of these:** stash apply/pop.
   - **Stages:** stage `:2:` is `HEAD` and `:3:` the incoming change.
   - **Stages in a rebase:** `HEAD` is the upstream being rebased onto plus the commits already replayed, and `:3:` is the branch's own commit being replayed.
   - **Side names:** name sides by these stage meanings, never by "ours/theirs".
   - **Three versions:** per conflicted path read all three versions (`git show :1:<path>` base, `:2:`, `:3:`) before touching markers: markers do not show intent.
2. **Classify each file:** C#, Unity YAML, Addressables, `.meta`, text/docs, or binary (no textual diff).
   - **Unity YAML files:** detect by `%YAML` header, not `.meta`.
   - **Addressables files:** `AddressableAssetSettings*.asset`, groups under `Assets/AddressableAssetsData`.
3. **Classify scope:** per hunk against the base.
   - **Big:** either side does something the other lacks (new method, member, event hookup, Core rule, prefab child/component, SO field, Addressables entry) → **big**.
   - **Small:** pure style with identical behaviour → **small**.
   - **Equivalence:** never assume equivalence without reading both diffs against the base.
4. **Big: feature-preserving:** combine so every feature-bearing addition from either side survives.
   - **Collision:** only a same-line/field collision with incompatible changes becomes a small-scope decision (step 5).
   - **Rest of the file:** the rest of the file still merges additively.
   - **Contradiction:** a true contradiction of intent → flag for `technical-architect`, never guess a winner.
5. **Small: standards:** pick the side that already matches `csharp-standards` (`references/coding-principles.md`, `references/code-style-and-layout.md`), cite the clause, fix the losing side up.
   - **Neither compliant:** write the compliant form.
6. **Unity YAML:**
   - **Wired driver:** a wired `merge=unityyamlmerge` driver already ran during the operation; a conflict left on the file means it failed.
   - **Driver output:** the working file then holds the driver's output, not markers — on every clashing field the left (theirs) value, so it looks resolved and passes step 10.
   - **Driver output, staging:** never stage that output: `git checkout -m <path>` restores the markers, then continue from the stages below.
   - **Otherwise:** otherwise run UnityYAMLMerge once on the three stages, written outside the working tree.
   - **Tool path and argument order:** `git-unity-repo` → `references/scene-and-prefab-conflicts.md`.
   - **Stage files:** write each stage byte-exact from Bash, `git cat-file blob :<n>:<path> > <file>`: PowerShell redirection re-encodes and rewrites line endings.
   - **Command:** run UnityYAMLMerge as `timeout 120 '<tool>' merge -h -p --fallback none <base> <stage-3> <stage-2> <out>` (Bash).
   - **Required flags:** without `-h` and `--fallback none` an unresolved conflict opens a dialog or GUI tool and the run hangs.
   - **Exit 0:** copy the tool's output over the path.
   - **Timeout or non-zero:** the tool failed and its output is discarded (exit 2 writes theirs on each clash with no markers).
   - **Clash list:** add `-o <clash-file> --describe` to list what clashed.
   - **Mergetool:** never `git mergetool`: it prompts, and its backups become `*.orig` assets.
   - **Still conflicted or tool absent:** merge by hand at GameObject/component/field level (steps 3–5), never across a `--- !u!` document boundary.
   - **Hand merge outcome:** every component and serialized field either side added survives; only a same-field value clash is the small conflict.
   - **`fileID`:** never invent a `fileID`; reuse the one a side assigned.
   - **Editor redo:** whatever must be redone in the Editor is listed for `gameplay-engineer`.
7. **`.meta`:** never hand-edit or regenerate a GUID.
   - **GUID to keep:** keep the GUID the resolved content and the repo's other references point to (`grep -rl "<guid>" Assets Packages ProjectSettings` first).
   - **Real clash:** both sides created different assets at one path with different GUIDs → real clash: keep both under distinct paths and rewire (step 9).
8. **Addressables:** merge entry by entry; every entry either side added keeps address, labels and group.
   - **Duplicates:** a duplicate address or schema mismatch is fixed now.
9. **Reference-wiring pass:** for every touched prefab/scene/SO, grep each `fileID`/`guid` it references and confirm the target exists post-merge.
   - **Both sides:** check both sides' pre-merge references (a component one side added referencing an object the other added is the likeliest miss).
10. **Verify the resolution:**
    - **Markers:** on the resolved paths, `grep -nE '^(<{7}|>{7}|\|{7})( |[[:space:]]*$)|^={7}[[:space:]]*$'` prints nothing.
    - **Pattern coverage:** diff3 `|||||||` included; `[[:space:]]` absorbs a CRLF checkout's `\r`; a longer `===` run in Markdown is not a marker.
    - **Risk lens:** apply the `/review-code-risks` lens to resolved `.cs`.
    - **Editor timing:** Editor checks come after every working-tree write, with the Editor closed during those writes (`git-unity-repo` step 10).
    - **C# Editor check:** compile-check C# (Unity ladder in `core.md` Tools, or `dotnet build`).
    - **Asset Editor check:** for touched assets, open the project and read the Console for missing-script/reference errors.
    - **No Editor reachable:** `Not verified`, `Next:` the owning engineer.
11. **Stage and report:**
    - **Staging:** `git add` only resolved files.
    - **Per-file report:** features combined, which side's style won and why (clause), references rewired, what verification ran.
    - **Approval:** before `git commit` or the operation's `--continue`, once per operation: dispatched agent → `Status: Needs-decision`; main session → `AskUserQuestion`.
    - **Approved `--continue`:** an approved `--continue` carries through later stops that need no big-scope decision.
12. **Multi-stop operations:** a rebase or a multi-commit cherry-pick stops once per conflicting commit: repeat steps 1–11 at each stop (stages change per commit), then `--continue`.
    - **Same conflict replayed at several stops:** pass `-c rerere.enabled=true` on the starting command and on every `--continue` (it records at the conflict and at the commit).
    - **Reused resolution:** still re-verify each reused resolution.
    - **Editor checks:** run once, after the last stop; never open the Editor between stops, since each `--continue` rewrites the tree.
    - **Stash entry:** a stash apply/pop conflict keeps the stash entry: drop it only after the result is confirmed (`git-safety-anchor` stash row).

## Never
- **Discarded feature:** discard either side's feature to make the merge look clean.
- **Whole-file side:** `git checkout --ours/--theirs` on a whole file before confirming the discarded side carries nothing the kept one lacks.
- **Automatic commit:** commit or push automatically.
- **Unrun verification:** claim wiring or compile verification that did not run.
