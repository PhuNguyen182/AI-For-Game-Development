---
name: csvhelper-csv-data
description: >
  Technique for reading and writing CSV (and other delimited-text) data with
  the CsvHelper library — `CsvReader`/`CsvWriter` over a `StreamReader`/
  `StreamWriter`, `GetRecords<T>()`/`WriteRecords()` for strongly-typed
  (or `dynamic`/anonymous) records, manual row-by-hand reading via
  `ReadHeader()`/`Read()`/`GetField<T>()`, `ClassMap<T>`/`AutoMap()` with
  `.Name()`/`.Index()`/`.Ignore()`/`.Optional()`/`.Constant()`/`.Validate()`/
  `.TypeConverter<T>()` mapping, the attribute-based equivalent
  (`[Name]`/`[Index]`/`[Ignore]`/`[Optional]`/`[Constant]`/`[TypeConverter]`/
  `[CultureInfo]`/`[Delimiter]`), `CsvConfiguration` (culture,
  `HasHeaderRecord`, delimiter, `IgnoreBlankLines`), custom `ITypeConverter`/
  `DefaultTypeConverter` implementations and `TypeConverterOptions`, and
  `CsvDataReader` for `DataTable` interop. Use this for importing/exporting
  tabular design data (game-balance tables, drop tables, localization
  strings, item/ability definition sheets) that a designer authors in
  Excel/Google Sheets and exports as CSV — almost always Editor-tooling or a
  build-time data pipeline step, not player-facing runtime code. CsvHelper
  itself has no `UnityEngine` dependency, so the pure parsing/mapping logic
  is safe to call from `Game.Core.*` or an Editor script alike; only the
  decision of *where the file/stream comes from* (a Unity asset path,
  `TextAsset`, `StreamingAssets`) is Unity-specific. Do not use this for
  binary/wire serialization (save snapshots, network DTOs, rollback state)
  — that's `memorypack-serialization`; CsvHelper is a human-readable
  tabular-text format, not a compact binary one. Do not use this for a
  general JSON config/save format — use `System.Text.Json` or similar for
  that; CsvHelper only applies once the source data is genuinely
  spreadsheet-shaped (rows and columns), not an arbitrary object graph. Do
  not use this to decide how the raw CSV file is located/loaded as a Unity
  asset (`TextAsset`, `Resources`, `StreamingAssets`, an Addressable) — that
  loading/reference-counting contract is `unity-addressables`'s territory or
  plain Editor `AssetDatabase`/`File` access; this skill only covers what
  happens once a `TextReader`/`Stream` is already in hand. Do not use this
  to author the resulting `ScriptableObject` config asset itself once rows
  are parsed — converting parsed CSV rows into `SO_`-named ScriptableObject
  data (per `naming-convention.md`) is a separate Editor-tooling step this
  skill hands off to, not something it produces directly.
---

# CsvHelper — CSV Import/Export

Sources: see [references/](references/) for the specific sub-pages this skill was built from, split by topic — [root-links.md](references/root-links.md), [prerequisites.md](references/prerequisites.md) (disposal, file/stream basics), [reading.md](references/reading.md) (`GetRecords<T>`, dynamic/anonymous records, manual reading-by-hand, multiple data sets, multiple record types), [writing.md](references/writing.md) (`WriteRecords`, appending to an existing file), [class-maps.md](references/class-maps.md) (`ClassMap<T>`, name/index/alternate-name/duplicate-name mapping, `AutoMap`, ignore/constant/optional, validation, inline conversion), [attributes.md](references/attributes.md) (the attribute-based equivalent of class maps), [type-conversion.md](references/type-conversion.md) (`TypeConverterOptions`, custom `ITypeConverter`, `CsvDataReader`).

## 1. Objective
Move tabular design data between CSV text and typed C# objects correctly: the right `CsvReader`/`CsvWriter` construction (always with an explicit, deliberate `CultureInfo`), the right mapping technique for the actual header shape (by-name convention, `ClassMap`, attributes, or manual `GetField`), and the right disposal/streaming discipline — without silently corrupting numeric/date data across locales, leaking file handles, or materializing a huge file into memory when streaming would do.

