# Reading CSV Data

Source: [reading](https://joshclose.github.io/CsvHelper/examples/reading/), [get-class-records](https://joshclose.github.io/CsvHelper/examples/reading/get-class-records/), [get-dynamic-records](https://joshclose.github.io/CsvHelper/examples/reading/get-dynamic-records/), [get-anonymous-type-records](https://joshclose.github.io/CsvHelper/examples/reading/get-anonymous-type-records/), [enumerate-class-records](https://joshclose.github.io/CsvHelper/examples/reading/enumerate-class-records/), [reading-by-hand](https://joshclose.github.io/CsvHelper/examples/reading/reading-by-hand/), [reading-multiple-data-sets](https://joshclose.github.io/CsvHelper/examples/reading/reading-multiple-data-sets/), [reading-multiple-record-types](https://joshclose.github.io/CsvHelper/examples/reading/reading-multiple-record-types/).

## GetRecords\<T\>() — strongly-typed records

```csharp
using (var reader = new StreamReader("path\\to\\file.csv"))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
{
    var records = csv.GetRecords<Foo>();
}

public class Foo
{
    public int Id { get; set; }
    public string Name { get; set; }
}
```

Column headers (`Id`, `Name`) match property names by default convention — no explicit mapping needed when the CSV header and the class's property names already agree.

`GetRecords<T>()` returns a **deferred, forward-only `IEnumerable<T>`** — it reads and yields one row at a time as the sequence is enumerated, it does not buffer the whole file in memory. Enumerate it with `foreach` (or `.ToList()` only when the full set genuinely needs to be materialized) — per [enumerate-class-records], iterating with `foreach` instead of `ToList()` is the low-memory choice for large files, since each row is discarded as soon as the loop moves past it. The one row currently being read is reused/overwritten internally — do not hold onto a reference to a record's backing row object outside the loop iteration that produced it; copy out the fields you need.

## GetRecords\<dynamic\>() — no class needed

```csharp
using (var reader = new StreamReader("path\\to\\file.csv"))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
{
    var records = csv.GetRecords<dynamic>();
}
```

Every property on the resulting `dynamic` object is a `string` — CsvHelper has no target type to convert into. Use this only for a quick inspection/passthrough case; reach for a typed class (with its own type conversion) as soon as the data needs anything other than raw text.

## Anonymous types

`GetRecords<T>()` also supports projecting into an anonymous type by passing an instance of the anonymous shape as the type witness, for a one-off read that doesn't warrant a named class.

## Reading by hand

For cases where "it's easier to not try and configure a mapping to match your class definition," read row-by-row manually instead of `GetRecords<T>()`:

```csharp
using (var reader = new StreamReader("path\\to\\file.csv"))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
{
    csv.ReadHeader();
    while (csv.Read())
    {
        var record = new Foo
        {
            Id = csv.GetField<int>("Id"),
            Name = csv.GetField("Name"),
        };
        records.Add(record);
    }
}
```

- `csv.ReadHeader()` consumes the header row and lets subsequent `GetField` calls address columns by name.
- `csv.Read()` advances to the next row; returns `false` at end-of-file — this is the loop condition, not a count.
- `csv.GetField<T>(name)` returns a converted value; `csv.GetField(name)` (no type parameter) returns the raw `string`.

## Reading multiple data sets in one file

Some CSV files contain more than one table separated by a blank line (e.g. a "Foo" section, then a blank line, then a "Bar" section). Handle this by:
1. Setting `IgnoreBlankLines = false` in `CsvConfiguration` so the blank-line separator survives instead of being silently skipped.
2. Reading manually: detect a blank line (end of the current section), call `csv.ReadHeader()` again to pick up the next section's header, and inspect the new header's first column name to decide which registered `ClassMap`/type applies next.
3. Registering a `ClassMap` per record type up front, and calling `csv.GetRecord<T>()` (singular) once per row inside whichever section is currently active.

## Reading multiple record types from one file (row-type discriminator)

For a file where every row can be a different record type (not separated into distinct sections, but interleaved), disable the header (`HasHeaderRecord = false`), register an index-based `ClassMap` per type, and use the first field on each row as a discriminator in a `switch` to decide which type to deserialize that row into — e.g. `1` maps to `Foo` (int Id, string Name), `2` maps to `Bar` (Guid Id, string Name), each read via `csv.GetRecord<Foo>()`/`csv.GetRecord<Bar>()` inside the matching `switch` arm.
