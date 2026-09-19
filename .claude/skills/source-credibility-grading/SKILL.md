---
name: source-credibility-grading
description: >
  Trust rubric for external sources feeding a research report. Grades each
  claim T1 first-party docs and specs, T2 a maintained repository's own
  README, source, release notes and LICENSE file, T3 an established forum
  answer with visible consensus, T4 rejected — content farms, undated
  tutorials, AI-generated listicles, marketing pages. Adds staleness checks
  against the project's engine version, `[Obsolete]` API detection, and a
  conflict rule that settles docs versus forum by claim type, not upvotes.
  Use before any claim enters a report. Not for: finding the sources
  (`technology-scouting-sweep`), testing a candidate against project
  constraints (`practical-fit-screening`), ranking candidates
  (`solution-comparison-report`), measuring one (`rd-engineer`).
---

# Source Credibility Grading — deciding which external claims may be acted on

## 1. Objective
Guarantee that every fact in a research report is attributable, dated and strong enough for its job, so a recommendation cannot rest on a content-farm number, an undated tutorial, or a forum answer written against an engine version the project no longer runs. It also settles the case that quietly produces wrong recommendations: an official page and a popular forum thread that disagree.

## 2. Role
Act as the evidence gatekeeper for the research track — the rubric applied to every claim between finding it and writing it down, so trust is decided once, deliberately, rather than inferred from how convincing the prose sounded.

## 3. When to invoke this skill
- A claim found during a sweep is about to be quoted, compared, or used to rank a candidate.
- Two sources disagree, and the report needs one answer rather than both.
- A source's age is in question against the project's engine, .NET or package version.
- A licence, pricing, or performance figure is about to be repeated from a secondary source.
- Negative trigger: no sources are in hand yet and the candidate set is still being built — that's `technology-scouting-sweep`.
- Negative trigger: the source is trusted and the question is whether the project can adopt what it describes — that's `practical-fit-screening`.
- Negative trigger: graded candidates must be ranked into one recommendation — that's `solution-comparison-report`.
- Negative trigger: the claim can only be settled by running it on this project's hardware — that's a spike, owned by `rd-engineer`.

## 4. How to use this skill
1. **Grade each source at the moment its claim is captured, never after the report is drafted** — a claim already written into a draft is one nobody goes back to re-grade.
2. **Assign the tier from who published it, not from how authoritative it reads** — T1 first-party documentation, specifications and release notes; T2 a maintained repository's own README, source and LICENSE; T3 an established forum answer carrying visible consensus; T4 everything else.
3. **Reject T4 outright rather than downgrading it** — a content farm, an undated tutorial, an AI-generated listicle and a vendor landing page are unattributable, and one wrong number from one of them discredits every correct claim beside it.
4. **Date every claim and treat staleness as a defect independent of tier** — a T1 page for an older engine version, a T2 repository whose last release predates the project's version, a T3 answer written before the API changed. A stale T1 outranks nothing.
5. **Resolve conflicts by claim type, never by popularity** — official documentation wins on API behaviour and contract; the repository's own source wins on what actually compiles against a version; a forum consensus wins only on real-world caveats the documentation omits, and only with two independent corroborations.
6. **Read a licence from the repository's own LICENSE file, never from a summary** — a blog naming a licence is a T4 claim about the single fact that can disqualify an entire candidate. Identifiers at https://spdx.org/licenses resolve the exact text.
7. **Treat an API the documentation marks deprecated or `[Obsolete]` as disqualifying, per coding-principles.md's Obsolete APIs section** — the vendor keeps hosting the page long after the API stops being the answer, so a live URL is not evidence of a live API.
8. **Verify a pricing, quota or performance figure at the vendor's own current page before repeating it** — these move without notice, and a stale number repeated confidently is indistinguishable from a fabricated one.
9. **Carry the tier and retrieval date with every claim into the report** — an ungraded claim reads exactly like a guess, so the grading has to survive into the output to be worth anything.
10. **Return `UNVERIFIED` for a claim that could not be sourced instead of dropping it** — the absence of evidence is itself decision-relevant, and a silently dropped claim looks like a claim nobody made.

## 5. Specific goals / tasks this skill performs
- A tier, URL and retrieval date attached to every claim entering the report.
- T4 sources rejected before they can influence a ranking.
- Conflicting sources resolved by claim type, with the losing source named.
- Licences, prices and quotas confirmed at first-party pages rather than repeated.
- Unsourceable claims marked `UNVERIFIED` instead of quietly dropped.
- Out of scope: finding sources (`technology-scouting-sweep`), project-fit gating (`practical-fit-screening`), ranking (`solution-comparison-report`), measurement (`rd-engineer`).

## 6. Output format
```
## Source Grading — <claim or candidate>
- Claim: <the fact being admitted or rejected>
- Tier: T1 official / T2 maintained repository / T3 forum consensus / T4 rejected
- Source: <URL>, retrieved <date>, published or last updated <date>
- Staleness: <matches the project's version / predates it by <n> versions / undated>
- Conflict: <the disagreeing source and which one won, by claim type> — or "none"
- Corroboration: <second independent source for a T3 claim> — or "not required"
- Decision: ADMITTED / ADMITTED AS CAVEAT / REJECTED / UNVERIFIED
- Routed to: <solution-comparison-report / rd-engineer / technology-scouting-sweep>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what the grading could not establish — a paywalled spec, a repository with no release notes>
- Latent concerns: <a T1 page not yet updated for the current version, a vendor price under review>
- Future remediation: <the re-check trigger for each concern — the release, renewal date or version bump>
```

## 7. Examples
**Example 1**
- Input: a blog post states a package is MIT-licensed and adds 2 MB to a mobile build.
- Output: both claims graded T4 and rejected as published. The licence is re-read from the repository's LICENSE file and admitted as T2; the size figure has no first-party source and is returned `UNVERIFIED`, routed to `rd-engineer` as something only a build measures.

**Example 2**
- Input: "the Stack Overflow answer has 800 upvotes, that settles it over the docs."
- Output: declined. Upvotes do not outrank an API contract; the documentation wins on behaviour. The answer is admitted only as a caveat about a real-world failure the docs omit, and only because a separate thread corroborates it.

**Example 3**
- Input: an official documentation page describes exactly the needed API.
- Output: graded T1, then checked for version and deprecation. The page belongs to an older documentation set and the member is marked obsolete in the current one, so the claim is REJECTED and the sweep is re-entered for the replacement API.

## 8. Edge cases & guardrails
- Never admit a claim whose URL you did not open; a citation that cannot be re-opened is a fabrication with a footnote.
- Never let tier substitute for freshness — a stale T1 page is still stale, and the version it documents decides its worth.
- Never resolve a conflict by preferring the more detailed or more confident source; the claim's type decides, per §4.
- Never repeat a licence, price or quota from a secondary source — those are the claims whose errors are most expensive.
- Never silently drop an unsourceable claim; mark it `UNVERIFIED` so the gap is visible to whoever decides.
- If a claim is load-bearing and cannot be graded above T4, say so and let the recommendation stand or fall without it — do not launder it into the report as background.
