# Blame and Line History

`git blame` says which commit last wrote the bytes now on a line. `git log -L` lists every commit that changed a range.

## Blame flags
| Flag | Effect |
|---|---|
| `-w` | Ignores whitespace when finding where a line came from; use unless whitespace is the finding |
| `-M[<num>]` | Moves/copies within the same file (min alphanumerics, default 20) |
| `-C[<num>]` | Adds cross-file detection (default 40); the last `<num>` given wins |
| `-L <start>,<end>` | Annotates a range; also `<start>,+<n>`, `/regex/` endpoints, `:<funcname>`; repeatable |
| `--ignore-rev <rev>` | Blames the previous commit that changed the line; repeatable |
| `--ignore-revs-file <file>` | Same for every rev listed (`fsck.skipList` format); repeatable |
| `--reverse <start>..<end>` | Walks forward, reporting the last revision where each line still existed (when it disappeared); path must exist at `<start>`; pair with `-w` |
| `--porcelain` / `--line-porcelain` | Machine output; the latter repeats the full header per line (use for per-line counts) |
| `blame.markIgnoredLines` | Marks lines moved by an ignored commit with `?` |
| `blame.markUnblamableLines` | Marks with `*` lines an ignored commit touched that no other revision can be credited with: report them as unattributed |

## Detection levels
| Level | Also scans |
|---|---|
| `-M` | Moved/copied lines in the file |
| `-C` | Other files the same commit modified |
| `-C -C` | Files in the commit that created the file (survives a split/extraction) |
| `-C -C -C` | Files in any commit: widest, slowest; finds a paste from a file the commit never touched |

Each extra `-C` can change the commit named (written vs merely pasted). Record the level in the finding.

## Ignoring reformat commits
```sh
git config blame.ignoreRevsFile .git-blame-ignore-revs
```
- One full 40-character sha per line; `#` comments and blanks ignored. Comment each entry with what the commit did, in English.
- An abbreviated sha is not the documented input (the man page states no fallback or error). Enable `blame.markIgnoredLines` and confirm `?` markers appear; otherwise report the exclusion as unverified.
- Command-line exclusions add to the configured list; an empty filename resets it (a trace without the project's exclusions).

```
# Reindent every C# file to Allman braces; no behavioural change.
<full 40-char sha>
```

## git log -L
`-L <start>,<end>:<path>`, `-L <start>,+<n>:<path>`, `-L /<regex>/,<end>:<path>`, `-L :<funcname>:<path>`; repeatable; implies `--patch`.

| | `git blame` | `git log -L` |
|---|---|---|
| Answers | Last writer of each line now present | Every change to the range, oldest to newest |
| Line added then removed | Not shown (unless `--reverse`) | Shown |
| Whitespace/reformat exclusion | `-w`, `--ignore-rev` | None |

Behaviour question -> [content-search-and-bisect.md](content-search-and-bisect.md); line gone -> [finding-lost-and-deleted-work.md](finding-lost-and-deleted-work.md).
