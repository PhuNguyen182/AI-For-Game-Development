---
name: csvhelper-csv-data
description: >
  CsvHelper — reading and writing delimited text: `CsvReader`/`CsvWriter` over
  a `StreamReader`/`StreamWriter`, `GetRecords<T>()`/`WriteRecords()`, manual
  `ReadHeader()`/`Read()`/`GetField<T>()`, `ClassMap<T>`/`AutoMap()` with
  `.Name()`/`.Index()`/`.Ignore()`/`.Optional()`/`.Constant()`/`.Validate()`/
  `.TypeConverter<T>()`, the attribute equivalents (`[Name]`, `[Index]`,
  `[Optional]`, `[Constant]`, `[TypeConverter]`, `[CultureInfo]`,
  `[Delimiter]`), `CsvConfiguration` (`HasHeaderRecord`, `IgnoreBlankLines`,
  delimiter), custom `ITypeConverter`/`DefaultTypeConverter`,
  `TypeConverterOptions`, and `CsvDataReader`. Use for designer-authored
  tabular data — balance tables, drop tables, localization, item sheets —
  normally Editor tooling or a build-time step. Not for: binary save/wire
  formats (`memorypack-serialization`), JSON config (`System.Text.Json`),
  locating the CSV asset (`unity-addressables`), authoring the resulting `SO_`
  asset (`unity-engineer`).
---

# CsvHelper — CSV Import/Export

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Every upstream CsvHelper doc page this skill was built from, grouped by topic | Looking for a page no other reference covers, or adding a new upstream link |
| [prerequisites.md](references/prerequisites.md) | Disposal ordering, the `StreamReader`→`CsvReader` adapter chain, which `Stream` types work | Constructing or reviewing any reader/writer scope |
| [reading.md](references/reading.md) | `GetRecords<T>`/`dynamic`/anonymous, deferred-enumeration semantics, manual reading, multi-data-set and discriminator files | Reading anything, or the file's shape is not one class per row |
| [writing.md](references/writing.md) | `WriteRecords` header behaviour and the append pattern | Writing a new file, or adding rows to a file that already has a header |
| [class-maps.md](references/class-maps.md) | Every `ClassMap<T>` technique with worked syntax: name, alternate/duplicate names, index, `AutoMap` + override, ignore, constant, optional, convert, validate | The by-name convention does not fit and a map is being written |
| [attributes.md](references/attributes.md) | The attribute equivalents and `CsvConfiguration.FromAttributes<T>()`, plus the coupling they impose | Deciding between attributes and a `ClassMap<T>` |
| [type-conversion.md](references/type-conversion.md) | `TypeConverterOptions`, custom `ITypeConverter` and its three registration scopes, `CsvDataReader` | A field needs conversion the defaults do not give, or a `DataTable` consumer exists |

## 1. Objective
Move tabular design data between CSV text and typed C# objects correctly: the right `CsvReader`/`CsvWriter` construction (always with an explicit, deliberate `CultureInfo`), the right mapping technique for the actual header shape, and the right disposal and streaming discipline — without silently corrupting numeric or date data across locales, leaking file handles, or materializing a huge file into memory when streaming would do.

## 2. Role
Act as the CSV/tabular-data-import specialist for the client track — the tool reached for whenever a feature needs to read a designer-authored spreadsheet export into game data, or write one back out, whether in an Editor tool, a build-time pipeline script, or (less commonly) at runtime.

## 3. When to invoke this skill
- Importing a designer-authored CSV (balance table, drop table, item/ability sheet, localization strings) into strongly-typed C# records via `CsvReader.GetRecords<T>()`.
- Exporting C# objects to CSV via `CsvWriter.WriteRecords()`, including appending rows to a file that already has a header.
- Header names don't match property names, there's no header row, a header repeats, or a property needs a fallback name — any case needing a `ClassMap<T>` (`.Name()`/`.Index()`) or the equivalent attributes.
- A property has no CSV column (`.Ignore()`/`.Constant()`), or is absent from some file variants (`.Optional()`).
- A field needs conversion beyond the built-in converters (a JSON-in-a-cell column, a project-specific ID format) — a custom `ITypeConverter`/`DefaultTypeConverter`, or validation at parse time via `.Validate()`.
- One file holds several logical tables separated by blank lines, or interleaved row types distinguished by a discriminator column.
- Negative trigger: designing a binary wire or save format — that's `memorypack-serialization`.
- Negative trigger: a general JSON config or save format — use `System.Text.Json` or similar; CsvHelper only applies once the data is genuinely row-and-column shaped, not an arbitrary object graph.
- Negative trigger: locating or loading the CSV as a Unity asset (`TextAsset`, `Resources`, `StreamingAssets`, Addressables) — that's `unity-addressables` or plain file access; this skill starts once a `TextReader`/`Stream` exists.
- Negative trigger: authoring the `ScriptableObject` asset the parsed data ends up in — that's a separate Editor-tooling step owned by `unity-engineer`, following `naming-convention.md`'s `SO_` convention.

