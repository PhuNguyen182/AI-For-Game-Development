# Attribute-Based Configuration — The ClassMap Alternative

Source: [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/).
Covers: SKILL.md §4 — **"Choose `ClassMap<T>` vs. attributes by how many mapping shapes the type needs"**.

Most of what a class map does can be declared as attributes on the model class
instead. That trade is the whole decision this file serves: attributes are
less code and couple the model to CsvHelper permanently; a
[class-maps.md](class-maps.md) map is more code and keeps the model clean.

## Supported attributes

| Attribute | Effect | Equivalent ClassMap call | Source |
|---|---|---|---|
| `[Name("Identifier")]` | Maps a property to a column by header name | `.Name(...)` | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| `[Index(1)]` | Maps a property by column position | `.Index(...)` | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| `[Ignore]` | Excludes the property from read and write | `.Ignore()` | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| `[Optional]` | Suppresses the throw when the column is missing | `.Optional()` | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| `[Constant(value)]` | Assigns a fixed value instead of reading a column | `.Constant(...)` | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| `[TypeConverter(typeof(T))]` | Assigns a custom `ITypeConverter` to the property | `.TypeConverter<T>()` | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| `[CultureInfo("...")]` | Sets culture at class or property level | Constructor culture argument | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| `[BooleanTrueValues]` / `[BooleanFalseValues]` | Customizes which strings parse as `true`/`false` | Type-converter option | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| `[Delimiter(",")]` | Sets the delimiter at class level | `CsvConfiguration.Delimiter` | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |

```csharp
var config = CsvConfiguration.FromAttributes<ItemBalanceRow>();
using (var reader = new StreamReader("path/to/file.csv"))
using (var csv = new CsvReader(reader, config))
{
    foreach (var record in csv.GetRecords<ItemBalanceRow>())
    {
        // FromAttributes<T>() is what activates the class-level attributes.
    }
}
```

## Deciding between the two

| Question | Answer it forces | Source |
|---|---|---|
| Does this type need more than one mapping shape? | Yes → `ClassMap<T>`; a class can carry only one attribute-based mapping | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| May the model type reference the CsvHelper package? | No → `ClassMap<T>`; attributes put a package reference on the model itself | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |
| Is the mapping simple, single, and stable? | Yes → attributes are the smaller, clearer option | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |

**Critical caveat**: a model type destined for `Game.Core.*` cannot use
attributes. Shared Core must not take an external package dependency it does
not strictly need, so the mapping has to live in a `ClassMap<T>` outside it.
