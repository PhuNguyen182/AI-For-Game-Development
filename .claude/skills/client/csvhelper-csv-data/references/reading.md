# Reading CSV Data — GetRecords, Manual Reading & Multi-Shape Files

Sources: [Reading](https://joshclose.github.io/CsvHelper/examples/reading/), [Get Class Records](https://joshclose.github.io/CsvHelper/examples/reading/get-class-records/), [Get Dynamic Records](https://joshclose.github.io/CsvHelper/examples/reading/get-dynamic-records/), [Get Anonymous Type Records](https://joshclose.github.io/CsvHelper/examples/reading/get-anonymous-type-records/), [Enumerate Class Records](https://joshclose.github.io/CsvHelper/examples/reading/enumerate-class-records/), [Reading by Hand](https://joshclose.github.io/CsvHelper/examples/reading/reading-by-hand/), [Reading Multiple Data Sets](https://joshclose.github.io/CsvHelper/examples/reading/reading-multiple-data-sets/), [Reading Multiple Record Types](https://joshclose.github.io/CsvHelper/examples/reading/reading-multiple-record-types/).
Covers: SKILL.md §4 — **"Default to `GetRecords<T>()`/`WriteRecords()` with the by-name convention"**, **"Enumerate `GetRecords<T>()` with `foreach`, not `.ToList()`, for large files"**, **"Reach for manual `ReadHeader()`/`Read()`/`GetField<T>()` when no class-per-row model fits"**.

Every way to get rows out of a file, and the enumeration semantics that decide
memory behaviour. Mapping the columns once the shape is chosen is
[class-maps.md](class-maps.md); the disposal scope every snippet here assumes
is [prerequisites.md](prerequisites.md).

## Contents

- [Reading strategies](#reading-strategies)
- [Enumeration semantics](#enumeration-semantics)
- [Manual reading](#manual-reading)
- [Files holding more than one shape](#files-holding-more-than-one-shape)

## Reading strategies

| Strategy | Effect | Use when | Source |
|---|---|---|---|
| `GetRecords<T>()` | Deferred sequence of typed records; headers match property names by default convention | The file is one class per row and headers agree with the model | [Get Class Records](https://joshclose.github.io/CsvHelper/examples/reading/get-class-records/) |
| `GetRecords<dynamic>()` | Every property comes back a `string` — there is no target type to convert into | A quick inspection or straight passthrough, nothing more | [Get Dynamic Records](https://joshclose.github.io/CsvHelper/examples/reading/get-dynamic-records/) |
| `GetRecords<T>()` with an anonymous witness | Projects into an anonymous shape passed as the type witness | A one-off read that does not warrant a named class | [Get Anonymous Type Records](https://joshclose.github.io/CsvHelper/examples/reading/get-anonymous-type-records/) |
| `ReadHeader()`/`Read()`/`GetField<T>()` | Row-by-row control, no mapping configuration, no expression-tree codegen | No class-per-row model fits, or an AOT-safe path is required | [Reading by Hand](https://joshclose.github.io/CsvHelper/examples/reading/reading-by-hand/) |

```csharp
using (var reader = new StreamReader("path/to/ItemBalance.csv"))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
{
    foreach (var record in csv.GetRecords<ItemBalanceRow>())
    {
        this.Apply(record);
    }
}
```

## Enumeration semantics

| Property | What it decides | Source |
|---|---|---|
| Deferred and forward-only | `GetRecords<T>()` yields one row at a time and never buffers the file | [Enumerate Class Records](https://joshclose.github.io/CsvHelper/examples/reading/enumerate-class-records/) |
| `foreach` is the low-memory choice | Each row is discarded as the loop moves past it | [Enumerate Class Records](https://joshclose.github.io/CsvHelper/examples/reading/enumerate-class-records/) |
| `.ToList()` holds everything | Justified only by a small file, or a caller needing random access or multiple passes | [Enumerate Class Records](https://joshclose.github.io/CsvHelper/examples/reading/enumerate-class-records/) |
| The current row is reused internally | Keeping a reference past its iteration reads whatever the next row overwrote | [Enumerate Class Records](https://joshclose.github.io/CsvHelper/examples/reading/enumerate-class-records/) |

**Critical caveat**: copy out the fields needed rather than storing the record
object itself when anything survives the loop iteration. The stale read is
silent — no exception, just the wrong row's values.

## Manual reading

| Call | Effect | Source |
|---|---|---|
| `csv.ReadHeader()` | Consumes the header row so later `GetField` calls can address columns by name | [Reading by Hand](https://joshclose.github.io/CsvHelper/examples/reading/reading-by-hand/) |
| `csv.Read()` | Advances one row; returns `false` at end of file — this is the loop condition, not a count | [Reading by Hand](https://joshclose.github.io/CsvHelper/examples/reading/reading-by-hand/) |
| `csv.GetField<T>(name)` | Returns the converted value | [Reading by Hand](https://joshclose.github.io/CsvHelper/examples/reading/reading-by-hand/) |
| `csv.GetField(name)` | Returns the raw `string`, unconverted | [Reading by Hand](https://joshclose.github.io/CsvHelper/examples/reading/reading-by-hand/) |

```csharp
csv.Read();
csv.ReadHeader();
while (csv.Read())
{
    var record = new ItemBalanceRow
    {
        Id = csv.GetField<int>("Item Id"),
        Name = csv.GetField("Name"),
    };
    records.Add(record);
}
```

## Files holding more than one shape

| Shape | How it is handled | Source |
|---|---|---|
| Several tables separated by blank lines | Set `IgnoreBlankLines = false` so the separator survives, then read manually: on a blank line call `ReadHeader()` again and inspect the new first column name to pick the next `ClassMap`/type | [Reading Multiple Data Sets](https://joshclose.github.io/CsvHelper/examples/reading/reading-multiple-data-sets/) |
| Interleaved rows of different types | Set `HasHeaderRecord = false`, register an index-based `ClassMap` per type, and `switch` on the first field as a discriminator, calling `csv.GetRecord<T>()` in the matching arm | [Reading Multiple Record Types](https://joshclose.github.io/CsvHelper/examples/reading/reading-multiple-record-types/) |

**Critical caveat**: `IgnoreBlankLines` defaults to skipping blank lines. Left
alone, a multi-data-set file reads as one continuous table and the section
boundary vanishes without error.
