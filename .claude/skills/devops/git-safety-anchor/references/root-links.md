# Root Links — Git Reference Manual and Pro Git

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Git publishes **no versioned documentation URLs** — `git-scm.com/docs/git-<subcommand>`
always serves the current release, and there is no `@<version>` segment to pin,
so this folder states that fact rather than inventing a pin. What replaces the
pin is the plumbing-vs-porcelain distinction tabulated below: because this
skill's anchors are verified by parsing command output, it matters which
outputs git promises to keep stable across versions and which it explicitly
does not.

## Contents

- [Documentation roots](#documentation-roots)
- [No version pin — what to check instead](#no-version-pin--what-to-check-instead)
- [Plumbing vs porcelain — output stability](#plumbing-vs-porcelain--output-stability)
- [Topic → file map](#topic--file-map)
- [Disclosed gaps](#disclosed-gaps)

## Documentation roots

| Root | Holds | Source |
|---|---|---|
| Git reference manual | The per-command pages every flag, mode, and default in this folder is cited from — `git-reset`, `git-stash`, `git-reflog`, `git-update-ref`, `git-fsck`, `git-gc`, `git-config` | [Git reference manual](https://git-scm.com/docs) |
| Pro Git, 2nd edition | The conceptual material no man page states — the object model, plumbing vs porcelain, submodule gitlinks, data recovery | [Pro Git](https://git-scm.com/book/en/v2) |

## No version pin — what to check instead

| Fact | Consequence for this skill | Source |
|---|---|---|
| Documentation URLs carry no version segment | Every link here resolves to whatever release git-scm.com currently publishes; a flag documented today may not exist on an older installed git | [Git reference manual](https://git-scm.com/docs) |
| The installed git is the real authority | Confirm a flag against `git <subcommand> --help` on the machine the operation will run on, not against the page alone, before the anchor depends on it | [Git reference manual](https://git-scm.com/docs) |
| Defaults are configuration, not constants | Every documented default (`gc.reflogExpire`, `gc.pruneExpire`, `core.logAllRefUpdates`) is overridable per repository, so read the effective value rather than assuming the documented one | [git-config](https://git-scm.com/docs/git-config) |

## Plumbing vs porcelain — output stability

Pro Git's own split: porcelain commands are the user-facing ones, plumbing
commands "do low-level work and were designed to be chained together
UNIX-style or called from scripts".

| Surface | Stability git promises | Consequence for verification | Source |
|---|---|---|---|
| Plumbing — `rev-parse`, `cat-file`, `update-ref`, `for-each-ref`, `hash-object` | Designed as "building blocks for new tools and custom scripts"; output shape is the command's contract | Safe to parse; these are the commands an anchor's verification should be built on | [Pro Git — Plumbing and Porcelain](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) |
| `git status --porcelain` (v1) | "guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration" | The one `status` form a pre-state snapshot may be parsed from | [git-status — porcelain format v1](https://git-scm.com/docs/git-status#_porcelain_format_version_1) |
| `git status` default long format | Explicitly none — "Its contents and format are subject to change at any time" | Never parse it, and never quote it as the recorded pre-state | [git-status — output](https://git-scm.com/docs/git-status#_output) |
| `git status --short` | No stability guarantee is stated; the guarantee is reserved for `--porcelain` | Human-readable only; use `--porcelain` when the output feeds a comparison | [git-status — short format](https://git-scm.com/docs/git-status#_short_format) |
| Porcelain commands generally — `git branch`, `git stash list`, `git log` without a format | Human-facing; shaped by user configuration (aliases, `color.*`, `log.date`) | Their output is evidence for a reader, never the value an undo command consumes | [Pro Git — Plumbing and Porcelain](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) |

**Critical caveat**: the word *porcelain* means opposite things in the two
usages above. A *porcelain command* is the human-facing one whose output is
unstable; the `--porcelain` *flag* asks a command for the machine-readable
form that is guaranteed stable. `git status --porcelain` is therefore the
stable output of an unstable command, and `git status --short` is not a
synonym for it.

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Anchor primitives — `git tag`, `git stash create`, `git rev-parse`, `git update-ref`, `git status --porcelain`, `ORIG_HEAD` — and the literal undo command per operation | [anchor-and-undo-recipes.md](anchor-and-undo-recipes.md) | [git-stash](https://git-scm.com/docs/git-stash), [git-reset](https://git-scm.com/docs/git-reset), [git-update-ref](https://git-scm.com/docs/git-update-ref) |
| What no ref, stash, or reflog holds — untracked and ignored files, submodule working trees, unpushed LFS objects, a fresh clone, pruned objects, another clone's refs | [what-cannot-be-anchored.md](what-cannot-be-anchored.md) | [git-reflog](https://git-scm.com/docs/git-reflog), [git-gc](https://git-scm.com/docs/git-gc), [Pro Git — Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) |
| Documentation roots and output-stability rules for both files above | this file | [Git reference manual](https://git-scm.com/docs) |

## Disclosed gaps

| Area | Issue | Source |
|---|---|---|
| Git LFS | Not documented under either root — `git-scm.com` has no LFS pages. [what-cannot-be-anchored.md](what-cannot-be-anchored.md) cites the git-lfs project's own man pages instead, and that is the one citation in this folder resolving outside the two roots above | [git-lfs-push](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-push.adoc) |
| `git filter-repo` | A third-party tool, not part of git; the reference manual documents only `git-filter-branch`, whose WARNING section recommends filter-repo in its place. Rows about filter-repo are cited to the filter-repo project itself, with the filter-branch page used only for what the built-in guarantees | [git-filter-branch — SAFETY](https://git-scm.com/docs/git-filter-branch#SAFETY) |
| Remote-side reflogs | No git documentation covers them, because git has no protocol for reading one — whether a hosting platform keeps or exposes a server-side reflog is a per-host fact this folder cannot source and does not claim | synthesized |
| In-page anchors | Anchors of the form `#_<section_title>` follow git-scm.com's generated asciidoc pattern and were confirmed on `git-status`, `git-gc`, `git-reflog`, and `git-fsck`; anchors on the remaining pages follow the same pattern but were not individually opened. A stale anchor still resolves to the correct page | synthesized |
| Recovery of state already lost | Deliberately absent. `git fsck --lost-found`, dangling-object salvage, and reflog archaeology belong to `git-recovery`; this folder holds only what is knowable before the operation runs | [git-fsck](https://git-scm.com/docs/git-fsck#_options) |

Every other link in this `references/` folder is a specific page under the two
roots above, each verified to resolve before inclusion. Because none of them
is version-pinned, treat a flag or default cited here as needing confirmation
against the installed git before an anchor is reported as verified.