## 2. Role
Act as the CSV/tabular-data-import specialist for the client track — the tool reached for whenever a feature needs to read a designer-authored spreadsheet export into game data, or write one back out, whether that happens in an Editor tool, a build-time pipeline script, or (less commonly) at runtime.

## 3. When to invoke this skill
- Importing a designer-authored CSV (balance table, drop table, item/ability sheet, localization strings) into strongly-typed C# records via `CsvReader.GetRecords<T>()`.
- Exporting C# objects/collections to a CSV file via `CsvWriter.WriteRecords()`, including appending new rows to a file that already has a header.
- The CSV header names don't match the target class's property names, there's no header row at all, a header repeats, or a property needs a fallback/alternate header name — any case needing a `ClassMap<T>` (`.Name()`/`.Index()`) or the equivalent attributes.
- A property has no CSV column (computed, or a fixed value) — `.Ignore()`/`.Constant()`, or a property that's absent in some file variants — `.Optional()`.
- A field needs conversion beyond what the built-in converters do (a JSON-in-a-cell column, a project-specific enum/ID format) — a custom `ITypeConverter`/`DefaultTypeConverter`, registered globally, via attribute, or via `ClassMap`.
- A field needs validation against a business rule at parse time (e.g. reject a malformed identifier) — `.Validate()`.
- A single file contains more than one logical table (multiple data sets separated by blank lines) or interleaved row types distinguished by a discriminator column.
- Negative trigger: designing a binary wire/save format — that's `memorypack-serialization`.
- Negative trigger: a general JSON config/save format — use `System.Text.Json`/similar instead.
- Negative trigger: deciding how the CSV file itself is located or loaded as a Unity asset (`TextAsset`, `Resources`, `StreamingAssets`, Addressables) — that's `unity-addressables`/plain file access; this skill starts once a `TextReader`/`Stream` exists.
- Negative trigger: building the `ScriptableObject` asset the parsed data ends up in — that's a separate Editor-tooling step following `naming-convention.md`'s `SO_` convention.

