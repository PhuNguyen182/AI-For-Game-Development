# Attribute-Based Configuration

Source: [attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/).

"Most of the configuration done via class maps can also be done using attributes" — decorate the model class directly instead of writing a separate `ClassMap<T>`, for the common case where a map class would otherwise just restate the same handful of settings.

## Supported attributes

| Attribute | Equivalent ClassMap call | Purpose |
|---|---|---|
| `[Name("Identifier")]` | `.Name(...)` | Map a property to a CSV column by header name |
| `[Index(1)]` | `.Index(...)` | Map a property by column position |
| `[Ignore]` | `.Ignore()` | Exclude a property from read/write |
| `[Optional]` | `.Optional()` | Don't throw if the column is missing |
| `[Constant(value)]` | `.Constant(...)` | Assign a fixed value instead of reading a column |
| `[TypeConverter(typeof(T))]` | `.TypeConverter<T>()` | Assign a custom `ITypeConverter` to this property |
| `[CultureInfo("...")]` | constructor culture argument | Set culture at class or property level |
| `[BooleanTrueValues]` / `[BooleanFalseValues]` | type-converter option | Customize which strings parse as `true`/`false` |
| `[Delimiter(",")]` | `CsvConfiguration.Delimiter` | Set the delimiter at class level |

## Wiring attributes into configuration

```csharp
var config = CsvConfiguration.FromAttributes<Foo>();
using (var reader = new StreamReader("path\\to\\file.csv"))
using (var csv = new CsvReader(reader, config))
{
    var records = csv.GetRecords<Foo>();
}
```

## Choosing attributes vs. ClassMap

- Attributes put configuration directly on the model class — convenient for a simple, stable mapping, but it couples the data model to CsvHelper (an attribute reference on every property) and to one specific mapping (a class can't have two different attribute-based mappings for two different files' header conventions).
- A `ClassMap<T>` keeps the model class free of CsvHelper attributes and supports registering more than one map for the same type (e.g. one per file variant) — prefer it once a type needs more than one mapping shape, or when the model class shouldn't take a dependency on the CsvHelper package at all (see this skill's negative triggers in `SKILL.md` for when a model type belongs in `Game.Core.*`).
