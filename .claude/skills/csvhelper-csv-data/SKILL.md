---
name: csvhelper-csv-data
description: "CsvHelper: CsvReader/CsvWriter, GetRecords, ClassMap, converters, IL2CPP. Use when config or balance data is CSV/TSV."
user-invocable: false
---

# CsvHelper

- **Not for:** binary save or wire formats (`memorypack-serialization`).
- **Not for:** JSON config (`System.Text.Json`).
- **Not for:** locating or loading the CSV asset (`unity-addressables`); this skill starts once a `TextReader`/`Stream` exists.
- **Not for:** authoring the resulting `SO_` asset (`gameplay-engineer`).
- **Docs:** https://joshclose.github.io/CsvHelper/ — references written against 33.x.
  - **Version caveat:** v34 (2026-10) reworked reader/writer options, so re-verify every reference before using v34.

## References
- **[reading.md](references/reading.md):** Choosing `GetRecords<T>` vs dynamic vs manual reading, streaming behaviour, or the file holds several tables or interleaved row types.
- **[writing.md](references/writing.md):** Writing a new file, or appending rows to a file that has a header.
- **[class-maps.md](references/class-maps.md):** The by-name convention does not fit, or choosing between `ClassMap<T>` and attributes.
- **[type-conversion.md](references/type-conversion.md):** A field needs conversion the defaults do not give, or a `DataTable` consumer exists.

## Steps
1. **Pass an explicit `CultureInfo` to every `CsvReader`/`CsvWriter`:** `InvariantCulture` for machine-authored data.
   - **33.x constructors:** require a `CultureInfo` or `CsvConfiguration`.
   - **`CurrentCulture`:** passing it makes parsing vary per machine (breaks Shared Core determinism).
2. **Culture, header shape or target layer unstated → `Blocked` naming it, before writing:** each of the three is invisible in the code and wrong only on another machine.
3. **Default to `GetRecords<T>()`/`WriteRecords()` with by-name headers:** writing and appending per [writing.md](references/writing.md).
   - **`ClassMap<T>`:** only when names diverge, the header is absent or duplicated, or a property needs ignore/constant/optional/validate/convert ([class-maps.md](references/class-maps.md)).
4. **Attributes for one simple stable mapping; `ClassMap<T>` when the type needs two mapping shapes or lives in a Core assembly:** no CsvHelper reference on Core types.
5. **Open in this order, each declared inline in `using`:** `Stream` > `StreamReader`/`StreamWriter` > `CsvReader`/`CsvWriter`.
   - **Stream layer:** CsvHelper takes a `TextReader`/`TextWriter`, never a raw `Stream`.
   - **Disposal:** runs in reverse: `CsvReader`/`CsvWriter` first, stream last.
   - **Syntax:** `using` declarations or nested blocks, not manual `try/finally`.
   - **Returning the sequence:** never return the `GetRecords<T>()` sequence out of the `using` — it is deferred and enumerates a disposed reader.
6. **`foreach` over `GetRecords<T>()` for large files:** `.ToList()` only for small files or random access ([reading.md](references/reading.md)).
7. **Manual `ReadHeader()`/`Read()`/`GetField<T>()` when no class-per-row model fits:** also the AOT-safe path.
8. **Treat every parsed value as external input (designer-edited):** range-check via `.Validate()` or after parsing.
   - **Conversion:** a successful conversion is not validation.
9. **Verify `GetRecords<T>()` on a device build before shipping it in runtime code on IL2CPP/AOT:** its accessor generation is expression-tree based.
   - **Default for design data:** Editor-only or build-time import (CSV to asset) avoids this.
10. **Prefer built-in converters and `TypeConverterOptions` over a custom `ITypeConverter`:** register a custom one at the narrowest scope ([type-conversion.md](references/type-conversion.md)).

## Never
- **Holding a record across iterations:** with `EnumerateRecords(record)` — it refills one instance per row; copy out the fields. `GetRecords<T>` yields a new object per row.
- **Appending without `HasHeaderRecord = false`:** appending to an existing CSV without it on that write — a second header lands mid-file.
- **Global custom converter:** registering one globally when ClassMap or attribute scope would do.

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
- Layer: <Core / Client / Editor-only>
```

## Example
- **"Call `csv.GetRecords<Foo>()` with no `CultureInfo`, it is simpler":** declined — build machine, device and Editor can parse the same decimal differently.
  - **Done instead:** passed `CultureInfo.InvariantCulture`.