## 4. How to use this skill
1. **Always pass an explicit `CultureInfo` to `CsvReader`/`CsvWriter`** — `CultureInfo.InvariantCulture` for machine-authored/round-tripped data, or a specific deliberate culture only when the file's actual number/date format requires it. Never omit it or rely on a constructor overload that falls back to the current thread's culture: a build machine, a player's device, and an Editor session can all have different OS-level locales (e.g. comma vs. period as the decimal separator), and locale-dependent parsing is exactly the kind of hidden platform divergence `coding-principles.md`'s Shared Core determinism rule exists to prevent when this data feeds into `Game.Core.*` state.
2. **Default to `GetRecords<T>()`/`WriteRecords()` with by-name convention** when the CSV headers already match the class's property names — per [reading.md](references/reading.md)/[writing.md](references/writing.md). Reach for a `ClassMap<T>` (per [class-maps.md](references/class-maps.md)) only once the header names diverge, the file has no header, a header repeats, or a property needs ignore/constant/optional/validate/custom-conversion behavior — don't hand-roll a `ClassMap` for a mapping the default convention already satisfies (YAGNI).
3. **Choose `ClassMap<T>` vs. attributes deliberately, per [attributes.md](references/attributes.md).** Attributes are fine for a simple, single, stable mapping directly on the model class; use a `ClassMap<T>` instead once the same type needs more than one mapping shape (two file variants with different headers), or when the model type shouldn't carry a CsvHelper package dependency at all — relevant if that type is meant to live in `Game.Core.*`, since Shared Core code should depend on as little external surface as strictly needed.
4. **Enumerate `GetRecords<T>()` with `foreach`, not `.ToList()`, for large files.** It returns a deferred, forward-round-trip `IEnumerable<T>` that reads one row at a time — materializing the whole sequence into a list defeats that and holds the entire dataset in memory at once. Reserve `.ToList()` for files small enough that holding the full set is genuinely fine, or when the calling code needs random access/multiple passes.
5. **Wrap every `StreamReader`/`StreamWriter`/`CsvReader`/`CsvWriter` in `using` (or a C# 8+ `using` declaration)**, per [prerequisites.md](references/prerequisites.md) and `coding-principles.md`'s Exception handling section — never a manual `try/finally` with explicit `Dispose()` calls, and never let a reader/writer outlive the scope that owns its underlying stream.
6. **Reach for manual reading-by-hand (`ReadHeader()`/`Read()`/`GetField<T>()`, per [reading.md](references/reading.md)) instead of forcing an awkward `ClassMap`** when the target shape genuinely doesn't fit a class-per-row model — a heterogeneous file, a one-off inspection, or a case where configuring a map would cost more than a short manual loop (KISS).
7. **Treat every parsed value as external input at the point it's consumed**, per `coding-principles.md`'s Correctness boundaries section — a designer-edited spreadsheet is exactly the kind of external, human-editable data that rule calls out; validate ranges/required fields (via `.Validate()` on the map, or an explicit check right after parsing) rather than trusting the CSV blindly because the type conversion succeeded.
8. **Verify AOT/IL2CPP compatibility on an actual device build before depending on `GetRecords<T>()`/`ClassMap` auto-mapping in shipped runtime code** (as opposed to Editor-only tooling). CsvHelper's automatic member-accessor generation is Expression-Tree-based; Expression-Tree compilation has historically been a source of AOT (iOS/console IL2CPP) incompatibilities in .NET libraries generally. Editor-only/build-pipeline usage (converting CSV into a ScriptableObject/asset at import time, never touching the shipped player) sidesteps this entirely and is the default recommendation for design data — reserve any runtime `GetRecords<T>()` call for after this has actually been confirmed on-device, and prefer the manual `GetField<T>()` path (which does no expression-tree codegen) as an AOT-safe fallback if it hasn't.
9. **Prefer the built-in type converters and `TypeConverterOptions`** (per [type-conversion.md](references/type-conversion.md)) over a custom `ITypeConverter` whenever an option (date style, number style, boolean literal set) already covers the need — write a custom converter only for a genuinely unsupported shape (e.g. a JSON-in-a-cell column), and register it at the narrowest scope that solves the problem (ClassMap or attribute, not global, unless every occurrence of that type across the whole process genuinely needs the same conversion).

## 5. Specific goals / tasks this skill performs
- Reading a designer-authored CSV into strongly-typed records (`GetRecords<T>()`), dynamic objects, or anonymous types.
- Writing a collection of C# objects to a new CSV file, or appending rows to an existing one without duplicating the header.
- Building a `ClassMap<T>` (or attribute-based mapping) for non-matching headers, index-based columns, alternate/duplicate header names, ignored/constant/optional properties, or field validation.
- Writing and registering a custom `ITypeConverter`/`DefaultTypeConverter`, or tuning built-in converters via `TypeConverterOptions`.
- Handling a file with multiple logical data sets or interleaved row types via manual reading and a discriminator column.
- Bridging parsed CSV data into a `DataTable` via `CsvDataReader`, only when a `DataTable`/`IDataReader`-based consumer genuinely requires it.
- Out of scope: binary/wire serialization (`memorypack-serialization`), general JSON config (`System.Text.Json`), locating/loading the CSV asset itself (`unity-addressables`/file access), authoring the resulting `ScriptableObject` asset.

## 6. Output format
```
## CsvHelper Work — <import/export task name>
- Direction: read (GetRecords<T> / dynamic / by-hand) — or write (WriteRecords / append)
- Culture: <CultureInfo passed explicitly> — never left to thread-default
- Mapping technique: <by-name convention / ClassMap<T> / attributes / by-hand GetField> — rationale
- Class map specifics: <Name/Index/Ignore/Constant/Optional/Validate/TypeConverter entries, or "not needed">
- Multiple data sets / record types: <handling, or "not applicable">
- Custom type conversion: <ITypeConverter name + registration scope, or "built-in converters sufficient">
- Disposal: using/using-declaration confirmed for reader/writer and underlying stream
- Boundary validation: <where parsed values are checked, per Correctness boundaries>
- Runtime vs. Editor-only: <Editor/build-tooling only — or confirmed AOT-safe for shipped runtime use>
- Layer: <Game.Core.* / Game.Client.* / Editor-only tool> — CsvHelper itself has no UnityEngine dependency
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: an Editor tool needs to import a designer's `ItemBalance.csv` (headers: `Item Id`, `Base Damage`, `Rarity`) into a `List<ItemBalanceRow>` for generating `SO_ItemBalance` ScriptableObject assets.
- Output: `CsvReader` constructed with `CultureInfo.InvariantCulture`; a `FooMap : ClassMap<ItemBalanceRow>` calling `AutoMap(CultureInfo.InvariantCulture)` then overriding the three mismatched headers with `.Name("Item Id")`/`.Name("Base Damage")`/`.Name("Rarity")`; read via `foreach` over `GetRecords<ItemBalanceRow>()` (not `.ToList()`, since the sheet can grow); each row's `BaseDamage` range-checked against design bounds right after parsing per Correctness boundaries, before being handed to the (separate) ScriptableObject-generation step; flagged as Editor-only, so the AOT/IL2CPP concern doesn't apply.

**Example 2**
- Input: "just call `csv.GetRecords<Foo>()` with no CultureInfo argument, it's simpler."
- Output: declined — an overload without an explicit `CultureInfo` falls back to the current thread's culture, which differs across build machines/devices/Editor sessions; passed `CultureInfo.InvariantCulture` explicitly instead, consistent with `coding-principles.md`'s Shared Core determinism requirement for any data that ends up feeding `Game.Core.*` state.

**Example 3**
- Input: a localization export tool needs to append newly-translated rows to an existing `Localization.csv` without duplicating the header.
- Output: opened the file with `File.Open(path, FileMode.Append)`, built a `CsvConfiguration` with `HasHeaderRecord = false` for the append write, and called `WriteRecords` for just the new rows — confirmed the existing header wasn't rewritten by inspecting the resulting file per [writing.md](references/writing.md)'s appending example.

**Example 4**
- Input: "a boss-drop-table CSV has a `LootJson` column containing a small embedded JSON array per row."
- Output: wrote a `LootJsonConverter : DefaultTypeConverter` overriding `ConvertFromString` to deserialize that column via `JsonSerializer.Deserialize<LootEntry[]>`, registered it on the specific property via `Map(m => m.Loot).TypeConverter<LootJsonConverter>()` (ClassMap scope, not global) since only this one sheet's column needs it.

## 8. Edge cases & guardrails
- Never construct `CsvReader`/`CsvWriter` without an explicit `CultureInfo` — the thread-culture fallback risks silent, platform/device-dependent numeric or date corruption, and breaks Shared Core determinism if the parsed data reaches `Game.Core.*`.
- Never materialize `GetRecords<T>()` with `.ToList()` as a default habit on a large file — it's a deferred `IEnumerable<T>` by design; enumerate with `foreach` unless the full set is genuinely needed at once.
- Never hold a reference to a record/row object across loop iterations while streaming `GetRecords<T>()` — the underlying row state can be reused internally; copy out the fields actually needed.
- Never write a `ClassMap` for a mapping the default by-name convention already satisfies — that's speculative complexity YAGNI already forbids.
- Never trust a parsed CSV value without a boundary check — a designer-edited spreadsheet is external, human-editable input per `coding-principles.md`'s Correctness boundaries section, not an internal contract that can't fail.
- Never append to an existing CSV without setting `HasHeaderRecord = false` on that write — the header gets duplicated mid-file otherwise.
- Never assume `GetRecords<T>()`/`ClassMap` auto-mapping is safe in shipped runtime code on an AOT/IL2CPP platform without verifying on an actual device build first — its accessor generation is Expression-Tree-based, a known category of AOT risk; default to Editor/build-time-only usage for design data, and fall back to manual `GetField<T>()` reading if runtime use is required and AOT compatibility hasn't been confirmed.
- Never register a custom `ITypeConverter` globally when a `ClassMap`/attribute-scoped registration would do — a global converter silently changes behavior for every other map in the same process, including ones this change wasn't meant to touch.
- Never use CsvHelper for a binary wire/save format or a general JSON config need — those are `memorypack-serialization`'s and `System.Text.Json`'s territory respectively; CsvHelper is for genuinely tabular, human-authored data.
