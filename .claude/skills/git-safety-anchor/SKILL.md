---
name: git-safety-anchor
description: "Blast radius, backup/<op>-<utc> tag, stash create, undo. Use before reset, rebase, force-push, filter-repo, clean."
user-invocable: false
---

# Git Safety Anchor

- **Not for:** recovering state already lost (`git-recovery`), tracing a change to its commit (`git-forensics`), Unity asset and LFS specifics (`git-unity-repo`).
- **Not for:** deciding a published-history rewrite (`cto` plans it; the GD authorises the run).
- **Docs:** https://git-scm.com/docs/git-<subcommand> — unversioned (always current release); confirm a flag with `git <subcommand> -h` on the machine that runs the operation.
- **Help:** `--help` opens a browser on Git for Windows.
- **Defaults:** `gc.reflogExpire`, `gc.pruneExpire`, `core.logAllRefUpdates` are per-repo config: read the effective value.

## References
- **[anchor-and-undo-recipes.md](references/anchor-and-undo-recipes.md):** deriving the `Undo:` line for a specific operation, or restoring from a `stash create` sha.
- **[what-cannot-be-anchored.md](references/what-cannot-be-anchored.md):** before claiming an anchor is complete, or the operation touches untracked/ignored files, submodules, LFS, a remote, or gc/expired reflog.

## Steps
1. **Classify blast radius before running anything:**
   - **Radius 1:** touches nothing, no anchor.
   - **Radius 2:** index, working tree or local refs, deleting a branch, tag or stash entry included, restorable from the anchor below.
   - **Radius 3:** remote refs, anything that deletes objects or untracked files.
   - **Radius 3 deleting commands:** `gc`, `prune`, `clean -f`, `reset --hard`, `checkout/switch -f`, `switch --discard-changes`, `read-tree -u --reset`.
   - **Radius 3 also deleting:** `lfs prune`, `worktree remove --force`, `submodule deinit`.
   - **Radius 3, reflogs and rewrites:** expiring reflogs a recovery searches (`reflog expire/delete/drop`), or a rewrite of every ref (`filter-repo`, `lfs migrate import` without `--no-rewrite`).
   - **Radius 2 beyond `git-expert`'s `Blast radius` list:** `rm`, `mv`, `apply`, `am`, `branch -f/-m/-M`, `remote add/set-url`, `config` writes, `submodule update`.
   - **Radius 2 also:** `lfs lock` and an own `lfs unlock`, `reset --merge`, `reflog write`, `lfs migrate import --no-rewrite`.
   - **Radius 3 also:** `--force` on another's lock (`lfs unlock`), `lfs push`, `maintenance run` (its default task is `gc`), `lfs fetch --prune`.
   - **Not listed:** classify by these definitions and name the row chosen. A command spanning two rows takes the higher.
2. **Radius 3 needs explicit authorization for that exact operation in the current conversation:** never inferred from an earlier approval or a general "tidy the branch".
   - **Why:** an anchor cannot restore a ref another clone already fetched.
   - **Dispatched:** only the GD's words for that operation quoted verbatim in the brief count.
   - **Hook-blocked forms:** `reset --hard`, `clean -f`, force/delete/mirror/prune/`--tags` push are never run, authorised or not; the exact command goes under `Needs GD` and the GD runs it.
3. **Tag every ref the operation can move, not just `HEAD`:** one lightweight `backup/<op>-<utc>` tag per affected ref (`git for-each-ref` to find them); a `filter-repo` moves all refs.
   - **`<utc>`:** `YYYYMMDDTHHMMSSZ` (a ref name cannot hold `:`).
   - **No tag needed:** a `commit`, `stash`, `tag -d` or `branch -D`; the `git rev-parse` sha from step 5 is its anchor.
   - **Remote ref:** anchored at its live value from `git ls-remote <remote> <ref>` (it prompts: transport commands are never auto-allowed), never a remote-tracking ref that may be stale.
   - **Fetch/pull:** read `git config --get fetch.pruneTags` and `remote.<r>.pruneTags` first; true deletes every local tag the remote lacks, `backup/*` anchors included, so add `--no-prune-tags`.
   - **Cleanup:** delete a `backup/*` tag once the requester confirms the result (`git tag -d`); list every one still standing in the return.
4. **Anchor uncommitted work with `git stash create`, never `git stash push`:** `create` returns a sha and leaves index and working tree untouched; `push` mutates the state being protected.
   - **Timing:** run it last before the operation, since it snapshots only that instant.
5. **Record the pre-state as shas:** `git rev-parse` for each affected ref and `git status --porcelain` (the only status form with a stability guarantee; never parse long or `--short` output).
6. **Derive the literal undo before the operation runs:** the exact command with its sha ([anchor-and-undo-recipes.md](references/anchor-and-undo-recipes.md)).
   - **No reflog advice:** never write "use the reflog"; if no reversal exists, say so and why.
7. **State what the anchor does not cover:** per [what-cannot-be-anchored.md](references/what-cannot-be-anchored.md); untracked/ignored files above all (`git clean -xdf` has only a preview: `git clean -xdn`).
   - **Unanchorable:** an operation whose purpose is deleting untracked/ignored files (`git clean -xdf`) is radius 3.
   - **Blocked:** `Decision: blocked` until the requester lists what may be deleted; `clean -f` itself is GD-run.
8. **Verify the anchor resolves:** `git rev-parse --verify <backup-ref>` and `git cat-file -e <stash-sha>`; report what they returned.
   - **Unconfirmed:** an unconfirmed anchor is never reported as one.
   - **Scripts:** build scripted checks on plumbing output.
9. **`Decision: blocked`:** when the radius cannot be determined or the anchor cannot be made; a stop, not a judgement call on the requester's behalf.

## Never
- **Reflog coverage claim:** claiming reflog coverage for uncommitted work, a fresh clone, or anything after `gc --prune` / `reflog expire`.
- **Published anchor:** publishing an anchor; `backup/*` tags stay local (`push --tags` and `--mirror` are blocked for this reason).

## Output
```
## Safety Anchor — <operation>
- Blast radius: 1 | 2 | 3 — <why>
- Operation: <exact command about to run>
- Anchor refs: <backup/... names and shas, or "none — radius 1">
- Uncommitted work: <stash create sha and restore command, or "working tree clean">
- Undo: <literal reversing command>
- Not covered: <what this anchor cannot restore>
- Decision: proceed | blocked
- Routed to: <git-expert / cto / gd / none>
```

## Example
- **"Squash and force-push develop, the anchor is overkill for a branch only I use":** declined — `develop` has an upstream.
  - **Why:** other clones' reflogs are out of reach and radius 3 applies whoever uses it.
  - **Done instead:** `Decision: blocked`, `Routed to: gd`, command quoted, cost stated; nothing run.
