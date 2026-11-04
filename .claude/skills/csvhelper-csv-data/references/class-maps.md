# Class Maps and Attributes

Docs: https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/ and /examples/configuration/attributes/.

Each technique below is a reason the by-name convention is not enough; if none applies, write no map.

## Registration
- `csv.Context.RegisterClassMap<FooMap>()` once per reader/writer, before `GetRecords<T>()`/`WriteRecords()`.
- Every technique is a `Map(m => m.Property)` chain, one property per statement.
- Several maps may be registered per type (attributes allow only one mapping per class); this is why a map wins for multi-variant files.

## Selecting the column
| Technique | Use when |
|---|---|
| `.Name("A")` | Header text differs from the property name |
| `.Name("A", "B")` | A column was renamed across export sources/versions |
| `.Name(...)` plus name index | Two columns share a header; selects the Nth |
| `.Index(0)` | `HasHeaderRecord = false` |
| `AutoMap(CultureInfo)` then overrides | More than a couple of properties need customizing |

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
Property declaration order is not guaranteed by .NET, so index mapping must name every index explicitly.

## Properties with no column
| Technique | Effect |
|---|---|
| `.Ignore()` | Excludes a property `AutoMap` would pick up (computed/runtime-only) |
| `.Constant(value)` | Fixed value on every row |
| `.Optional()` | No throw when the column is absent in some file variants |

## Conversion and validation
| Technique | Use when |
|---|---|
| `.TypeConverter<T>()` | Non-trivial or reused conversion ([type-conversion.md](type-conversion.md)) |
| `.Convert(row => ...)` | One-off inline conversion |
| `.Validate(args => ...)` | Predicate on raw `args.Field`; `false` rejects the field at parse time |

```csharp
Map(m => m.Id).Validate(args => !args.Field.Contains("-"));
Map(m => m.Loot).TypeConverter<LootJsonConverter>();
```

## Attributes
Equivalents: `[Name("x")]`, `[Index(1)]`, `[Ignore]`, `[Optional]`, `[Constant(v)]`, `[TypeConverter(typeof(T))]`, `[CultureInfo("..")]`, `[BooleanTrueValues]`/`[BooleanFalseValues]`, `[Delimiter(",")]`. Class-level ones need `CsvConfiguration.FromAttributes<T>()`:
```csharp
var config = CsvConfiguration.FromAttributes<ItemBalanceRow>();
using (var csv = new CsvReader(reader, config)) { /* GetRecords<ItemBalanceRow>() */ }
```
Attributes put a CsvHelper reference on the model, so a type destined for a Core assembly must use a `ClassMap<T>` outside Core.
