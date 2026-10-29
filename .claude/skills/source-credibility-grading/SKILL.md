---
name: source-credibility-grading
description: "Grade external sources T1 official docs, T2 maintained repo, T3 forum consensus, T4 unverified, plus tiers for shipped-game precedents; date every claim; resolve conflicts by tier. Use before any claim enters a research report."
user-invocable: false
---

# Source Credibility Grading

Not for: finding sources (`technology-scouting-sweep`), project-fit gating (`practical-fit-screening`), ranking (`solution-comparison-report`), measuring (`rd-engineer`).
Docs: licence identifiers https://spdx.org/licenses.

## Steps
1. **Grade each source when its claim is captured**, not after drafting.
2. **Tier by publisher, not by how authoritative it reads** — T1 first-party docs, specs, release notes, and a vendor's own pricing, quota and docs pages; T2 a maintained repo's README, source, LICENSE, or an Asset Store package page (publisher, supported versions, licence, last update); T3 established forum answer with visible consensus; T4 everything else.
   **Precedent claims** (how a shipped game solved a problem): T1 the shipping team's own account — GDC talk, postmortem, studio tech blog, engine-vendor case study naming the studio; T2 a named author's teardown of the shipped game; T3 forum consensus; T4 everything else.
3. **Reject T4** (content farm, undated tutorial, AI listicle, a vendor's marketing claims of performance or adoption) rather than downgrading.
4. **Date every claim; staleness is a defect independent of tier** — T1 for an older engine version, T2 whose last release predates the project's version, T3 older than an API change. A stale T1 outranks nothing.
5. **Resolve conflicts by claim type, not popularity or confidence** — docs win on API behaviour and contract; repo source wins on what compiles against a version; forum consensus wins only on real-world caveats docs omit, and needs two independent corroborations. Name the losing source.
6. **Read a licence from the repository's LICENSE file** (Asset Store: the licence named on the package page), never a summary. **Verify pricing, quota and performance figures at the vendor's current page** before repeating them.
7. **An API marked deprecated or `[Obsolete]` is disqualifying** — a live docs URL is not evidence of a live API; re-enter the sweep for the replacement.
8. **Open every URL you cite**; carry tier and retrieval date with each claim into the report.
9. **Unsourceable claim → `UNVERIFIED`**, never dropped silently. A load-bearing claim that cannot exceed T4: let the recommendation stand or fall without it, do not launder it in as background.

## Output
```
## Source Grading — <claim or candidate>
- Claim: <fact>
- Tier: T1 / T2 / T3 / T4 rejected
- Source: <URL>, retrieved <date>, published/updated <date>
- Staleness: <matches project version / predates by <n> / undated>
- Conflict: <other source and winner, by claim type> — or "none"
- Corroboration: <second independent source for T3> — or "not required"
- Decision: ADMITTED / ADMITTED AS CAVEAT / REJECTED / UNVERIFIED
- Routed to: <solution-comparison-report / rd-engineer / technology-scouting-sweep>
```
On request only, add `Known limitations`, `Latent concerns`, `Future remediation` (each with its re-check trigger).

## Example
- Blog says "MIT, adds 2 MB" → both T4, rejected; licence re-read from LICENSE (T2); size has no first-party source, `UNVERIFIED`, routed to `rd-engineer` (only a build measures it).
