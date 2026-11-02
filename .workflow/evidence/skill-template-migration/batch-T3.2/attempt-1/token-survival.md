# Token survival explanations (T3.2 attempt 1)

Run: token-survival.ps1 -Base bdf5c9ec70bf217ee9ed2763abd75fa4280b717c with the 15 T3.2 skills. Final output: "TOTAL 15 skill(s), 366 tokens, 45 missing". Every miss is explained below.

## Deleted by rule (batch brief "Remove or move")
- 42 misses: `Known limitations`, `Latent concerns`, `Future remediation` (3 tokens each) in 14 skills. The "On request only, add ..." line after `## Output` was deleted in each of them. The tool prints one line per token per skill. design-precedent-sweep had no such line (0 missing).
- Skills: ad-mediation-monetization-platform, analytics-telemetry-platform, anti-cheat-strategy, backend-build-vs-buy, cross-platform-expansion-assessment, engineering-standard-adr-authoring, live-ops-content-pipeline, netcode-architecture-decision, tco-reversibility-scoring, tech-vendor-dependency-risk-assessment, practical-fit-screening, solution-comparison-report, source-credibility-grading, technology-scouting-sweep.
- Each deleted line only added optional fields with re-evaluation triggers; no domain-specific limit was in them, so nothing moved to a step or `Never`.

## Description symbols (frontmatter unchanged in T3.2; lost in T2)
The tool printed `symbol [SKILL.md:3]` for three compounds in the Base description. Each part survives in the body:
- ad-mediation-monetization-platform `fill/eCPM`: step 3 keeps "fill rate and eCPM".
- anti-cheat-strategy `Deck/console`: step 6 keeps "Steam Deck/Proton" and "per-console certification"; step 3 of cross-platform keeps the same pair.
- netcode-architecture-decision `Transport/LiteNetLib`: step 3 keeps "Unity Transport, LiteNetLib" in the Custom bullet.

## Earlier misses fixed in this run
- backend-build-vs-buy step 7: bold title was "Recommend per component" and the tool flagged "Recommend per component; a mixed result is normal". Title now carries that whole text.
- cross-platform-expansion-assessment step 9: same cause; title is now "Give the GD cost, timeline and risk in product terms and leave the decision to them".
