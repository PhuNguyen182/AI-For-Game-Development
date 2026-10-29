# Attribution Honesty

Each instrument reports a narrower fact than readers assume. State the narrower claim. Rows marked (inferred) are reasoning from documented mechanics, not an upstream statement.

## Reports vs meaning
| Tool reports | Actually means |
|---|---|
| `blame` names a commit | Last to write those bytes; a reindent, rename, encoding change or licence sweep counts as much as a logic change |
| Same line differs under `-w -C -C -C` | Detection level changed, not the truth; the level is part of the finding |
| `--ignore-rev` moved the blame earlier | Now the previous changer, possibly another unlisted reformat |
| `*` line (`blame.markUnblamableLines`) | No honest author: report as unattributed |
| `%an` | Recorded author metadata, overridable; not proof this person typed the line |
| `bisect` first bad commit | Oldest tested revision where the test failed, given the marks and verdicts |
| `shortlog -sn` | Commit counts per author in the walked range, not lines, effort or ownership |
| `blame` on a moved file without `-C` | The rename commit is last writer of every line |

## Author vs committer
| Operation | Author (`%an`) | Committer (`%cn`) |
|---|---|---|
| Ordinary commit | Committer | Same person |
| Rebase / cherry-pick | Preserved | Whoever ran it, new date |
| Amend | Preserved unless reset | Whoever amended (sha changes, author does not) |
| `--author` override | Unverified string | Person who ran it |
| Applied patch | Patch `From:` header | Maintainer who applied it (inferred) |
| Squash | The squasher; collapsed authors survive only in the message, if at all (inferred) | Squasher |
| Filtered/rewritten history | Whatever the rewrite wrote; originals may be gone | Whoever rewrote |

```sh
git log -5 --pretty=format:'%h | author %an | committer %cn | %s'
```
When the two diverge, an operation above happened and neither field alone says who wrote the code. On a squash-merge repo an attribution is about the merge process, not the writer.

## Cause vs exposure
| Claim | Justified by |
|---|---|
| "First revision where the test fails" | `bisect` marks and verdicts, reproducible from `git bisect log` |
| "This commit caused the fault" | Reading its diff and confirming it introduced the faulty logic (`bisect` does not do this) (inferred) |
| "Exposed a latent fault" | Diff innocent alone but made an existing defect reachable (new call into broken function, config crossing a threshold, timing change) (inferred) |
| "The merge introduced it" | `bisect --first-parent` names the merge, not the commit that wrote it |
| "Nothing before was affected" | Only if every good revision used the same deterministic check; `skip`ped ranges are untested and appear in `git bisect log` |
| Flaky test | Supports nothing; the result looks identical to a sound one |

Causing commit routes to the owner of the code it changed; exposing commit to the owner of the latent defect. Name which one.

## Shortlog
`-s` counts only, `-n` sort by count, `-e` adds email (splits same-name identities), `-c`/`--group=committer` group by committer (differs on rebase/patch repos), `--group=trailer:<field>` groups by trailer (commits without it are not counted; several values count once each), `--no-merges`.
```sh
git shortlog -sne --no-merges HEAD
```
| Distortion | Effect |
|---|---|
| Squash-merge | Counts collapse toward the squasher (inferred) |
| Rebase-heavy | Author counts survive, committer counts concentrate on the rebaser |
| Rewritten/imported history | Only the rewritten history is counted |
| Several identities for one person | Separate groups unless a mailmap merges them |
| Path-limited range | Simplification prunes commits first: a lower bound, not a total |
| Formatting, generated, vendored commits | Inflate counts (inferred) |

## Ownership data
| Question | Can answer | Cannot answer |
|---|---|---|
| Who should fix this file | Who has recent commits there | Whether they still own the area |
| Who knows this code | Where commits cluster | Knowledge of reviewers, designers, pairs (inferred) |
| Who broke this | Which commit changed the line, at which detection level | Intent, competence, fault: the commit may implement a spec or review comment |
| Whose performance is at fault | Nothing: route to `gd` | Everything |
| Who owns the decision a commit encodes | Nothing in the commit; it lives in the Tech Spec | Origin of the decision |

Report the commit by default; name a person only if asked, with the identity field (`%an`/`%cn`), the operations that could have changed it, and the detection level.
