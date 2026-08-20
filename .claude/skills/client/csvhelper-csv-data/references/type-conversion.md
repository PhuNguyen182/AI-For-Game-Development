# Type Conversion

Source: [type-conversion](https://joshclose.github.io/CsvHelper/examples/type-conversion/), [type-converter-options](https://joshclose.github.io/CsvHelper/examples/type-conversion/type-converter-options/), [custom-type-converter](https://joshclose.github.io/CsvHelper/examples/type-conversion/custom-type-converter/), [csvdatareader](https://joshclose.github.io/CsvHelper/examples/csvdatareader/).

## Type converter options

"Most type converters use `IFormattable.ToString` to write and `TryParse` to read." Options tune that formatting/parsing (date styles, number styles, boolean literals) without replacing the converter entirely — set via the class map:

```csharp
public sealed class FooMap : ClassMap<Foo>
{
    public FooMap()
    {
        Map(m => m.DateTimeProp)
            .TypeConverterOption
            .DateTimeStyles(DateTimeStyles.AllowInnerWhite | DateTimeStyles.RoundtripKind);
    }
}
```

or via attribute:

```csharp
public class Foo
{
    [DateTimeStyles(DateTimeStyles.AllowInnerWhite | DateTimeStyles.RoundtripKind)]
    public DateTime DateTimeProp { get; set; }
}
```

## Custom type converter

"The built in type converters will handle most situations for you, but if you find a situation where they don't you can create your own type converter" — subclass `DefaultTypeConverter` (or implement `ITypeConverter` directly) and override `ConvertFromString`/`ConvertToString`:

```csharp
public class JsonNodeConverter : DefaultTypeConverter
{
    public override object ConvertFromString(string text, IReaderRow row, MemberMapData memberMapData)
    {
        return JsonSerializer.Deserialize<JsonNode>(text);
    }
}
```

Three ways to register it, in increasing order of scope:
1. **Global** — every occurrence of the target type, across every map: `csv.Context.TypeConverterCache.AddConverter<JsonNode>(new JsonNodeConverter());`
2. **Attribute** — on one property: `[TypeConverter(typeof(JsonNodeConverter))] public JsonNode Json { get; set; }`
3. **ClassMap** — on one property, for one specific map: `Map(m => m.Json).TypeConverter<JsonNodeConverter>();`

Prefer the narrowest scope that actually solves the problem — a global converter changes behavior for every map in the process, including ones this change wasn't meant to affect.

## CsvDataReader (DataTable integration)

`CsvDataReader` wraps a configured `CsvReader` as an `IDataReader`, primarily to feed a `DataTable.Load(...)`. "There is really no reason to use this class directly over using `CsvReader`" for anything else — reach for it only when the actual requirement is a `DataTable`/`IDataReader` consumer (e.g. handing data to an existing ADO.NET-oriented API), not as a general substitute for `GetRecords<T>()`.

```csharp
using (var reader = new StreamReader("path\\to\\file.csv"))
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
using (var dr = new CsvDataReader(csv))
{
    var dt = new DataTable();
    dt.Columns.Add("Id", typeof(int));
    dt.Columns.Add("Name", typeof(string));
    dt.Load(dr);
}
```

The `CsvReader` passed in must already be configured before constructing `CsvDataReader` — it reads the first row immediately on construction. Pre-declaring `DataTable` columns with explicit types (as above) gets typed columns instead of everything loading as `string`.
