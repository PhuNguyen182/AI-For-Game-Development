# Writing CSV Data — WriteRecords & Appending

Sources: [Writing](https://joshclose.github.io/CsvHelper/examples/writing/), [Write Class Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-class-objects/), [Write Dynamic Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-dynamic-objects/), [Write Anonymous Type Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-anonymous-type-objects/), [Appending to an Existing File](https://joshclose.github.io/CsvHelper/examples/writing/appending-to-an-existing-file/).
Covers: SKILL.md §4 — **"Default to `GetRecords<T>()`/`WriteRecords()` with the by-name convention"**.

Writing is symmetric with [reading.md](reading.md) with one asymmetry that
causes most of the bugs: `WriteRecords` emits a header unconditionally, which
is correct for a new file and wrong for an append.

## WriteRecords behaviour

| Property | What it decides | Source |
|---|---|---|
| Header written once, then one row per item | Property names supply the header by default convention | [Write Class Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-class-objects/) |
| Disposal flushes and closes | No manual `Flush()` is needed when the `using` scopes are correct | [Write Class Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-class-objects/) |
| Dynamic and anonymous records work identically | The header is inferred from the first record's runtime member names or keys | [Write Dynamic Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-dynamic-objects/), [Write Anonymous Type Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-anonymous-type-objects/) |

```csharp
using (var writer = new StreamWriter("path/to/Localization.csv"))
using (var csv = new CsvWriter(writer, CultureInfo.InvariantCulture))
{
    csv.WriteRecords(records);
}
```

## Appending to a file that already has a header

| Step | Effect | Source |
|---|---|---|
| `File.Open(path, FileMode.Append)` | Positions the stream at end of file rather than truncating it | [Appending to an Existing File](https://joshclose.github.io/CsvHelper/examples/writing/appending-to-an-existing-file/) |
| `HasHeaderRecord = false` on the `CsvConfiguration` | Suppresses the second header — the one setting the whole pattern depends on | [Appending to an Existing File](https://joshclose.github.io/CsvHelper/examples/writing/appending-to-an-existing-file/) |
| `WriteRecords(newRecords)` | Writes only the new rows, which combine under the original header | [Appending to an Existing File](https://joshclose.github.io/CsvHelper/examples/writing/appending-to-an-existing-file/) |

```csharp
var config = new CsvConfiguration(CultureInfo.InvariantCulture)
{
    HasHeaderRecord = false,
};

using (var stream = File.Open("path/to/Localization.csv", FileMode.Append))
using (var writer = new StreamWriter(stream))
using (var csv = new CsvWriter(writer, config))
{
    csv.WriteRecords(newRecords);
}
```

**Critical caveat**: without `HasHeaderRecord = false`, the append writes a
second header row at the current file position — a header in the middle of the
data. Nothing throws; the file is simply corrupt for every later reader.
