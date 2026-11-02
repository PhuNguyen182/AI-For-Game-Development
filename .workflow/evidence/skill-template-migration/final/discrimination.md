# Discrimination of the T5 rev 2 fixtures

- **Run on:** 2026-11-02, working-tree `run.ps1` against variants of `verify.ps1`, in a throwaway copy under the session scratchpad (deleted after).
- **Scope:** the verify-layer section of `run.ps1` only (its head plus everything from `# verify-layer skill format:` on): 119 checks. The hook sections before it do not read `verify.ps1`'s title or fence rules.
- **Shells:** pwsh 7.6.9 for every row. Windows PowerShell 5.1.26100 for `control`, `b50f2e4` and `M-backtrack`, with the same red list as pwsh in each.

## Against `verify.ps1` as of `b50f2e4`

Exit 1, 113 PASS, 6 FAIL, on both shells. Control (working-tree `verify.ps1`): exit 0, 119 PASS, 0 FAIL, on both shells.

Red:
- `verify: a title may hold an odd backtick run, with a backticked pair after the title` (F1, new)
- `verify: no FAIL for title-odd-backtick among the plants` (F1, new)
- `verify: a checklist title takes what a skill title takes` (F5, new)
- `verify: no FAIL for checklist-backtick among the plants` (F5, new)
- `soft: exit 0 on a whole-layer run, no FAIL, no per-file form` (existing; the two new clean fixtures fail there)
- `verify: the whole-layer failure count is the plants and nothing else` (existing; same cause)

Green against `b50f2e4`, as expected: `b50f2e4` already has the rule these guard, so its code cannot turn them red. They are proved by the mutants below.
- F2: `fence-trailing-plant`, `fence-longer-plant`, `long-unclosed`
- F3: the LF/CRLF output comparison
- F4: the backtick-run job
- F5 negative: `a checklist item with no title`

## Against one-rule mutants of the working-tree `verify.ps1`

| Mutant | Change | Exit, PASS, FAIL | Red |
|---|---|---|---|
| `M-trailing` | A mark with trailing text closes a fence | 1, 118, 1 | `the fence closed, and only the plant after it fails: fence-trailing-plant` |
| `M-exactlen` | A closer must match the opener's length | 1, 115, 4 | `verify fails per file: fence-longer-plant`; `the fence closed, and only the plant after it fails: fence-longer-plant`; `verify fails whole-layer: fence-longer-plant`; `the whole-layer failure count` |
| `M-unclosed` | An unclosed fence counts as no fence | 1, 116, 3 | `verify fails per file: long-unclosed reference fence`; `verify fails whole-layer: long-unclosed reference fence`; `the whole-layer failure count` |
| `M-backtrack` | The non-atomic title pattern of before the fix | 1, 117, 2 | `30 backticked pairs with no title end finish within 30 s`; `verify fails per file: backtick-run` |
| `M-crbullet` | The size check splits lines on LF only, so a CR counts | 1, 118, 1 | `a CRLF copy gives the output of its LF original, name aside` |
| `M-anycheck` | A checklist line needs no title | 1, 116, 3 | `verify fails per file: a checklist item with no title`; `verify fails whole-layer: a checklist item with no title`; `the whole-layer failure count` |

## `M-backtrack` timing

- **Result:** the check fails at the 30 s timeout, the job's process is killed, and the run continues to its last check. No process left behind.
- **Run time, pwsh:** 122 s, against 32 s for the control.
- **Run time, Windows PowerShell 5.1:** 57 s, against 26 s for the control.
- **Cause of the pwsh excess:** on pwsh `Remove-Job -Force` takes about 55 s once its process is killed (measured in isolation). On 5.1 it takes 31 ms. This costs time only on a regression.

## T5 rev 3: `short-unclosed` and `title-bare-star`

- **Run on:** 2026-11-02, pwsh 7.6.9, same scope as above (the verify-layer section of the working-tree `run.ps1`, now 123 checks), in a throwaway copy under the session scratchpad (deleted after). Windows PowerShell 5.1 not run here.

| Variant of `verify.ps1` | Change | Exit, PASS, FAIL | Red |
|---|---|---|---|
| `control` | Working tree | 0, 123, 0 | none |
| `9ce3cdd` | The file as of that commit | 1, 119, 4 | `an unclosed 14-line reference fence with a final newline passes`; `no FAIL for short-unclosed among the plants`; `soft: exit 0 on a whole-layer run`; `the whole-layer failure count` |
| `M-droptwo` | `Test-RefFences` drops two final elements, so one real line goes uncounted | 1, 120, 3 | `verify fails per file: long-unclosed reference fence`; `verify fails whole-layer: long-unclosed reference fence`; `the whole-layer failure count` |
| `M-star` | The title pattern allows a star outside backticks | 1, 120, 3 | `verify fails per file: title-bare-star`; `verify fails whole-layer: title-bare-star`; `the whole-layer failure count` |

- **Boundary:** `long-unclosed` stays green on `9ce3cdd`, where it counted 16. On the working tree it counts 15, so `M-droptwo`, one line short of that, turns it red. Together with `short-unclosed` that holds 14 passing and 15 failing for an unclosed fence with a final newline.
