# Comparison: batch T3.2, attempt 1

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`.
- **Verdict:** fail. Failing skills: `ad-mediation-monetization-platform`, `analytics-telemetry-platform`, `anti-cheat-strategy`, `cross-platform-expansion-assessment`, `netcode-architecture-decision`, `source-credibility-grading`.
- **Other 9 skills:** every Base criterion kept or moved as listed below. Kept lines are not listed.

## Findings

Line numbers: Base at the Base sha, current in the working tree. Every fix keeps step numbers, stays under 200 chars and matches the titled-item shape.

| Skill | Check | Base text | Current text | Why it fails | Exact fix |
|---|---|---|---|---|---|
| `ad-mediation-monetization-platform` | 1, 2 (deleted line) | `:40` "On request only, add ... (each with its trigger: policy change, region launch, scale)." | Absent. Step 7 says policies "change" and step 3 names regions; neither says they re-open the decision. Scale appears nowhere. | The three named triggers are a domain condition on how long this decision holds, not an envelope field: `Limitations` is "what this does not do" and has no trigger slot. The batch brief moves a domain-specific limit in a deleted line to a step; T3.1 did the same for `git-unity-repo`. | Add after step 8 (after `:35`): `9. **Re-decision triggers:** on request, name what re-opens this decision: policy change, region launch, scale.` |
| `analytics-telemetry-platform` | 1, 2 (deleted line) | `:33` "On request only, add ... (each with its trigger: volume, region, pricing)." | Absent. `volume` survives only as a migration field at `:38`, a different meaning. Pricing as a trigger appears nowhere. | Same as above. | Add after step 7 (after `:29`): `8. **Re-decision triggers:** on request, name what re-opens this decision: volume, region, pricing.` |
| `anti-cheat-strategy` | 1, 2 (step 1) | `:12` "Player-to-player item trading makes duplication an economy attack even without PvP, so stakes are at least medium; confirm server authority over item creation and transfer as the floor." | `:18` "**Floor:** confirm server authority over item creation and transfer as the floor." | The split dropped the shared condition. The check now applies to every game, including one with no item trading. Step 2 already holds the general floor, so this bullet's only content is the conditional one. | Replace `:18`: `   - **Item-trading floor:** with player-to-player item trading, confirm server authority over item creation and transfer as the floor.` |
| `anti-cheat-strategy` | 1, 8 (step 5) | `:16` "**Tiers and what each buys** — server authority: ..." No instruction to price. | `:27` "**Tiers and what each buys:** price each tier against its cover." | Added instruction breaks a required order: step 6 disqualifies a tier "before price", and step 9 scores only survivors. | Replace `:27`: `5. **Tiers and what each buys:** what each tier covers.` |
| `cross-platform-expansion-assessment` | 1, 2 (step 3) | `:14` "if the committed netcode model or anti-cheat tier does not carry over, say plainly it reopens `netcode-architecture-decision` or `anti-cheat-strategy`" | `:20` "...may not carry over." `:21` "**Reopening:** say plainly it reopens ..." | The `if` is gone. `:20` only speculates and `:21` is now unconditional, so a platform that carries both decisions still gets a stated reopening. This step is cited (`anchors.md`) and step 8 keys Low reversibility on it. | Replace `:21`: `   - **Reopening:** if the committed netcode model or anti-cheat tier does not carry over, say plainly it reopens `netcode-architecture-decision` or `anti-cheat-strategy`.` |
| `cross-platform-expansion-assessment` | 2 (step 5) | `:16` "controller focus navigation per screen, safe area and aspect ratio, readability at TV distance" | `:26` "**Per screen:** controller focus navigation, safe area and aspect ratio, readability at TV distance." | "per screen" qualified one item. As a title it covers all three, which changes what the estimate must enumerate. | Replace `:26`: `   - **Reflow items:** controller focus navigation per screen, safe area and aspect ratio, readability at TV distance.` |
| `netcode-architecture-decision` | 1, 2 (step 4) | `:15` "lockstep/rollback need a bit-deterministic simulation; floats and Unity physics are not deterministic across platforms. A deterministic framework presupposes it" | `:29` "**Presupposition:** a deterministic framework presupposes it (...)" | As its own bullet the pronoun has no antecedent; the nearest candidate at `:28` is "floats and Unity physics", the wrong one. The bullet carries the requirement the skill's Never calls "the most common expensive failure". | Replace `:29`: `   - **Presupposition:** a deterministic framework presupposes a bit-deterministic simulation (`csharp-standards` → `coding-principles.md` Shared Core integrity).` |
| `netcode-architecture-decision` | 8 (step 3) | `:14` "**Shortlist by sync model, not popularity** — Mirror, FishNet: ..." | `:21` "...: each option fits one model." | Added claim absent from Base and contradicted by `:26` `Custom`, which names no model. | Replace `:21`: `3. **Shortlist by sync model, not popularity:** options by model.` |
| `source-credibility-grading` | 2 (step 5) | `:18` "forum consensus wins only on real-world caveats docs omit, and needs two independent corroborations" | `:33` "**Real-world caveats docs omit:** forum consensus wins, and needs two independent corroborations." | The plain-word limit "only" is gone. The bullet now says where forums win, not that they win nowhere else. | Replace `:33`: `   - **Real-world caveats docs omit:** forum consensus wins only here, and needs two independent corroborations.` |
| `source-credibility-grading` | 2 (step 6) | `:19` "Read a licence from the repository's LICENSE file (Asset Store: the licence named on the package page), never a summary." | `:34` "...LICENSE file:** Asset Store: the licence named on the package page, never a summary." | Without the parenthesis the ban attaches to the Asset Store clause, so repository licences lost "never a summary". | Replace `:34`: `6. **Read a licence from the repository's LICENSE file, never a summary:** Asset Store: the licence named on the package page.` |

