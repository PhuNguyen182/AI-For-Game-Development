---
name: git-safety-anchor
description: "Before a state-changing git command: classify blast radius, tag backup/<op>-<utc>, git stash create, derive the literal undo; lists what reflog cannot recover. Use before reset, rebase, merge, checkout, force-push, filter-repo, clean, branch -D."
user-invocable: false
---

# Git Safety Anchor

Not for: recovering state already lost (`git-recovery`), tracing a change to its commit (`git-forensics`), Unity asset and LFS specifics (`git-unity-repo`), deciding a published-history rewrite (`cto` plans it; the GD authorises the run).
Docs: https://git-scm.com/docs/git-<subcommand> — unversioned (always current release); confirm a flag with `git <subcommand> -h` on the machine that runs the operation (`--help` opens a browser on Git for Windows). Defaults (`gc.reflogExpire`, `gc.pruneExpire`, `core.logAllRefUpdates`) are per-repo config: read the effective value.

| Reference | Read when |
|---|---|
| [anchor-and-undo-recipes.md](references/anchor-and-undo-recipes.md) | Deriving the `Undo:` line for a specific operation, or restoring from a `stash create` sha |
| [what-cannot-be-anchored.md](references/what-cannot-be-anchored.md) | Before claiming an anchor is complete, or the operation touches untracked/ignored files, submodules, LFS, a remote, or gc/expired reflog |

## Steps
1. **Classify blast radius before running anything** — 1: touches nothing, no anchor; 2: index, working tree or local refs, deleting a branch, tag or stash entry included, restorable from the anchor below; 3: remote refs, anything that deletes objects or untracked files (`gc`, `prune`, `clean -f`, `reset --hard`, `checkout/switch -f`, `switch --discard-changes`, `read-tree -u --reset`, `lfs prune`, `worktree remove --force`, `submodule deinit`), expiring reflogs a recovery searches (`reflog expire/delete/drop`), or a rewrite of every ref (`filter-repo`, `lfs migrate import` without `--no-rewrite`). Radius 2 beyond the agent's table: `rm`, `mv`, `apply`, `am`, `branch -f/-m/-M`, `remote add/set-url`, `config` writes, `submodule update`, `lfs lock` and an own `lfs unlock` (`--force` on another's lock is 3, as is `lfs push`), `reset --merge`, `reflog write`, `lfs migrate import --no-rewrite`. Radius 3 also: `maintenance run` (its default task is `gc`), `lfs fetch --prune`. Not listed → classify by these definitions and name the row chosen. A command spanning two rows takes the higher.
2. **Radius 3 needs explicit authorization for that exact operation in the current conversation** — never inferred from an earlier approval or a general "tidy the branch"; an anchor cannot restore a ref another clone already fetched. Dispatched, only the GD's words for that operation quoted verbatim in the brief count. A form the hooks block (`reset --hard`, `clean -f`, force/delete/mirror/prune/`--tags` push) is never run, authorised or not: its exact command goes under `Needs GD` and the GD runs it.
3. **Tag every ref the operation can move, not just `HEAD`** — one lightweight `backup/<op>-<utc>` tag per affected ref (`git for-each-ref` to find them); a `filter-repo` moves all refs. `<utc>` is `YYYYMMDDTHHMMSSZ` (a ref name cannot hold `:`). A `commit`, `stash`, `tag -d` or `branch -D` needs no tag: the `git rev-parse` sha from step 5 is its anchor. A remote ref is anchored at its live value from `git ls-remote <remote> <ref>` (it prompts: transport commands are never auto-allowed), never a remote-tracking ref that may be stale. Before a `fetch`/`pull`, read `git config --get fetch.pruneTags` and `remote.<r>.pruneTags`: true deletes every local tag the remote lacks, `backup/*` anchors included — add `--no-prune-tags`. Delete a `backup/*` tag once the requester confirms the result (`git tag -d`); list every one still standing in the return.
4. **Anchor uncommitted work with `git stash create`, never `git stash push`** — `create` returns a sha and leaves index and working tree untouched; `push` mutates the state being protected. Run it last before the operation, since it snapshots only that instant.
5. **Record the pre-state as shas** — `git rev-parse` for each affected ref and `git status --porcelain` (the only status form with a stability guarantee; never parse long or `--short` output).
6. **Derive the literal undo before the operation runs** — the exact command with its sha ([anchor-and-undo-recipes.md](references/anchor-and-undo-recipes.md)). Never write "use the reflog"; if no reversal exists, say so and why.
7. **State what the anchor does not cover** per [what-cannot-be-anchored.md](references/what-cannot-be-anchored.md) — untracked/ignored files above all (`git clean -xdf` has only a preview: `git clean -xdn`). An operation whose purpose is deleting untracked/ignored files (`git clean -xdf`) is unanchorable: radius 3, `Decision: blocked` until the requester lists what may be deleted; `clean -f` itself is GD-run.
8. **Verify the anchor resolves** — `git rev-parse --verify <backup-ref>` and `git cat-file -e <stash-sha>`; report what they returned. An unconfirmed anchor is never reported as one. Build scripted checks on plumbing output.
9. **`Decision: blocked`** when the radius cannot be determined or the anchor cannot be made — a stop, not a judgement call on the requester's behalf.

## Never
- Claim reflog coverage for uncommitted work, a fresh clone, or anything after `gc --prune` / `reflog expire`.
- Publish an anchor: `backup/*` tags stay local (`push --tags` and `--mirror` are blocked for this reason).

## Output
```
## Safety Anchor — <operation>
- Blast radius: 1 | 2 | 3 — <why>
- Operation: <exact command about to run>
- Anchor refs: <backup/... names and shas, or "none — radius 1">
- Uncommitted work: <stash create sha and restore command, or "working tree clean">
- Undo: <literal reversing command>
- Not covered: <what this anchor cannot restore>
- Verified: <what rev-parse / cat-file -e returned>
- Decision: proceed | blocked
- Routed to: <git-expert / cto / gd / none>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Squash and force-push develop, the anchor is overkill for a branch only I use" → declined: `develop` has an upstream, so other clones' reflogs are out of reach and radius 3 applies whoever uses it. `Decision: blocked`, `Routed to: gd`, command quoted, cost stated; nothing run.
