---
name: ad-mediation-monetization-platform
description: >
  Vendor/infra framework for two commonly-bundled but independent decisions —
  which ad mediation platform to commit to (AppLovin MAX, ironSource, Google
  AdMob) and whether the virtual-currency ledger should be a managed service
  or custom-built — weighing fill rate and eCPM against take rate, switching
  cost, and store disclosure policy for gacha/loot-box and IAP receipt
  validation. Use when choosing a mediation vendor or economy backend.
  Not for: integrating the chosen SDK or wiring IAP
  (`tech-lead-sdk-platform`), designing the economy, gacha rates, or currency
  sinks (a GD decision with `advisor`/`critic`), the scoring rubric
  (`tco-reversibility-scoring`), general dependency vetting
  (`tech-vendor-dependency-risk-assessment`), player-data persistence
  (`backend-build-vs-buy`).
---

# Ad Mediation & Monetization Platform — vendor and ledger decision

## 1. Objective
Give the CTO a consistent framework for the infrastructure decisions behind monetization — kept separate from the game-design question of what the economy is — so the mediation platform and the currency ledger are chosen deliberately rather than defaulted to whatever integrates fastest.

## 2. Role
Act as a monetization-infrastructure CTO: aware of mediation vendor market share, fill-rate and take-rate trade-offs, and what store compliance actually costs when it goes wrong.

## 3. When to invoke this skill
- Choosing an ad mediation platform for the project.
- Deciding whether the economy/virtual-currency ledger runs on a managed service or custom-built infrastructure.
- A mediation SDK or ledger service is about to be adopted without the store-policy check having been run.
- Negative trigger: the vendor is chosen and the work is integrating the SDK or wiring IAP against store APIs — that is `tech-lead-sdk-platform`.
- Negative trigger: the question is what the economy, gacha rates, or currency sinks should be — a GD design decision supported by `advisor` and `critic`; this skill owns only the infra beneath it.
- Negative trigger: the question is whether a third-party dependency in general is safe to build on — that is `tech-vendor-dependency-risk-assessment`.

## 4. How to use this skill
1. **Separate the two decisions before evaluating either** — the mediation platform and the currency ledger are independent choices with different reversibility profiles. Bundling them lets the easier decision drag the harder one.
2. **Judge mediation on fill rate and eCPM for this game's target regions and genre, not on headline averages** — a vendor's global eCPM says little about the regions this title actually ships to, and genre mix moves it further.
3. **Price the mediation platform's own take rate into ongoing cost** — the revenue that reaches the studio is net of it, so comparing gross eCPM across vendors compares the wrong number.
4. **Count an existing studio relationship as reversibility, not sentiment** — a platform already integrated on a sibling project carries a real, quantifiable switching-cost advantage. Score it in that bucket rather than as a tiebreaker feeling.
5. **Decide whether the ledger needs server authority at all before shortlisting ledger vendors** — any real-money-adjacent economy, player-to-player trading, or fraud-sensitive currency needs an authoritative ledger; a cosmetic soft currency usually needs only client-tracked value with server validation on spend. This question decides whether a managed ledger is even in scope.
6. **Score both shortlists with `tco-reversibility-scoring`** — mediation typically lands Medium reversibility, since an SDK swap behind a wrapper is real but contained; a currency ledger baked into the save-data format typically lands Low and should be weighted accordingly.
7. **Run the store-policy check as a gate, not a scoring factor** — gacha and loot-box disclosure rules, and IAP receipt-validation requirements, differ per store and move. An option that risks rejection is out, because the exposure is the whole app's store standing rather than one feature's revenue.
8. **Write both verdicts in English**, per `language-and-comments.md`'s Working language section — `tech-lead-sdk-platform` implements against this document; the Vietnamese reply to the GD is the final message, not the document.
9. **Redirect the economy design question to the GD when it turns out to be undecided** — this skill cannot choose a ledger for an economy whose shape is still contested, and guessing the shape produces a ledger that fits nothing.

## 5. Specific goals / tasks this skill performs
- Produce two separate, clearly-labelled verdicts: ad mediation platform, and economy/currency backend.
- Establish the ledger's authority requirement before any ledger vendor is considered.
- Gate both verdicts on current store disclosure and receipt-validation policy.
- Score switching cost from real existing integrations rather than treating vendors as interchangeable.
- Out of scope: SDK integration and IAP wiring (`tech-lead-sdk-platform`), economy and gacha design (GD, `advisor`, `critic`), persistence infra (`backend-build-vs-buy`).

## 6. Output format
```
## Monetization Infrastructure Decision — <project>
### Ad Mediation Platform
- Target regions / genre: <what fill rate and eCPM were judged against>
- Options considered: <vendors>
- Take rate: <per vendor>
- Existing integration: none / <vendor, from which project>
- TCO / Reversibility: <score from tco-reversibility-scoring>
- Store-policy check: pass / fail — <which rule>
- Decision: <vendor> — <one line>

### Economy / Currency Backend
- Ledger requirement: server-authoritative / client-tracked with server-validated spend
- Options considered: <managed service / custom>
- TCO / Reversibility: <score, noting save-data lock-in if any>
- Store-policy check: pass / fail — <disclosure and receipt-validation rules>
- Decision: <option> — <one line>

- Rule compliance: both verdicts written in English, per Working language
- Routed to: `tech-lead-sdk-platform` for integration
```

**Extended report — emit ONLY when the requester asks for it.** It replaces each one-line decision rationale with all three fields:
```
- Known limitations: <what these verdicts do not cover — regions unpriced, stores unchecked>
- Latent concerns: <assumptions holding only at current scale, or under current store policy>
- Future remediation: <the trigger for each — the policy change, region launch, or scale that forces a revisit>
```

## 7. Examples
**Example 1**
- Input: a mid-core mobile title choosing mediation and a currency backend; no trading in the design.
- Output: AppLovin MAX on an existing studio integration (switching cost already paid, scored as reversibility rather than preference); client-tracked currency with server-validated spend, since no real-money-adjacent surface exists to justify a managed ledger. Both pass the store check.

**Example 2**
- Input: "vendor B's eCPM is higher in the deck, go with B."
- Output: declined on that basis. B's figure is gross and its take rate is three points higher, so net revenue favours A at this title's region mix; B also has no existing integration, adding switching cost the deck does not show. Re-scored net-of-take-rate, A wins — the number in the deck was the wrong number.

**Example 3**
- Input: a game with player-to-player trading of a purchasable currency.
- Output: managed ledger over custom, on fraud and compliance exposure rather than cost — building currency-trading infrastructure in-house means owning the fraud surface too. Gacha disclosure flagged as a gate to re-check per store before launch, since the design includes a randomised reward.

## 8. Edge cases & guardrails
- Never choose mediation on eCPM alone — take rate, region mix, and existing integration all move the net result, per §4.
- Never treat a store-policy risk as a cost to weigh against revenue: a disclosure violation puts the entire app's store standing at risk, not the monetization feature's.
- Never bundle the mediation and ledger verdicts into one recommendation — they have different reversibility and different owners downstream.
- Never build a custom ledger for an economy that needs no server authority — that is speculative complexity YAGNI already forbids.
- If the economy design itself is undecided or contested, redirect that part to the GD and hold the ledger verdict — do not infer the design from the infra question.