## Cuts

| Skill | Base text | Class |
|---|---|---|
| `engineering-standard-adr-authoring` | "On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger." | Batch brief "Remove or move"; no domain trigger named |
| `anti-cheat-strategy` | Same line, "each with its escalation trigger" | Same |
| `backend-build-vs-buy` | Same line, "each with its re-decision trigger" | Same |
| `cross-platform-expansion-assessment` | Same line, "each with its re-estimate trigger" | Same |
| `live-ops-content-pipeline`, `netcode-architecture-decision` | Same line, "each with its re-open trigger" | Same |
| `tco-reversibility-scoring` | Same line, "each with its re-score trigger" | Same |
| `tech-vendor-dependency-risk-assessment` | Same line, "each with its re-assessment trigger" | Same |
| `practical-fit-screening` | Same line, "each with its re-screen trigger" | Same |
| `solution-comparison-report` | Same line, "each with its re-evaluation trigger" | Same; `Picture taken ... restate if` stays at `:47` |
| `source-credibility-grading` | Same line, "each with its re-check trigger" | Same |
| `technology-scouting-sweep` | Same line, "each with its re-sweep trigger" | Same |

- **Decision rule:** 14 skills had this line. Twelve only restate the skill's own verb, so nothing specific is lost. Two name domain conditions and are findings above.
- **"Common knowledge" cuts:** none, so no automatic finding.
- **`Never` bullets deleted:** none.

## Moves

| Skill | Base | Now |
|---|---|---|
| `engineering-standard-adr-authoring` | `:11` "`cto` drafts the ADR ..." prose | `SKILL.md:14` `Writer` bullet |
| `design-precedent-sweep` | `:10` `Sources:` line | `SKILL.md:13` `Docs` bullet |
| `practical-fit-screening` | Step 3 SPDX URL | Kept at `SKILL.md:27`, copied to `Docs` at `:15`; no new fact |
| `technology-scouting-sweep` | `:10` `Docs:` line | `SKILL.md:13`-`:18`, nested; all 5 URLs and "one doc set per release" present |
| `tco-reversibility-scoring` | `:9` `Not for` skill list | `SKILL.md:9`-`:14`, nested; all 8 skills present |
| `source-credibility-grading` | `:15` Precedent claims paragraph | `SKILL.md:22`-`:26` |

