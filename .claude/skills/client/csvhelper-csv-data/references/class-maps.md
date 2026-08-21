# Class Maps — Every ClassMap<T> Mapping Technique

Sources: [Class Maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/), [Mapping Properties](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-properties/), [Mapping by Name](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-name/), [Alternate Names](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-alternate-names/), [Duplicate Names](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-duplicate-names/), [Mapping by Index](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-index/), [Auto Mapping](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/auto-mapping/), [Ignoring Properties](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/ignoring-properties/), [Constant Value](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/constant-value/), [Optional Maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/optional-maps/), [Type Conversion](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/type-conversion/), [Inline Type Conversion](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/inline-type-conversion/), [Validation](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/validation/).
Covers: SKILL.md §4 — **"Default to `GetRecords<T>()`/`WriteRecords()` with the by-name convention"**, **"Choose `ClassMap<T>` vs. attributes by how many mapping shapes the type needs"**.

Each row below is one reason the by-name convention is not enough. If none
applies, no map should be written at all. The attribute form of the same
settings is [attributes.md](attributes.md); converter selection is
[type-conversion.md](type-conversion.md).

## Contents

- [Registration](#registration)
- [Selecting the column](#selecting-the-column)
- [Properties with no column](#properties-with-no-column)
- [Conversion and validation](#conversion-and-validation)

## Registration

| Fact | What it decides | Source |
|---|---|---|
| `csv.Context.RegisterClassMap<FooMap>()` | Registers the map once per reader or writer, **before** `GetRecords<T>()`/`WriteRecords()` | [Class Maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/) |
| Every technique is a chained `Map(m => m.Property)` call | One property per statement, so a map reads as a column list | [Mapping Properties](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-properties/) |
| More than one map may be registered per type | This is what attributes cannot do — the reason a map wins for multi-variant files | [Class Maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/) |

## Selecting the column

| Technique | Effect | Use when | Source |
|---|---|---|---|
| `.Name("ColumnA")` | Matches by header text instead of property name | The header text and the property name differ | [Mapping by Name](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-name/) |
| `.Name("A", "B")` | Accepts several header strings for one property | Export sources or versions renamed a column | [Alternate Names](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-alternate-names/) |
| `.Name(...)` plus a name index | Selects the Nth column carrying that header text | Two columns share the same header | [Duplicate Names](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-duplicate-names/) |
| `.Index(0)` | Matches by column position | `HasHeaderRecord = false` — there is no header to match | [Mapping by Index](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-index/) |
| `AutoMap(CultureInfo)` then overrides | Generates the by-name mapping for every property, then replaces only the exceptions | More than a couple of properties need customization | [Auto Mapping](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/auto-mapping/) |

```csharp
public sealed class ItemBalanceRowMap : ClassMap<ItemBalanceRow>
{
    public ItemBalanceRowMap()
    {
        AutoMap(CultureInfo.InvariantCulture);
        Map(m => m.Id).Name("Item Id");
        Map(m => m.BaseDamage).Name("Base Damage");
    }
}
```

**Critical caveat**: .NET does not guarantee the declaration order of class
properties, so index-based mapping must name every index explicitly. A map
that relies on property order is correct until an unrelated edit reorders the
class.

## Properties with no column

| Technique | Effect | Use when | Source |
|---|---|---|---|
| `.Ignore()` | Excludes a property `AutoMap` would otherwise pick up | The property is computed or runtime-only | [Ignoring Properties](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/ignoring-properties/) |
| `.Constant(value)` | Assigns a fixed value on every row instead of reading one | No column exists but the object still needs a deterministic value | [Constant Value](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/constant-value/) |
| `.Optional()` | Suppresses the throw when the column is absent | The column exists in some file variants and not others | [Optional Maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/optional-maps/) |

## Conversion and validation

| Technique | Effect | Use when | Source |
|---|---|---|---|
| `.TypeConverter<T>()` | Assigns a named `ITypeConverter` to one property's mapping | The conversion is non-trivial or reused across maps | [Type Conversion](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/type-conversion/) |
| `.Convert(row => ...)` | Supplies the conversion inline as a lambda | A one-off that does not warrant a converter class | [Inline Type Conversion](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/inline-type-conversion/) |
| `.Validate(args => ...)` | Runs a predicate against the raw `args.Field`; `false` signals an invalid field | A business rule must reject bad data at parse time | [Validation](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/validation/) |

```csharp
public sealed class ItemBalanceRowMap : ClassMap<ItemBalanceRow>
{
    public ItemBalanceRowMap()
    {
        Map(m => m.Id).Validate(args => !args.Field.Contains("-"));
        Map(m => m.Loot).TypeConverter<LootJsonConverter>();
    }
}
```
