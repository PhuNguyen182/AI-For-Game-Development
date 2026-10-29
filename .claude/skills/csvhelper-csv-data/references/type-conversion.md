# Type Conversion

Docs: https://joshclose.github.io/CsvHelper/examples/type-conversion/ (type-converter-options, custom-type-converter) and /examples/csvdatareader/.

Escalate in order: tune the built-in converter, then a custom one, and `CsvDataReader` only for an `IDataReader` consumer.

## Built-ins
- Most converters write with `IFormattable.ToString` and read with `TryParse`; anything those accept needs no custom code.
- `TypeConverterOption` (from a map or attribute) tunes date styles, number styles and boolean literals.
```csharp
Map(m => m.ReleasedAt).TypeConverterOption
    .DateTimeStyles(DateTimeStyles.AllowInnerWhite | DateTimeStyles.RoundtripKind);
```

## Custom converter
Subclass `DefaultTypeConverter` (override `ConvertFromString`/`ConvertToString`) or implement `ITypeConverter` directly; only when no option covers the shape.
```csharp
public sealed class LootJsonConverter : DefaultTypeConverter
{
    public override object ConvertFromString(string text, IReaderRow row, MemberMapData memberMapData)
        => JsonSerializer.Deserialize<LootEntry[]>(text);
}
```

## Registration scope — narrowest that works
| Scope | Registration |
|---|---|
| ClassMap (default) | `Map(m => m.Loot).TypeConverter<LootJsonConverter>();` |
| Attribute | `[TypeConverter(typeof(LootJsonConverter))]` |
| Global | `csv.Context.TypeConverterCache.AddConverter<LootEntry[]>(new LootJsonConverter());` |

Global changes every map in the process, including ones written later; use it only when every occurrence of that type needs the same conversion.

## CsvDataReader
- Wraps a configured `CsvReader` as `IDataReader` to feed `DataTable.Load(...)`; it reads the first row on construction.
- Pre-declare typed `DataTable` columns, otherwise all load as `string`.
- Upstream: no reason to use it over `CsvReader` except `DataTable`/`IDataReader` interop.
```csharp
using (var dataReader = new CsvDataReader(csv))
{
    var table = new DataTable();
    table.Columns.Add("Id", typeof(int));
    table.Columns.Add("Name", typeof(string));
    table.Load(dataReader);
}
```
