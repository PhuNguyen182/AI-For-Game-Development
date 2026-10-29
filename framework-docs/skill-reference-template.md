# <Topic — the API surface or procedure area this file holds>

Sources: [a] <url or path below the SKILL.md `Docs:` base>, [b] <...>. <Or: "Synthesized from <what>.">

<Optional: one sentence, only if it carries a fact a reader needs before the tables.>

## <Group, in the order a reader arrives at the decision>

| Subject | Fact that decides |
|---|---|
| `<exact type / member / setting / command>` | <threshold with unit, failure mode and its trigger, constraint the name does not imply> [a] |

```csharp
// Only where the shape is the point; one snippet per pattern; compiles as written.
```

**Caveat:** <silent-failure mode, ordering constraint, platform limit>.

Unverified: <claims not confirmed against the source, if any>.

<!--
=====================================================================
Reference authoring rules (not shipped)
=====================================================================
A reference loads only when SKILL.md's trigger fires, but then loads whole.
Every row must settle something the procedure needs.

Keep
- Facts the SKILL.md steps rely on: API surface, defaults and thresholds with
  units, version-specific behaviour, gotchas, worked syntax whose shape matters.

Cut
- Procedure, steps or output formats. SKILL.md owns those.
- Anything SKILL.md, a sibling reference or another skill already states.
  Point to it by file or skill name.
- Knowledge a strong model already has. Vendor prose copied word for word.
- Table of contents, "API index" tables, `Covers:` lines, orientation that
  restates the heading.
- A Source column on every row. List sources once in the header with short
  keys; cite a key only on a row whose claim is version-specific or surprising.
- Notes about how the file was made. Unconfirmed claims go in one `Unverified:` line.

Shape
- No frontmatter. One H1. kebab-case filename named for the topic.
- Tables where content enumerates; prose only for one-line orientation, code,
  `**Caveat:**` lines.
- A doc base URL and version pin live in SKILL.md's `Docs:` line, so the
  header lists paths below that base, not full repeated URLs.
- ~250 lines max; past that, split by topic.
- Portability as in skill-template.md.
=====================================================================
-->