## 4. How to use this skill
1. **Always pass an explicit `CultureInfo` to `CsvReader`/`CsvWriter`** — `CultureInfo.InvariantCulture` for machine-authored data, or a specific culture only when the file's real number/date format demands it. An overload that falls back to the thread's culture makes parsing depend on the OS locale of whichever machine ran it, which is precisely the hidden platform divergence `coding-principles.md`'s Shared Core integrity section exists to prevent once this data reaches `Game.Core.*`.
2. **Default to `GetRecords<T>()`/`WriteRecords()` with the by-name convention** when headers already match property names, per [reading.md](references/reading.md) and [writing.md](references/writing.md) (the full upstream page index is [root-links.md](references/root-links.md)). Escalate to a `ClassMap<T>` (per [class-maps.md](references/class-maps.md)) only once names diverge, the header is absent or duplicated, or a property needs ignore/constant/optional/validate/convert behaviour — writing a map the default convention already satisfies is speculative complexity YAGNI forbids.
3. **Choose `ClassMap<T>` vs. attributes by how many mapping shapes the type needs**, per [attributes.md](references/attributes.md). Attributes suit one simple, stable mapping. A `ClassMap<T>` is required once the same type needs two shapes (two file variants), and is the only option when the model must not take a CsvHelper dependency at all — which is the case for any type living in `Game.Core.*`.
4. **Enumerate `GetRecords<T>()` with `foreach`, not `.ToList()`, for large files**, per [reading.md](references/reading.md) — it is a deferred, forward-only `IEnumerable<T>` reading one row at a time, and materializing it defeats that. Reserve `.ToList()` for files small enough to hold whole, or when the caller genuinely needs random access or multiple passes.
5. **Wrap every reader, writer, and stream in `using`**, per [prerequisites.md](references/prerequisites.md) and `coding-principles.md`'s Exception handling section — never a manual `try/finally` with explicit `Dispose()`, and never let a reader outlive the scope owning its stream.
6. **Reach for manual `ReadHeader()`/`Read()`/`GetField<T>()` when no class-per-row model fits**, per [reading.md](references/reading.md) — a heterogeneous file, a one-off inspection, or a case where configuring a map costs more than a short loop (KISS). This path also does no expression-tree codegen, which makes it the AOT-safe fallback in step 8.
7. **Treat every parsed value as external input at the point it is consumed**, per `coding-principles.md`'s Correctness boundaries section — a designer-edited spreadsheet is exactly the human-editable external data that rule names. Range-check via `.Validate()` on the map or an explicit check after parsing; a successful type conversion is not a successful validation.
8. **Verify AOT/IL2CPP compatibility on a device build before shipping `GetRecords<T>()` in runtime code**, per `performance-and-algorithms.md`'s Verification section. CsvHelper's member-accessor generation is expression-tree based, a known AOT risk category on iOS and console IL2CPP. Editor-only or build-time use (CSV → asset at import time, never in the player) sidesteps this entirely and is the default recommendation for design data.
9. **Prefer built-in converters and `TypeConverterOptions` over a custom `ITypeConverter`**, per [type-conversion.md](references/type-conversion.md) — write a converter only for a genuinely unsupported shape, and register it at the narrowest scope that solves the problem (ClassMap or attribute, never global unless every occurrence of that type process-wide needs it).
10. **If the file's culture, header shape, or target layer is unstated, ask before writing** — culture decides step 1, header shape decides steps 2–3, and layer decides step 8. Each is invisible in the resulting code and wrong in a way that only shows up on another machine.

## 5. Specific goals / tasks this skill performs
- Reading a designer-authored CSV into strongly-typed records, dynamic objects, or anonymous types.
- Writing a collection to a new CSV, or appending rows to an existing one without duplicating the header.
- Building a `ClassMap<T>` or attribute mapping for non-matching headers, index-based columns, alternate/duplicate names, ignored/constant/optional properties, or field validation.
- Writing and registering a custom `ITypeConverter`/`DefaultTypeConverter`, or tuning built-in converters via `TypeConverterOptions`.
- Handling a file with several logical data sets or interleaved row types via manual reading and a discriminator column.
- Bridging parsed data into a `DataTable` via `CsvDataReader`, only where an `IDataReader`-based consumer genuinely requires it.
- Out of scope: binary/wire serialization (`memorypack-serialization`); general JSON config (`System.Text.Json`); locating or loading the CSV asset (`unity-addressables`); authoring the resulting `ScriptableObject` (`unity-engineer`).

