# Type Conversion — Options, Custom Converters & CsvDataReader

Sources: [Type Conversion](https://joshclose.github.io/CsvHelper/examples/type-conversion/), [Type Converter Options](https://joshclose.github.io/CsvHelper/examples/type-conversion/type-converter-options/), [Custom Type Converter](https://joshclose.github.io/CsvHelper/examples/type-conversion/custom-type-converter/), [CsvDataReader](https://joshclose.github.io/CsvHelper/examples/csvdatareader/).
Covers: SKILL.md §4 — **"Prefer built-in converters and `TypeConverterOptions` over a custom `ITypeConverter`"**.

Ordered by escalation: tune the built-in converter first, write a custom one
only when no option covers the shape, and reach for `CsvDataReader` only when
the consumer genuinely demands an `IDataReader`. Where a converter is attached
to a property is [class-maps.md](class-maps.md) or [attributes.md](attributes.md).

## Built-in converters and their options

| Fact | What it decides | Source |
|---|---|---|
| Most converters use `IFormattable.ToString` to write and `TryParse` to read | Anything those two accept is already supported without custom code | [Type Conversion](https://joshclose.github.io/CsvHelper/examples/type-conversion/) |
| `TypeConverterOption` tunes formatting and parsing | Date styles, number styles, and boolean literal sets — no converter replacement needed | [Type Converter Options](https://joshclose.github.io/CsvHelper/examples/type-conversion/type-converter-options/) |
| Options are settable from a map or an attribute | Same effect either way; pick per [attributes.md](attributes.md) | [Type Converter Options](https://joshclose.github.io/CsvHelper/examples/type-conversion/type-converter-options/) |

```csharp
public sealed class FooMap : ClassMap<Foo>
{
    public FooMap()
    {
        Map(m => m.ReleasedAt)
            .TypeConverterOption
            .DateTimeStyles(DateTimeStyles.AllowInnerWhite | DateTimeStyles.RoundtripKind);
    }
}
```

## Custom converters

| Element | Effect | Use when | Source |
|---|---|---|---|
| `DefaultTypeConverter` subclass | Override `ConvertFromString`/`ConvertToString` for one type | The built-in converters and their options genuinely do not cover the shape | [Custom Type Converter](https://joshclose.github.io/CsvHelper/examples/type-conversion/custom-type-converter/) |
| `ITypeConverter` directly | Full control where the default base class is not wanted | A converter shares nothing with the default behaviour | [Custom Type Converter](https://joshclose.github.io/CsvHelper/examples/type-conversion/custom-type-converter/) |

```csharp
public sealed class LootJsonConverter : DefaultTypeConverter
{
    public override object ConvertFromString(string text, IReaderRow row, MemberMapData memberMapData)
    {
        return JsonSerializer.Deserialize<LootEntry[]>(text);
    }
}
```

## Registration scope — narrowest that solves the problem

| Scope | Registration | Reach | Source |
|---|---|---|---|
| ClassMap | `Map(m => m.Loot).TypeConverter<LootJsonConverter>();` | One property, one map — the default choice | [Custom Type Converter](https://joshclose.github.io/CsvHelper/examples/type-conversion/custom-type-converter/) |
| Attribute | `[TypeConverter(typeof(LootJsonConverter))]` | One property, everywhere that type is mapped | [Custom Type Converter](https://joshclose.github.io/CsvHelper/examples/type-conversion/custom-type-converter/) |
| Global | `csv.Context.TypeConverterCache.AddConverter<LootEntry[]>(new LootJsonConverter());` | Every occurrence of the type across every map in the process | [Custom Type Converter](https://joshclose.github.io/CsvHelper/examples/type-conversion/custom-type-converter/) |

**Critical caveat**: a global registration changes behaviour for maps this
change never intended to touch, including ones written later by someone else.
It is justified only when every occurrence of that type process-wide genuinely
needs the same conversion.

## CsvDataReader — DataTable interop

| Fact | What it decides | Source |
|---|---|---|
| Wraps a configured `CsvReader` as an `IDataReader` | Its purpose is feeding `DataTable.Load(...)`, not general reading | [CsvDataReader](https://joshclose.github.io/CsvHelper/examples/csvdatareader/) |
| The `CsvReader` must already be configured | It reads the first row immediately on construction | [CsvDataReader](https://joshclose.github.io/CsvHelper/examples/csvdatareader/) |
| Pre-declare `DataTable` columns with types | Otherwise every column loads as `string` | [CsvDataReader](https://joshclose.github.io/CsvHelper/examples/csvdatareader/) |

```csharp
using (var reader = new StreamReader("path/to/file.csv"))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
using (var dataReader = new CsvDataReader(csv))
{
    var table = new DataTable();
    table.Columns.Add("Id", typeof(int));
    table.Columns.Add("Name", typeof(string));
    table.Load(dataReader);
}
```

**Critical caveat**: upstream states there is no reason to use this class over
`CsvReader` for anything but `DataTable`/`IDataReader` interop. It is not a
general substitute for `GetRecords<T>()`.
