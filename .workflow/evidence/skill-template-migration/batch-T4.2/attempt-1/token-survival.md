# Token survival explanations (T4.2 attempt 1)

Run: `token-survival.ps1 -Base bdf5c9ec70bf217ee9ed2763abd75fa4280b717c` with the 9 T4.2 skills, after the last edit.

## What the tool printed
```
token-survival: base bdf5c9ec70bf, current C:\Users\Admin\Projects\AI-For-Game\AI-For-Game-Development\.claude\skills
decide: 13 tokens, 0 missing, 0 found only in scripts/
new-project: 73 tokens, 0 missing, 0 found only in scripts/
plan-game: 15 tokens, 0 missing, 0 found only in scripts/
plan-test-coverage: 21 tokens, 0 missing, 0 found only in scripts/
investigate-device-crash: 35 tokens, 1 missing, 0 found only in scripts/
  symbol [SKILL.md:3]: Android/iOS
resolve-merge-conflicts: 72 tokens, 0 missing, 0 found only in scripts/
review-code-risks: 48 tokens, 0 missing, 0 found only in scripts/
save-workmemory: 3 tokens, 0 missing, 0 found only in scripts/
verify-layer: 29 tokens, 0 missing, 0 found only in scripts/
TOTAL 9 skill(s), 309 tokens, 1 missing
```

## The 1 miss
- `Android/iOS` (`investigate-device-crash`, `symbol [SKILL.md:3]`): a slash compound in the Base description, reworded in T2 (frontmatter finished there, unchanged by this batch). Both parts stay in the body: `[android|ios]` under `Input`, `Android source`, `Android commands` and `iOS commands` under step 3.

## Tokens the tool passes that changed form
- `Verify` (`resolve-merge-conflicts`, bold title of step 10): the title is now `Verify the resolution`, because the dispatch bans a `Verify:` title (`round-cap.ps1` marker shape). The number and subject are unchanged.
- `Verified on real device: yes` (`investigate-device-crash`, Output fence, not a tool token): the line left `## Output` per the brief; step 5 `Real device` holds the same statement, and `Not covered` stays in the fence as its own line.

## Ask check
- **Output:** `ask-check: 40 hit(s), 38 allowlisted, 2 in resolved form, 0 open`.
- **Unused rows printed:** `release/SKILL.md|then ask before tag` and `qa/SKILL.md|when the GD asks`. Both were frontmatter sentences at Base, reworded in T2, and T4.1 reported the same two. No allowlist row was edited.
