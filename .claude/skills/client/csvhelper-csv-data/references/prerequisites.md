# Prerequisites — Disposal, Files & Streams

Sources: [Using and Dispose](https://joshclose.github.io/CsvHelper/examples/prerequisites/using-and-dispose/), [Reading and Writing Files](https://joshclose.github.io/CsvHelper/examples/prerequisites/reading-and-writing-files/), [Streams](https://joshclose.github.io/CsvHelper/examples/prerequisites/streams/).
Covers: SKILL.md §4 — **"Wrap every reader, writer, and stream in `using`"**.

CsvHelper never touches a byte stream directly: it operates on a
`TextReader`/`TextWriter`, so every usage is a chain of two or three
`IDisposable` objects whose disposal order matters. This file holds that chain
and the scope pattern that gets it right.

## The adapter chain

| Layer | Effect | Use when | Source |
|---|---|---|---|
| `Stream` | The raw bytes — `FileStream`, `MemoryStream`, a network stream | Always present underneath, explicitly or via a convenience constructor | [Streams](https://joshclose.github.io/CsvHelper/examples/prerequisites/streams/) |
| `StreamReader`/`StreamWriter` | Adapts bytes to characters — the required intermediary | Always; CsvHelper cannot consume a raw `Stream` | [Streams](https://joshclose.github.io/CsvHelper/examples/prerequisites/streams/) |
| `CsvReader`/`CsvWriter` | Parses/formats CSV over the character reader or writer | Always; takes the `TextReader`/`TextWriter` plus culture or `CsvConfiguration` | [Reading and Writing Files](https://joshclose.github.io/CsvHelper/examples/prerequisites/reading-and-writing-files/) |

## Disposal rules

| Rule | Effect | Source |
|---|---|---|
| Every `IDisposable` is disposed when done | The upstream guidance is unconditional; a leaked handle keeps a file locked | [Using and Dispose](https://joshclose.github.io/CsvHelper/examples/prerequisites/using-and-dispose/) |
| Prefer the inline form | `using (var stream = new MemoryStream())` shows intent; declaring first and writing `using (stream) { }` works but does not | [Using and Dispose](https://joshclose.github.io/CsvHelper/examples/prerequisites/using-and-dispose/) |
| Nest reader inside stream | `CsvReader`/`CsvWriter` disposes first, the underlying stream second | [Reading and Writing Files](https://joshclose.github.io/CsvHelper/examples/prerequisites/reading-and-writing-files/) |
| C# 8+ `using` declarations are equivalent | Same ordering guarantee without the nesting braces | [Using and Dispose](https://joshclose.github.io/CsvHelper/examples/prerequisites/using-and-dispose/) |

```csharp
using (var reader = new StreamReader("path/to/file.csv"))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
{
    foreach (var record in csv.GetRecords<ItemBalanceRow>())
    {
        // Consume each row here; the reader is disposed on scope exit.
    }
}
```

**Critical caveat**: never let the `CsvReader` outlive the scope owning its
stream. `GetRecords<T>()` is deferred (see [reading.md](reading.md)), so
returning its `IEnumerable<T>` out of the `using` block hands the caller a
sequence backed by an already-disposed reader — it compiles and fails at
enumeration.
