---
name: csvhelper-csv-data
description: "CsvHelper for reading and writing delimited text: CsvReader/CsvWriter, GetRecords/WriteRecords, ClassMap, type converters, culture, IL2CPP/AOT caveats. Use when config or balance data lives in CSV/TSV."
user-invocable: false
---

# CsvHelper

Not for: binary save or wire formats (`memorypack-serialization`); JSON config (`System.Text.Json`); locating or loading the CSV asset (`unity-addressables`; this skill starts once a `TextReader`/`Stream` exists); authoring the resulting `SO_` asset (`gameplay-engineer`).
Docs: https://joshclose.github.io/CsvHelper/ — references written against 33.x; v34 (2026-10) reworked reader/writer options, so re-verify every reference before using v34.

| Reference | Read when |
|---|---|
| [reading.md](references/reading.md) | Choosing `GetRecords<T>` vs dynamic vs manual reading, streaming behaviour, or the file holds several tables or interleaved row types |
| [writing.md](references/writing.md) | Writing a new file, or appending rows to a file that has a header |
| [class-maps.md](references/class-maps.md) | The by-name convention does not fit, or choosing between `ClassMap<T>` and attributes |
| [type-conversion.md](references/type-conversion.md) | A field needs conversion the defaults do not give, or a `DataTable` consumer exists |

## Steps
1. **Pass an explicit `CultureInfo` to every `CsvReader`/`CsvWriter`** — `InvariantCulture` for machine-authored data. 33.x constructors require a `CultureInfo` or `CsvConfiguration`; passing `CurrentCulture` makes parsing vary per machine (breaks Shared Core determinism).
2. **Culture, header shape or target layer unstated → `Blocked` naming it, before writing** — each is invisible in the code and wrong only on another machine.
3. **Default to `GetRecords<T>()`/`WriteRecords()` with by-name headers** (writing and appending: [writing.md](references/writing.md)). Write a `ClassMap<T>` only when names diverge, the header is absent or duplicated, or a property needs ignore/constant/optional/validate/convert ([class-maps.md](references/class-maps.md)).
4. **Attributes for one simple stable mapping; `ClassMap<T>` when the type needs two mapping shapes or lives in `Game.Core.*`** (no CsvHelper reference on Core types).
5. **Open in this order, each declared inline in `using`**: `Stream` > `StreamReader`/`StreamWriter` (CsvHelper takes a `TextReader`/`TextWriter`, never a raw `Stream`) > `CsvReader`/`CsvWriter`. Disposal runs in reverse: `CsvReader`/`CsvWriter` first, stream last. Use `using` declarations or nested blocks, not manual `try/finally`. Never return the `GetRecords<T>()` sequence out of the `using` — it is deferred and enumerates a disposed reader.
6. **`foreach` over `GetRecords<T>()` for large files**; `.ToList()` only for small files or random access ([reading.md](references/reading.md)).
7. **Manual `ReadHeader()`/`Read()`/`GetField<T>()` when no class-per-row model fits** — also the AOT-safe path.
8. **Treat every parsed value as external input** (designer-edited): range-check via `.Validate()` or after parsing. A successful conversion is not validation.
9. **Verify `GetRecords<T>()` on a device build before shipping it in runtime code on IL2CPP/AOT** — its accessor generation is expression-tree based. Editor-only or build-time import (CSV to asset) avoids this and is the default for design data.
10. **Prefer built-in converters and `TypeConverterOptions` over a custom `ITypeConverter`**; register a custom one at the narrowest scope ([type-conversion.md](references/type-conversion.md)).

## Never
- Hold a record across loop iterations with `EnumerateRecords(record)` — it refills one instance per row; copy out the fields. `GetRecords<T>` yields a new object per row.
- Append to an existing CSV without `HasHeaderRecord = false` on that write (a second header lands mid-file).
- Register a custom converter globally when ClassMap or attribute scope would do.

## Output
```
## CsvHelper Work — <task>
- Direction: <GetRecords<T> / dynamic / by-hand — or WriteRecords / append>
- Culture: <CultureInfo passed explicitly>
- Disposal: <using chain confirmed>
- Mapping: <by-name / ClassMap<T> / attributes / by-hand> — why; entries used
- Multiple data sets or record types: <handling, or n/a>
- Custom conversion: <converter + scope, or built-ins sufficient>
- Boundary validation: <where parsed values are checked>
- AOT/IL2CPP: <confirmed on device, or "Editor/build-time only">
- Layer: <Game.Core.* / Game.Client.* / Editor-only>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Call `csv.GetRecords<Foo>()` with no `CultureInfo`, it is simpler" → declined: build machine, device and Editor can parse the same decimal differently; passed `CultureInfo.InvariantCulture`.
