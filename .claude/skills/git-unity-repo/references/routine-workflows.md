# Routine Workflows

Sources (Docs bases in SKILL.md): git-scm.com/docs/git-pull, git-revert, git-cherry-pick, git-worktree, git-clone, git-sparse-checkout, git-maintenance; [faulty] git-scm.com/docs/howto/revert-a-faulty-merge; [upm] docs.unity3d.com/Manual/upm-git.html; [lfs] github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-prune.adoc.

Each state change below is anchored first (`git-safety-anchor`) and runs with the Editor closed when it writes the tree.

## Sync with the remote
| Step | Fact that decides |
|---|---|
| `git fetch <remote>` | Updates remote-tracking refs only; never touches the tree |
| `git log --oneline HEAD..@{upstream}` / `@{upstream}..HEAD` | Incoming vs local-only commits: decides the next row |
| No local-only commits → `git pull --ff-only` | Fast-forward or abort; never an unasked merge commit |
| Local-only, unpublished commits → `git pull --rebase` | Replays them on the upstream; conflicts per `resolve-merge-conflicts` (stages invert, step 1) |
| Local commits already published (`git for-each-ref --contains <c> refs/remotes` lists a ref) | Never rebase them: merge, or ask (rewriting them is radius 3) |
| Dirty tree | Commit or anchor first; `--autostash` hides a pop conflict behind a successful pull |
| Credentials needed | Run network commands with `GIT_TERMINAL_PROMPT=0` and, where Git Credential Manager is the helper (`git config --get credential.helper` = `manager`), `GCM_INTERACTIVE=never`: the first stops the terminal prompt, the second the GCM sign-in window. Over SSH, `GIT_SSH_COMMAND='ssh -o BatchMode=yes'` makes a passphrase or host-key prompt fail instead of wait. A failure is `Needs GD: credentials`; never write one into a URL or config |

## Undo a merged change
| Case | Command | Fact that decides |
|---|---|---|
| Published commit | `git revert <sha>` | New commit; no rewrite, so radius 2 |
| Published merge | `git revert -m 1 <merge>` | `-m 1` keeps the mainline side. A later re-merge of that branch does not bring the reverted changes back; revert the revert first [faulty] |
| Fix to a release branch | `git switch <release>` then `git cherry-pick -x <sha>` | `-x` records the source sha in the message |

## Worktrees
`git worktree add <path> <branch>` gives a second checkout sharing one object store. A Unity worktree has no `Library/`: opening it is a full reimport, and it is a second Editor (`core.md`: ask first). `git worktree remove` refuses on uncommitted changes; `--force` deletes them (radius 3).

## UPM packages from git [upm]
`Packages/manifest.json`: `"com.vendor.pkg": "https://<host>/<org>/<repo>.git?path=/<subfolder>#<tag-or-sha>"`. Pin a tag or sha, never a branch: a branch is held only by the hash in `packages-lock.json`, so anyone who regenerates the lock gets a different commit. A third-party package goes through `security-reviewer` before it lands (`core.md` Security).

## Large clones
| Need | Command | Cost |
|---|---|---|
| Less history data | `git clone --filter=blob:none <url>` | Blobs download on demand: later `checkout`, `blame`, `log -p` need the network |
| Fewer LFS downloads | `GIT_LFS_SKIP_SMUDGE=1 git clone <url>`, then `git lfs pull --include="<paths>"` | Skipped files stay pointers (step 9 check) |
| Fewer directories | `git sparse-checkout set <dirs>` | Unity needs all of `Assets/`, `Packages/`, `ProjectSettings/`; only non-project folders are worth excluding |

## Maintenance
`git maintenance run --task=commit-graph` and `--task=incremental-repack` are safe. `gc`, `prune` and `git lfs prune` delete objects: radius 3, and never during a recovery (`git-recovery`). `git lfs prune --dry-run` lists what would go [lfs].

## Pull requests and signing
| Task | Fact that decides |
|---|---|
| Open a PR | Push first (GD-ordered), then `gh pr create --base <b> --head <branch> --title "<subject>" --body-file <file>`; the body follows the attribution the session gives. Publishing: only when the GD asked |
| `commit.gpgsign=true` or a signing key is set | Signing may need a passphrase prompt that has no terminal here. A signing failure is `Needs GD: signing`; never `--no-gpg-sign` or `-c commit.gpgsign=false` |

## Windows and large-repo specifics
| Case | Fact that decides |
|---|---|
| Case-only rename (`Player.cs` → `player.cs`) on Windows (`core.ignorecase=true`) | A plain rename is invisible to git. `git mv Player.cs player.cs` and `git mv Player.cs.meta player.cs.meta` together, in one commit; renaming in Explorer leaves two index entries on a case-sensitive clone, and Unity can mint a second GUID |
| `Filename too long` on checkout | `git config core.longpaths true` (local write, radius 2) |
| Slow `status` on a large `Assets/` | `git config core.untrackedCache true`; `core.fsmonitor=true` uses git's built-in daemon (local config, never on the command line, where the hook refuses it) |
| Shallow clone (CI, `--depth`) | `blame`, `bisect`, `log -S` see only the fetched depth and answer wrongly without error: `git rev-parse --is-shallow-repository`, then `git fetch --unshallow` before forensics |

## Release tags
`git tag -a v<x.y.z> -m "<subject>" <sha>` (annotated: carries tagger and date), then `git push origin v<x.y.z>`, one tag by name; `--tags` is refused because it publishes `backup/*` anchors. A release tag is asked for first (`core.md`) and runs from `/release`.

