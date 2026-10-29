# Writing CSV

Docs: https://joshclose.github.io/CsvHelper/examples/writing/ (write-class-objects, write-dynamic-objects, write-anonymous-type-objects, appending-to-an-existing-file).

- `WriteRecords` writes the header once, then a row per item (property names by default). Disposal flushes and closes; no manual `Flush()`.
- Dynamic and anonymous records infer the header from the first record's member names or keys.
- `WriteRecords` always emits a header: right for a new file, wrong for an append.

```csharp
using (var writer = new StreamWriter(path))
using (var csv = new CsvWriter(writer, CultureInfo.InvariantCulture))
    csv.WriteRecords(records);
```

## Append to a file that has a header
Open with `File.Open(path, FileMode.Append)` and set `HasHeaderRecord = false` on the `CsvConfiguration`; without it a second header lands mid-file and nothing throws.
```csharp
var config = new CsvConfiguration(CultureInfo.InvariantCulture) { HasHeaderRecord = false };
using (var stream = File.Open(path, FileMode.Append))
using (var writer = new StreamWriter(stream))
using (var csv = new CsvWriter(writer, config))
    csv.WriteRecords(newRecords);
```
