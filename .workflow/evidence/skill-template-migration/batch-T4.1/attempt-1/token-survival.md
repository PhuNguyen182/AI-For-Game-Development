# Token survival explanations (T4.1 attempt 1)

Run: `token-survival.ps1 -Base bdf5c9ec70bf217ee9ed2763abd75fa4280b717c` with the 9 T4.1 skills, after the last edit.

## What the tool printed
```
token-survival: base bdf5c9ec70bf, current C:\Users\Admin\Projects\AI-For-Game\AI-For-Game-Development\.claude\skills
agent-protocol: 27 tokens, 0 missing, 0 found only in scripts/
feature: 145 tokens, 0 missing, 0 found only in scripts/
fix: 39 tokens, 0 missing, 0 found only in scripts/
qa: 22 tokens, 0 missing, 0 found only in scripts/
review: 76 tokens, 0 missing, 0 found only in scripts/
release: 28 tokens, 1 missing, 0 found only in scripts/
  symbol [SKILL.md:3]: analytics/IAP
qa-standards: 28 tokens, 0 missing, 0 found only in scripts/
code-review-method: 59 tokens, 0 missing, 0 found only in scripts/
csharp-standards: 201 tokens, 0 missing, 0 found only in scripts/
TOTAL 9 skill(s), 625 tokens, 1 missing
```

## The 1 miss
- `analytics/IAP` (`release`, `symbol [SKILL.md:3]`): a slash compound in the Base description, reworded in T2 (frontmatter finished there, unchanged by this batch). Both parts stay in the body: gate table row 7 is `Analytics + IAP`, its Pass cell reads `Events seen in the vendor debug view; sandbox purchase + restore`, and the table is verbatim.

## Moved between files, found by the tool in the same folder
- **`feature`:** the compile-check commands and the `unity test` command moved to `feature/references/build-checks.md`. The tool counts that folder, so these show as present, not as `found only in scripts/`.
- **`csharp-standards`:** the 15-line fence moved to `scripts/AbilityRunner.cs`. The fence's lines hold no backticked token, number with a unit, bold title, URL or link, which is why the tool printed `0 found only in scripts/`. The fence body was diffed separately against Base: identical.

## Ask check
- **Output:** `ask-check: 5 hit(s), 4 allowlisted, 1 in resolved form, 0 open`.
- **Unused rows printed:** `qa/SKILL.md|when the GD asks` and `release/SKILL.md|then ask before tag`. Both sentences were frontmatter descriptions at Base, reworded in T2 (`ask-inventory.md`: "a frontmatter hit is not an instruction; T2 may reword it and the row then shows as unused"). No allowlist row was edited.
