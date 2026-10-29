---
name: technology-scouting-sweep
description: "Tiered search for a package, technique or service the project lacks: official docs, then maintained repos and the Asset Store, then forums, version-pinned, with a stop rule and query cap. Use for every research-mode question."
user-invocable: false
---

# Technology Scouting Sweep

Not for: grading a source's trust (`source-credibility-grading`), screening candidates against project constraints (`practical-fit-screening`), ranking survivors (`solution-comparison-report`), measuring a candidate (`rd-engineer`).
Docs: Unity https://docs.unity3d.com (one doc set per release), .NET https://learn.microsoft.com/dotnet, GitHub search syntax https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories, Unity registry https://openupm.com, Unity Asset Store https://assetstore.unity.com.

## Steps
1. **Restate the request as behaviour, not a product name** — a name returns that product's marketing and hides competitors.
2. **Ambiguous capability → search the most likely reading and state the assumption** (the sweep cannot ask mid-run).
3. **Name the subject type; it sets what each tier holds** — package/SDK: as below. Technique (algorithm, pattern): tier 1 adds the original paper or the author's talk, tier 2 is a maintained reference implementation. Hosted service: tier 1 is the vendor's docs and pricing page, tier 2 its Unity SDK repository.
4. **Tier 1 first (official)** — Unity Manual/Scripting Reference, .NET docs, the vendor docs of anything already in the project. Pin every query and URL to the project's engine (`ProjectSettings/ProjectVersion.txt`) and .NET version; a page from another release can document an API this project lacks. Engine fully covers it → stop with `already covered in project`; partial coverage → state what it does and does not cover, then justify going to tier 2. A package for something the engine ships is maintenance for nothing.
5. **Tier 2 (repositories and the Asset Store)** — GitHub: filter with qualifiers, not free text: `pushed:>` a date within 12 months, `archived:false`, `language:C#`, and a star floor as a first cut only (`stars:>500` general .NET, `stars:>50` Unity-specific — the ecosystem is small). Read release history and whether issues against the current engine version get answers before listing; stars record past popularity. Unity packages: also check registry presence and version history at openupm.com. Asset Store: publisher, last update, Unity versions the page lists as supported, recent reviews, licence named on the page; paid → flag the price per seat or per title.
6. **Tier 3 (forums) only corroborates real-world caveats**, never the API contract. Quote one only with an accepted answer plus independent corroboration in another thread, and the thread date checked against the engine version.
7. **Record URL, tier and retrieval date as each candidate is found**; never write a URL you did not open.
8. **Stop at saturation** — three consecutive distinct queries returning only collected candidates; earlier hides the winner. **Hard cap 20 queries** → `STOPPED AT CAP`, naming what was not searched. Use the standard search mode; extended only when standard returns thin or stale results.
9. **Empty or single-item result is a finding** — name the tier that produced it.

## Never
- Widen the sweep into adjacent capabilities nobody asked about.
- Install, add or modify anything found; adoption needs an explicit GD request routed to the owning implementation role.

## Output
```
## Scouting Sweep — <capability, as behaviour>
- Searched as: <phrasing; assumption if ambiguous>
- Version pin: <engine and .NET version>
- Tier 1 (official): <coverage, or "no first-party coverage"> — <URL>, retrieved <date>
- Subject type: package/SDK / technique / hosted service
- Tier 2 (repositories): <name — stars, last release, archived y/n, licence file> — <URL>, retrieved <date>
- Tier 2 (Asset Store): <name — publisher, last update, supported Unity versions, price, licence> — <URL>, retrieved <date>
- Tier 3 (forums): <consensus, corroboration, thread date, or "no visible consensus"> — <URL>, retrieved <date>
- Sweep status: SATURATED / STOPPED AT CAP / STOPPED EARLY — <repeating queries, not searched, or why>
- Decision: <candidate set complete / no candidate exists / already covered in project>
- Routed to: <source-credibility-grading / practical-fit-screening / none>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its re-sweep trigger.

## Example
- "Everyone on Reddit says this asset is the standard" → declined as the primary answer: tier 3, two engine versions old, and the repository it points at is archived; tier 1 first, the claim kept only as a caveat if a live candidate corroborates it.
