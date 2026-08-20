# Writing CSV Data

Source: [writing](https://joshclose.github.io/CsvHelper/examples/writing/), [write-class-objects](https://joshclose.github.io/CsvHelper/examples/writing/write-class-objects/), [write-dynamic-objects](https://joshclose.github.io/CsvHelper/examples/writing/write-dynamic-objects/), [write-anonymous-type-objects](https://joshclose.github.io/CsvHelper/examples/writing/write-anonymous-type-objects/), [appending-to-an-existing-file](https://joshclose.github.io/CsvHelper/examples/writing/appending-to-an-existing-file/).

## WriteRecords\<T\>() — a collection

```csharp
var records = new List<Foo>
{
    new Foo { Id = 1, Name = "one" },
};

using (var writer = new StreamWriter("path\\to\\file.csv"))
using (var csv = new CsvWriter(writer, CultureInfo.InvariantCulture))
{
    csv.WriteRecords(records);
}
```

Produces:
```
Id,Name
1,one
```

`WriteRecords` writes the header row (property names, by default convention) once, then one row per item in the collection. Disposing the nested `using (var writer = ...)` / `using (var csv = ...)` block flushes and closes both — no manual `Flush()` call needed for the common case.

Dynamic objects and anonymous types can be written the same way — `WriteRecords` infers the header from whatever member names/keys the runtime type of the first record exposes.

## Appending to an existing file

Writing again into a file that already has a header requires suppressing the header row, or it gets written a second time. Open the file in append mode and configure `HasHeaderRecord = false` for that second write:

```csharp
var config = new CsvConfiguration(CultureInfo.InvariantCulture)
{
    HasHeaderRecord = false,
};

using (var stream = File.Open("path\\to\\file.csv", FileMode.Append))
using (var writer = new StreamWriter(stream))
using (var csv = new CsvWriter(writer, config))
{
    csv.WriteRecords(newRecords);
}
```

Result — header appears once, both writes' rows combine under it:
```
Id,Name
1,one
2,two
```

`HasHeaderRecord = false` is the essential setting here — without it, `WriteRecords` writes the header again at the current (appended) file position, producing a header row in the middle of the data.
