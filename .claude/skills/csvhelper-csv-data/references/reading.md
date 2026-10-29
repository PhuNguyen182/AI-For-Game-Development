# Reading CSV

Docs: https://joshclose.github.io/CsvHelper/examples/reading/ (get-class-records, get-dynamic-records, get-anonymous-type-records, enumerate-class-records, reading-by-hand, reading-multiple-data-sets, reading-multiple-record-types).

## Strategies
| Strategy | Notes |
|---|---|
| `GetRecords<T>()` | Deferred typed records; headers match property names by default |
| `GetRecords<dynamic>()` | Every property is a `string` (no target type); inspection only |
| `GetRecords(anonymousWitness)` | Projects into an anonymous shape for a one-off read |
| `ReadHeader()`/`Read()`/`GetField<T>(name)` | Row-by-row, no mapping, no expression-tree codegen (AOT-safe) |

```csharp
using (var reader = new StreamReader(path))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
{
    foreach (var record in csv.GetRecords<ItemBalanceRow>())
        Apply(record);
}
```

## Enumeration
- `GetRecords<T>()` is deferred and forward-only; it never buffers the file. `.ToList()` holds every row.
- `GetRecords<T>()` creates a new object per row. `EnumerateRecords(record)` refills the one instance you pass (zero-allocation): keeping a reference past its iteration silently reads the next row's values.

## Manual reading
- `csv.ReadHeader()` consumes the header so `GetField` can address by name; `csv.Read()` advances and returns `false` at end of file; `GetField<T>(name)` converts, `GetField(name)` returns the raw string.
```csharp
csv.Read();
csv.ReadHeader();
while (csv.Read())
    records.Add(new ItemBalanceRow { Id = csv.GetField<int>("Item Id"), Name = csv.GetField("Name") });
```

## Files with more than one shape
- Several tables separated by blank lines: set `IgnoreBlankLines = false` (default skips them, so the boundary vanishes without error), read manually, and on a blank line call `ReadHeader()` again and pick the next type/`ClassMap` from the new first column name.
- Interleaved row types: set `HasHeaderRecord = false`, register an index-based `ClassMap` per type, `switch` on the first field, and call `csv.GetRecord<T>()` in the matching arm.
