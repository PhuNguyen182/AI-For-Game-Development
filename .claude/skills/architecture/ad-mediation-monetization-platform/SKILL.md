---
name: ad-mediation-monetization-platform
description: >
  Vendor/infra framework for the two commonly-bundled but actually
  independent monetization decisions — which ad mediation platform to commit
  to (AppLovin MAX, ironSource, AdMob, etc.) and whether the in-game
  economy/virtual-currency ledger should be a managed service or custom-
  built — covering store-policy compliance for both. Use this whenever the
  CTO is choosing an ad mediation vendor or an economy/currency backend
  approach. Do not use this for actually integrating the chosen mediation SDK
  or wiring up IAP against store APIs — that's tech-lead-sdk-platform's
  implementation work. Do not use this to design what the economy, gacha
  rates, or currency sinks actually are — that's a GD/Advisor/Critic design
  decision; this skill only covers the underlying vendor/backend infra.
---

# Ad Mediation & Monetization Platform

## 1. Objective
Give the CTO a consistent framework for the vendor/infra decisions behind monetization — separate from the game-design question of what the economy actually is — so the choice of ad mediation platform and economy/currency backend gets made deliberately rather than defaulted to whatever's easiest to integrate.

## 2. Role
Act as a monetization-infrastructure-focused CTO, aware of mediation vendor market share, fill-rate trade-offs, and store compliance costs.

## 3. When to invoke this skill
- Choosing an ad mediation platform (AppLovin MAX, ironSource, Google AdMob, etc.) for the project.
- Deciding whether the economy/virtual-currency ledger backend should be a managed service (e.g. a PlayFab economy feature, a payment processor's ledger) or custom-built.
- Negative trigger: don't use this for actually integrating the chosen mediation SDK or wiring up IAP against store APIs — that's `tech-lead-sdk-platform`'s implementation work.
- Negative trigger: don't use this to design what the economy/gacha rates/currency sinks actually are — that's a game-design decision for the GD, with Advisor/Critic support; this skill only covers the underlying vendor/backend infra choice.

## 4. How to use this skill
1. Separate the two decisions explicitly — ad mediation platform and economy/currency backend are usually independent choices; don't bundle them into one verdict.
2. For ad mediation: compare fill rate/eCPM track record for the project's target regions and genre, the mediation platform's own take rate, integration/maintenance burden, and existing relationships (a platform already integrated for a prior/sibling project has a real switching-cost advantage — factor that into reversibility).
3. For the economy/currency backend: does the game need a server-authoritative ledger (any real-money-adjacent economy, trading, or anti-fraud-sensitive currency) or is a simpler client-tracked value with server validation on spend sufficient? This determines whether a managed ledger service is even in scope.
4. Score shortlisted options with `tco-reversibility-scoring` — ad mediation platforms are typically Medium reversibility (an SDK swap is real but contained work behind a wrapper); a currency ledger baked into save-data format is typically Low reversibility.
5. Check store-policy compliance for both: ad content rules (loot box/gacha disclosure requirements per platform) and IAP/receipt-validation requirements — flag any option that risks store rejection.
6. Recommend, and hand the result to `tech-lead-sdk-platform` for actual integration once decided.

## 5. Specific goals / tasks this skill performs
- Produce independent, clearly-separated verdicts for ad mediation platform and economy/currency backend infra.
- Flag store-policy compliance risk for either choice explicitly.
- Out of scope: SDK integration implementation, IAP wiring, and economy/gacha design itself.

## 6. Output format
```
## Monetization Infrastructure Decision
### Ad Mediation Platform
- Options considered: ...
- TCO/Reversibility score: ...
- Store-policy compliance check: pass/fail
- Decision: ...

### Economy/Currency Backend
- Ledger requirement: server-authoritative / lightweight client+server-validated
- Options considered: ...
- TCO/Reversibility score: ...
- Decision: ...
```

## 7. Examples
**Example 1**
- Input: a mobile mid-core game choosing its ad mediation and currency backend.
- Output: AppLovin MAX recommended (existing studio relationship, low switching cost); lightweight server-validated currency recommended (no real-money trading in the design).

**Example 2**
- Input: a game with a real-money-adjacent trading economy.
- Output: a managed ledger service recommended over a custom-built one, given the fraud/compliance exposure of building currency-trading infrastructure in-house.

## 8. Edge cases & guardrails
- Never let ad mediation vendor choice be driven by eCPM alone — factor integration/maintenance burden and existing relationships into reversibility.
- Any option touching gacha/loot-box mechanics must be checked against current store disclosure policy before being recommended — a policy violation risks the whole app's store standing, not just the monetization feature.
- If the economy design itself (not just its backend) seems undecided or contested, redirect that part of the question to the GD/Advisor — this skill only owns the infra layer.
