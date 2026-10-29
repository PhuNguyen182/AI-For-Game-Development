---
name: ad-mediation-monetization-platform
description: "Decide the ad mediation vendor (AppLovin MAX, ironSource, AdMob) and whether the currency ledger is managed or custom — fill/eCPM vs take rate, switching cost, loot-box disclosure. Use when choosing a mediation or economy backend."
user-invocable: false
---

# Ad Mediation & Monetization Platform

Not for: SDK integration and IAP wiring (`sdk-platform-engineer`), economy/gacha/sink design (GD with `researcher`, `critic`), scoring rubric (`tco-reversibility-scoring`), general dependency vetting (`tech-vendor-dependency-risk-assessment`), player-data persistence (`backend-build-vs-buy`).

## Steps
1. **Decide mediation and ledger separately** — different reversibility and downstream owners; never one bundled recommendation.
2. **Economy design undecided or contested** → redirect that part to the GD and hold the ledger verdict; do not infer the design from the infra question.
3. **Judge mediation on fill rate and eCPM for this game's regions and genre**, net of the platform's take rate. Gross eCPM across vendors compares the wrong number.
4. **Score an existing studio integration as reversibility** (switching cost already paid), not as a tiebreaker.
5. **Ledger authority first** — real-money-adjacent economy, player trading or fraud-sensitive currency needs a server-authoritative ledger (managed usually beats custom: you would own the fraud surface). A cosmetic soft currency needs client-tracked value with server-validated spend; a custom ledger there is speculative complexity.
6. **Score both shortlists with `tco-reversibility-scoring`** — mediation typically Medium (SDK behind a wrapper); a ledger baked into the save format typically Low.
7. **Store-policy check is a gate, not a score** — loot-box/gacha disclosure and IAP receipt validation differ per store and change; an option risking rejection is out, because the exposure is the whole app's store standing.

## Output
```
## Monetization Infrastructure Decision — <project>
### Ad Mediation Platform
- Target regions / genre: <...>
- Options considered / take rate: <per vendor>
- Existing integration: none / <vendor, project>
- TCO / Reversibility: <score>
- Store-policy check: pass / fail — <rule>
- Decision: <vendor> — <reason>
### Economy / Currency Backend
- Ledger requirement: server-authoritative / client-tracked with server-validated spend
- Options considered: managed / custom
- TCO / Reversibility: <score, save-data lock-in>
- Store-policy check: pass / fail — <rules>
- Decision: <option> — <reason>
- Routed to: `sdk-platform-engineer`
```
On request only, add `Known limitations`, `Latent concerns`, `Future remediation` (each with its trigger: policy change, region launch, scale).

## Example
- "Vendor B's eCPM is higher in the deck" → declined: figure is gross and B's take rate is three points higher; net of take rate A wins, and B adds switching cost.
