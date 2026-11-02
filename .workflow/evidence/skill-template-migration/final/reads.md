# Reads with no report of their own

Copied by the main session from the agents' returns, which were not written to disk. Each is a reading, not a run.

## Independent read of the last 8 lines (after `reread-81`)
- **Reader:** general-purpose agent on `sonnet`, not the author of those lines.
- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`, read with `git show` for the descriptions and the IAP line.
- **Method for the reference lines:** new at the migration, so compared with the sample script headers.
- **Result:** all 8 pass, no replacement needed.
- **Lines:**
  - `feature/SKILL.md:3`
  - `backend-build-vs-buy/SKILL.md:3`
  - `consent-att-init-order/references/google-ump.md:20`
  - `osa-optimized-scrollview-adapter/references/pooling-and-performance.md:25`
  - `flexalon-layouts/references/custom-layouts.md:20`
  - `litmotion-tweening/references/litmotion-animation-component.md:27`
  - `csharp-standards/references/code-style-and-layout.md:10`
  - `iap-server-receipt-ledger/SKILL.md:69`
- **Commit:** `c824afd`.

## CP3 final anchor walk
- **Reader:** `technical-architect`, CP3 mode, read-only.
- **Result:** 341 of 341 rows resolve, 0 unresolved.
- **Step rows:** 167; current title at each number against the inventory subject.
- **File and path rows:** 109 + 21; every distinct cited file exists at its path.
- **Heading rows:** 8; headings present, and citations still name them.
- **Hook rows:** 33; `$HookContracts` read, 33 strings match the rows.
- **Internal rows:** 3.
- **Same subject, reworded:** `resolve-merge-conflicts` step 10; `performance-budget-verification` step 9; `unity-3d-physics` step 3; `consent-att-init-order` 3(d).
- **Not checked:** citing lines in agents, rules, hooks and memory notes, row by row; those rows were checked on the cited side only.

## Budget headroom
- **Method:** `claude -p /context` on a 1M window, with the fraction set for one run through `--settings`; output in `context-*.txt` here.
- **0.01 (control):** 55 name-only rows, Skills 9.9k. Proves the flag takes effect.
- **0.01805:** 1 name-only row, Skills 17.7k. So 0.019 did not have 5% headroom.
- **0.019 (`context-plain.txt`):** 201 of 201 rows listed, Skills 18k.
- **Conclusion:** the listing fits 0.019, which is 95% of 0.02, so 0.02 meets AC2's 5% floor. Standing cost is the listing itself, about 18k; the setting only moves the cap.
