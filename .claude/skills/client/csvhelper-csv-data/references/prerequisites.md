# Prerequisites — Disposal, Files, Streams

Source: [prerequisites/using-and-dispose](https://joshclose.github.io/CsvHelper/examples/prerequisites/using-and-dispose/), [prerequisites/reading-and-writing-files](https://joshclose.github.io/CsvHelper/examples/prerequisites/reading-and-writing-files/), [prerequisites/streams](https://joshclose.github.io/CsvHelper/examples/prerequisites/streams/).

## Using and Dispose

`CsvReader`/`CsvWriter` wrap an `IDisposable` `TextReader`/`TextWriter` (typically a `StreamReader`/`StreamWriter`). The documentation's guidance: "Whenever you have an object that implements `IDisposable`, you need to dispose of the resource when you're done with it" — wrap it in a `using` block so disposal happens as soon as the block exits, rather than deferring it manually:

```csharp
var stream = new MemoryStream();
using (stream) { }
```

This deferred form works but "doesn't show intent" as clearly as an inline `using (var stream = new MemoryStream())`. Prefer the inline form. Nest the reader/writer's `using` inside the stream's `using` (or use C# 8+ `using` declarations) so both are disposed in the correct order — `CsvReader`/`CsvWriter` first, then the underlying stream.

## Reading and Writing Files

The canonical pattern pairs a `StreamReader`/`StreamWriter` with a `CsvReader`/`CsvWriter`, both scoped to the same `using`:

```csharp
using (var reader = new StreamReader("path\\to\\file.csv"))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
{
    var records = csv.GetRecords<Foo>();
}
```

## Streams

`CsvReader`/`CsvWriter` operate against a `TextReader`/`TextWriter`, not a raw `Stream` — a `StreamReader`/`StreamWriter` is the adapter between a byte stream (file, network, memory) and the character-based reader/writer CsvHelper needs. Any `Stream` works (`FileStream`, `MemoryStream`, a network stream) as long as it's wrapped in a `StreamReader`/`StreamWriter` first.