## Resolved tokens

- **Run:** `token-survival.ps1 -Base bdf5c9ec... <15 skills>`: 366 tokens, 45 missing, matching the author's count. All 45 explained below.
- **Deleted by rule (42):** `Known limitations`, `Latent concerns`, `Future remediation` in 14 skills. `design-precedent-sweep` had no such line. Confirmed by reading.
- **Description compounds (3):** frontmatter equals `HEAD`. `fill/eCPM` at `ad-mediation-monetization-platform:18`; `Deck/console` at `anti-cheat-strategy:32`; `Transport/LiteNetLib` at `netcode-architecture-decision:26`. The two vendor parentheticals in those skills' steps were already at `HEAD` (T2), so they are not T3.2 additions.

### Author explanations refuted
- **"no domain-specific limit was in them":** false for `ad-mediation-monetization-platform` and `analytics-telemetry-platform`. See findings.
- **"step 3 of cross-platform keeps the same pair":** cross-platform step 3 holds neither. `Steam Deck` is at `:57`, console at `:29`. `anti-cheat-strategy:32` carries the token, so nothing was lost.

### Author explanations confirmed
- **Earlier misses:** `backend-build-vs-buy:28` and `cross-platform-expansion-assessment:32` titles hold the whole Base text.

## Author claims tested, no finding

- **`Precedent claims`:** the title is exact at `source-credibility-grading:22`. The `design-precedent-sweep:23` citation resolves to the same subject, and so does `researcher.md:25`, which `anchors.md` does not list. Sibling tiers are labelled, so they cannot be read as the publisher tiers. `Precedent T4` still falls under step 3 "Reject T4".
- **Output blocks:** all 15 fences are identical to Base after CRLF normalisation (md5). No Base fence held `Verified` or `Known limitations`; `solution-comparison-report` keeps its `Unverified` field.
- **`ad-mediation-monetization-platform:24` "Custom ledger there":** Base's own word; the adjacent bullet is the correct referent.
- **`engineering-standard-adr-authoring:17` "one of the following must hold":** `Call still open` is a sibling of the three conditions, but its own text gives the Base outcome, so behaviour is unchanged.
- **`tech-vendor-dependency-risk-assessment:19` and `technology-scouting-sweep:38`:** "never infer health" and "Paid" sit in slightly wider bullets. No limit is lost.

## Other checks

- **Anchors:** every row resolves to the same subject. `ad-mediation-monetization-platform` step 5 `:21`, step 8 `:28`; `cross-platform-expansion-assessment` step 3 `:20`; `live-ops-content-pipeline` steps 3 `:22`, 5 `:28`, 7 `:32`, 9 `:34`; `csharp-standards` citations at `netcode-architecture-decision:29`, `practical-fit-screening:34`. All 15 skills keep their Base step count and numbers.
- **Ask:** `ask-check.ps1` whole layer: no open hit and no unused row in these skills. The 6 hits match their 6 allowlist rows, all "Not an instruction". Its `-Skills` argument failed with several names under `pwsh -File` (exit 2), so the whole-layer run is the evidence.
- **Moved code:** n/a. No references or scripts in these skills at Base or now.
- **Sections:** all 15 have `## Steps`, as `batches.md` requires by omission from its list of 22.
- **Scope:** frontmatter equals `HEAD` in all 15. `git status` shows only these 15 files plus untracked `.workflow/`.
- **Verify:** `verify.ps1 -File` on each: OK, 0 warnings. Whole layer: `verify-layer: OK (21 warning(s))`, exit 0.
