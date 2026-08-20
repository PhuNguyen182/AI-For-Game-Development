# Class Maps

Source: [class-maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/), [mapping-properties](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-properties/), [mapping-by-name](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-name/), [mapping-by-alternate-names](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-alternate-names/), [mapping-duplicate-names](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-duplicate-names/), [mapping-by-index](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-index/), [auto-mapping](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/auto-mapping/), [ignoring-properties](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/ignoring-properties/), [constant-value](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/constant-value/), [type-conversion](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/type-conversion/), [inline-type-conversion](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/inline-type-conversion/), [optional-maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/optional-maps/), [validation](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/validation/).

A `ClassMap<T>` is registered once per reader/writer via `csv.Context.RegisterClassMap<FooMap>()`, before calling `GetRecords<T>()`/`WriteRecords()`. Every mapping technique below is a `Map(m => m.Property)` call chained with a configuration method.

## Mapping by name

Use when the CSV header text doesn't match the property name:

```csharp
public sealed class FooMap : ClassMap<Foo>
{
    public FooMap()
    {
        Map(m => m.Id).Name("ColumnA");
        Map(m => m.Name).Name("ColumnB");
    }
}
```

## Mapping by alternate names

`.Name(...)` accepts multiple header strings for the same property, so a property can match whichever header name the current file actually uses (useful across CSV export sources/versions that renamed a column).

## Mapping duplicate names

When two columns in the CSV share the same header text, disambiguate with a name index alongside `.Name(...)` (the Nth column with that header name) rather than relying on plain `.Name(...)`, which would otherwise resolve ambiguously.

## Mapping by index

Use when the CSV has no header row at all — `HasHeaderRecord = false` in `CsvConfiguration`, then map every property to a fixed column position. **You can't rely on the order of class properties in .NET**, so index-based mapping must be explicit:

```csharp
public sealed class FooMap : ClassMap<Foo>
{
    public FooMap()
    {
        Map(m => m.Id).Index(0);
        Map(m => m.Name).Index(1);
    }
}
```

## Auto mapping + overrides

`AutoMap(CultureInfo)` generates the default (by-name) mapping for every property; call it first, then override only the properties that need something different — the common pattern once a class has more than a couple of properties needing customization:

```csharp
public sealed class FooMap : ClassMap<Foo>
{
    public FooMap()
    {
        AutoMap(CultureInfo.InvariantCulture);
        Map(m => m.Name).Name("The Name");
    }
}
```

## Ignoring properties

`.Ignore()` excludes a property AutoMap would otherwise pick up, for a property that has no corresponding CSV column (a computed/runtime-only field):

```csharp
AutoMap(CultureInfo.InvariantCulture);
Map(m => m.IsDirty).Ignore();
```

## Constant value

`.Constant(value)` assigns a fixed value to a property on every row instead of reading it from a column — for a property with no CSV column at all that still needs a deterministic value on the resulting object:

```csharp
Map(m => m.IsDirty).Constant(true);
```

## Optional maps

`.Optional()` on a mapped property tells CsvHelper not to throw when that column is missing from the file — needed for a property that's present in some file versions/variants but not others:

```csharp
Map(m => m.Date).Optional();
```

## Type conversion (class-map level) and inline type conversion

`.TypeConverter<T>()` (or the attribute/global-registration forms — see [type-conversion.md](type-conversion.md)) assigns a specific `ITypeConverter` to one property's mapping. `.Convert(row => ...)` (inline type conversion) supplies a conversion lambda directly on the map for a one-off case that doesn't warrant a whole separate converter class — reach for a named `ITypeConverter` once the conversion logic is non-trivial or reused across maps (see [type-conversion.md](type-conversion.md)'s Custom Type Converter section).

## Validation

`.Validate(args => ...)` runs a predicate against the raw field value (`args.Field`) before/during conversion; returning `false` signals an invalid field:

```csharp
public class FooMap : ClassMap<Foo>
{
    public FooMap()
    {
        Map(m => m.Id);
        Map(m => m.Name).Validate(args => !args.Field.Contains("-"));
    }
}
```
