# model-tiers trials — attempt 1 (log-triage.md at 0d170dc, hook 094bd65, routing afc5907)

Main session, 2026-11-25. Counts, pass/fail and model ids only. Digests kept in the session scratchpad and deleted after.

| Run | Model | Log lines | Digest lines | Tokens in / out / cache-create / cache-read | Hook blocks observed |
|---|---|---|---|---|---|
| fixture (synthetic) | claude-haiku-5-5 | 5000 | 16 | 10 / 6102 / 25229 / 79139 | 0 |
| missing path | claude-haiku-5-5 | 0 | 9 | 4 / 1491 / 20010 / 14340 | 0 |
| Editor.log | claude-haiku-5-5 | 119573 | 18 | 10 / 8601 / 19355 / 84116 | 0 |
| Editor-prev.log | claude-haiku-5-5 | 5211906 | 20 | 12 / 11659 / 25912 / 117409 | 0 |
| upm.log | claude-haiku-5-5 | 579 | 12 | 12 / 10035 / 36018 / 120540 | 0 |
| AssetImportWorker0-prev.log | claude-haiku-5-5 | 1749 | 17 | 14 / 17389 / 40536 / 160548 | 0 |
| read-denied path | claude-haiku-5-5 | unknown | 9 | 6 / 2205 / 15343 / 39804 | 0 |
| AC8 Fable ping (technical-architect) | claude-fable-5-2 | — | — | 2 / 62 / 15415 / 0 | — |

- AC2: pass — every digest has the C1 fields, no Route hint, ≤ 40 lines, excerpt ≤ 20 lines, no cause/fix field.
- AC3: pass with deviation — first blocking line 3001 and `Bar.cs:12` correct; `error CS\d+` 2 = Select-String 2; read 4 windows, never the whole file. Deviation: three unity signatures reported as one alternation count (1 = Select-String 1 for the same alternation), not one count per pattern.
- AC4: pass — 0 of 9 planted values in the digest; secret-patterns scan 0 of 19 patterns (control: same scan finds 4 kinds in the planted values); Redactions 5 lines withheld.
- AC5: FAIL — Editor.log pass (first compile error line 32474 = ripgrep, user path masked); Editor-prev.log pass (BuildFailedException 5192116 = ripgrep, count 4 = 4, user path masked); upm.log FAIL (Log: header kept the raw home-folder path with the OS username); AssetImportWorker0-prev.log FAIL (Log: header raw path, and a quoted line carried the OS username inside a licensing channel name; Redactions 0). Secret-pattern hits 0 in all four.
- AC5 note: the literal criterion "first signature hit" is wrong for logs whose first `Exception` match is a non-blocking stack frame (Editor.log 366, Editor-prev.log 1108); the agent's first blocking pick (compile error / BuildFailedException) is the correct one.
- AC6: pass — all seven log-triage transcripts on claude-haiku-5-5; token totals above.
- AC8: pass — claude-fable-5-2.
- AC13: pass — missing path and read-denied path both `Blocked`, naming the path (the header of both still shows the raw home-folder path — same defect as AC5).
- Hook blocks observed: 0 in every run (no secret-shaped return, so hook liveness in this session is not shown by these runs).