## 6. Output format
```
## CsvHelper Work — <import/export task name>
- Direction: <read: GetRecords<T> / dynamic / by-hand — or write: WriteRecords / append>
- Culture: <the CultureInfo passed explicitly> — never left to thread default
- Mapping technique: <by-name convention / ClassMap<T> / attributes / by-hand GetField> — rationale
- Class map specifics: <Name / Index / Ignore / Constant / Optional / Validate / TypeConverter entries, or "not needed">
- Multiple data sets or record types: <handling, or "not applicable">
- Custom type conversion: <converter name + registration scope, or "built-in converters sufficient">
- Rule compliance: <using/using-declaration on reader, writer, and stream, per Exception handling>
- Boundary validation: <where parsed values are checked, per Correctness boundaries>
- Verification: <AOT/IL2CPP confirmed on device — or "Editor/build-time only, not applicable">
- Layer: <Game.Core.* / Game.Client.* / Editor-only> — CsvHelper itself has no UnityEngine dependency
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions holding only under current conditions, thresholds not yet reached>
- Future remediation: <the concrete fix for each concern, each with its trigger condition>
```

## 7. Examples
**Example 1**
- Input: an Editor tool must import a designer's `ItemBalance.csv` (headers `Item Id`, `Base Damage`, `Rarity`) into `List<ItemBalanceRow>` for generating `SO_ItemBalance` assets.
- Output: `CsvReader` built with `CultureInfo.InvariantCulture`; a `ClassMap<ItemBalanceRow>` calling `AutoMap(CultureInfo.InvariantCulture)` then overriding the three mismatched headers with `.Name(...)`, per [class-maps.md](references/class-maps.md); read via `foreach` over `GetRecords<T>()` since the sheet grows; each `BaseDamage` range-checked right after parsing per Correctness boundaries; flagged Editor-only, so the AOT concern in step 8 does not apply.

**Example 2**
- Input: "just call `csv.GetRecords<Foo>()` with no `CultureInfo` argument, it's simpler."
- Output: declined — that overload falls back to the current thread's culture, so a build machine, a device, and an Editor session can parse the same decimal differently, and nothing reports it. Passed `CultureInfo.InvariantCulture` explicitly, per `coding-principles.md`'s Shared Core integrity requirement for data reaching `Game.Core.*`.

**Example 3**
- Input: a localization export tool must append newly translated rows to an existing `Localization.csv` without duplicating the header.
- Output: opened with `File.Open(path, FileMode.Append)`, built a `CsvConfiguration` with `HasHeaderRecord = false` for that write, and called `WriteRecords` for the new rows only — per [writing.md](references/writing.md), without that setting the header is rewritten at the append position, producing a header row in the middle of the data.

**Example 4**
- Input: a boss-drop-table CSV has a `LootJson` column holding a small embedded JSON array per row.
- Output: wrote `LootJsonConverter : DefaultTypeConverter` overriding `ConvertFromString`, registered on that one property via `Map(m => m.Loot).TypeConverter<LootJsonConverter>()` — ClassMap scope, not global, since only this sheet's column needs it, per [type-conversion.md](references/type-conversion.md).

## 8. Edge cases & guardrails
- Never construct `CsvReader`/`CsvWriter` without an explicit `CultureInfo` — the thread-culture fallback corrupts numbers and dates silently and per-machine.
- Never materialize `GetRecords<T>()` with `.ToList()` by habit on a large file — it is deferred by design, and the list holds every row at once.
- Never hold a reference to a record's backing row across loop iterations while streaming — the row state is reused internally; copy out the fields needed.
- Never write a `ClassMap` for a mapping the by-name convention already satisfies — that's speculative complexity YAGNI already forbids.
- Never trust a parsed value without a boundary check — a designer-edited spreadsheet is external human-editable input, not an internal contract.
- Never append to an existing CSV without `HasHeaderRecord = false` on that write — the header is duplicated mid-file.
- Never ship `GetRecords<T>()`/`AutoMap` in runtime code on an AOT/IL2CPP platform without a device-build check — expression-tree accessor generation is a known AOT risk; default to Editor/build-time use and fall back to manual `GetField<T>()`.
- Never register a custom `ITypeConverter` globally where ClassMap or attribute scope would do — a global converter changes every other map in the process, including ones this change never meant to touch.
- If culture, header shape, or target layer is unstated, ask — each independently decides a different §6 field and none is recoverable from the code afterwards.
