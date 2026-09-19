---
name: technology-scouting-sweep
description: >
  Tiered external search discipline for a capability the project lacks.
  Tier 1 official docs — Unity Manual, Unity Scripting Reference, Microsoft
  Learn, vendor docs, version-pinned. Tier 2 maintained GitHub repositories,
  filtered with `stars:`, `pushed:`, `archived:`, `language:` qualifiers plus
  release and issue history, and OpenUPM registry presence. Tier 3
  established forums — Unity Discussions, Stack Overflow, GameDev Stack
  Exchange — where visible consensus exists. Use when building a candidate
  set or judging a sweep saturated. Not for: grading a source's
  trustworthiness (`source-credibility-grading`), screening candidates
  against project constraints (`practical-fit-screening`), ranking survivors
  into one recommendation (`solution-comparison-report`), measuring a
  candidate (`rd-engineer`).
---

# Technology Scouting Sweep — finding candidate solutions in tiered source order

## 1. Objective
Produce a candidate set that is complete enough to decide from, without inventing sources, mistaking marketing for documentation, or stopping at the first plausible hit. The failure modes it prevents are specific: recommending a third-party package for something the engine already ships, quoting a forum answer written against an engine version the project no longer runs, citing a repository whose last release predates that version, and reconstructing URLs from memory at report time.

## 2. Role
Act as the external-search discipline for the research track — the tool reached for the moment a feature needs a capability nobody on the project has built, and the answer must come from outside the repository.

## 3. When to invoke this skill
- A feature needs a technique, algorithm, package or SDK the project does not already contain.
- The first-party answer is unknown, and whether the engine already covers the capability has to be settled before looking outward.
- A candidate set exists but its coverage is unproven, and the sweep needs a defined stopping point.
- Negative trigger: a source is already in hand and the question is whether to trust it — that's `source-credibility-grading`.
- Negative trigger: candidates are collected and must be tested against this project's engine version, platforms and licence needs — that's `practical-fit-screening`.
- Negative trigger: screened candidates must be ranked into a single recommendation — that's `solution-comparison-report`.
- Negative trigger: the question needs numbers from this project's hardware — that's a spike, owned by `rd-engineer`.

## 4. How to use this skill
1. **Restate the request as the behaviour needed, never as a product name** — a name-led query returns that product's own marketing and hides every competitor; a behaviour-led query returns the field.
2. **Exhaust tier 1 before opening tier 2** — Unity Manual and Scripting Reference at https://docs.unity3d.com, .NET at https://learn.microsoft.com/dotnet, and the vendor's own docs for anything already in the project. A package adopted for something the engine ships is permanent maintenance bought for nothing.
3. **Pin every tier-1 query and URL to the project's engine and .NET version** — Unity publishes one documentation set per release, so a page from another version can document an API this project does not have, with no visible error.
4. **Filter tier 2 with repository qualifiers instead of free text** — `stars:>500`, `pushed:>` a date inside the last twelve months, `archived:false`, `language:C#`; syntax at https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories. For Unity packages also check https://openupm.com for registry presence and version history.
5. **Read a tier-2 repository's release history and open issues before listing it** — stars record past popularity; the date of the last release, and whether issues filed against the current engine version get answers, record whether it is alive now.
6. **Use tier 3 only to corroborate real-world caveats, never as the API contract** — Unity Discussions, Stack Overflow and GameDev Stack Exchange show what breaks in practice and what developers did about it. They do not define behaviour, and a confident post is not a specification.
7. **Require visible agreement and a checked date before quoting a forum solution** — an accepted answer plus independent corroboration in a separate thread, with the thread's date compared against the current engine version. One upvoted post is one developer's opinion.
8. **Record the URL, tier and retrieval date as each candidate is found** — reconstructing citations after the fact is precisely where invented sources appear.
9. **Stop at saturation — three consecutive distinct queries returning only candidates already collected** — stopping earlier hides the option that would have won; continuing past it buys nothing.
10. **Report an empty or single-item result as a finding, naming the tier that produced it** — "no maintained package exists; teams build this by hand" is actionable, and silence is not.
11. **State the interpretation searched under whenever the capability was ambiguous, and search the most likely reading** — this skill cannot ask mid-run, so a flagged assumption beats a stalled sweep.

## 5. Specific goals / tasks this skill performs
- A candidate set where every entry carries its tier, URL and retrieval date.
- An explicit tier-1 verdict, including "the engine already covers this" when that is the answer.
- Tier-2 entries carrying stars, last release date, archived state and maintenance signal.
- Tier-3 entries carrying the consensus evidence and the thread's date.
- A stated stopping point: saturated, or stopped early with the reason.
- Out of scope: trust grading (`source-credibility-grading`), project-constraint screening (`practical-fit-screening`), ranking and recommendation (`solution-comparison-report`), empirical measurement (`rd-engineer`).

## 6. Output format
```
## Scouting Sweep — <capability, stated as behaviour>
- Searched as: <the behaviour phrasing used, plus the assumption if the request was ambiguous>
- Version pin: <engine and .NET version every tier-1 query and URL was pinned to>
- Tier 1 (official): <what the first-party API covers, or "no first-party coverage"> — <URL>, retrieved <date>
- Tier 2 (repositories): <name — stars, last release, archived yes/no, licence file present> — <URL>, retrieved <date>
- Tier 3 (forums): <the consensus, its corroboration and thread date, or "no visible consensus"> — <URL>, retrieved <date>
- Sweep status: SATURATED / STOPPED EARLY — <the repeating queries, or why it stopped>
- Decision: <candidate set complete / no candidate exists / already covered in project>
- Routed to: <source-credibility-grading / practical-fit-screening / none>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what the sweep did not cover — a paywalled source, a language the queries did not reach>
- Latent concerns: <a candidate maintained by one person, a tier-3 consensus predating the current engine version>
- Future remediation: <the re-sweep trigger for each concern — the release, date or version bump that invalidates it>
```

## 7. Examples
**Example 1**
- Input: a feature needs runtime mesh cutting; the project has nothing for it.
- Output: tier 1 checked first and reported as no first-party coverage; two tier-2 repositories listed with stars, last release date and licence; one tier-3 thread corroborating a mobile-specific caveat; sweep marked SATURATED after three repeating queries; routed to `practical-fit-screening`.

**Example 2**
- Input: "everyone on Reddit says this asset is the standard, just use it."
- Output: declined as the primary answer. The thread is tier 3 and dates from two engine versions back; the repository it points at was archived last year. Tier 1 is checked first, and the tier-3 claim is carried only as a caveat if a live candidate corroborates it.

**Example 3**
- Input: "find a package for object pooling."
- Output: tier 1 returns `UnityEngine.Pool.ObjectPool<T>`, already shipped with the engine. Sweep stops there with `Decision: already covered in project`; no tier-2 search is run, since adopting a package here would add maintenance for a capability the engine provides.

## 8. Edge cases & guardrails
- Never write a URL you did not open — a plausible-looking documentation link that 404s is worse than no citation, because it reads as verified.
- Never let star count stand in for maintenance; a five-year-dead repository keeps every star it ever earned.
- Never skip tier 1 because a third-party option looks more capable — state what the first-party API does and does not cover, then justify going outward.
- Never widen the sweep into adjacent capabilities nobody asked about; that is speculative scope YAGNI already forbids.
- Never present a tier-3 claim as an API contract, however many upvotes it carries.
- If the capability is ambiguous, search the most likely reading and flag it explicitly — do not guess silently, and do not stall.
- This skill reads and reports only. Never install, add, or modify anything found; adoption requires an explicit GD request routed to the owning implementation role.
