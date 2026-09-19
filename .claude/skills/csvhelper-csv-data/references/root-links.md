# Root Links — CsvHelper Documentation Index

Source: the documentation pages listed below, on the official CsvHelper site.
Covers: the whole skill — provenance and page index for every file in this
folder.

Indexes every upstream page this skill was distilled from, grouped by the
topic file that covers it. Reach for it when a needed page is not covered by
a sibling file. **CsvHelper's documentation is unversioned** — there is no
version segment to pin, so consult the live site for anything absent here;
the library adds features between releases.

## Getting started and prerequisites

| Page | Holds | Source |
|---|---|---|
| Getting Started | Installation (`Install-Package CsvHelper`, `dotnet add package CsvHelper`) and the minimal read/write pattern | [Getting Started](https://joshclose.github.io/CsvHelper/getting-started/) |
| Prerequisites | Index of the disposal/file/stream pages, distilled in [prerequisites.md](prerequisites.md) | [Prerequisites](https://joshclose.github.io/CsvHelper/examples/prerequisites/) |
| Using and Dispose | Disposal discipline for `IDisposable` readers and writers | [Using and Dispose](https://joshclose.github.io/CsvHelper/examples/prerequisites/using-and-dispose/) |
| Reading and Writing Files | The canonical `StreamReader` + `CsvReader` scope pattern | [Reading and Writing Files](https://joshclose.github.io/CsvHelper/examples/prerequisites/reading-and-writing-files/) |
| Streams | Which `Stream` types work and the adapter that is required | [Streams](https://joshclose.github.io/CsvHelper/examples/prerequisites/streams/) |

## Reading — distilled in [reading.md](reading.md)

| Page | Holds | Source |
|---|---|---|
| Reading | Entry point for the reading topics | [Reading](https://joshclose.github.io/CsvHelper/examples/reading/) |
| Get Class Records | `GetRecords<T>()` with by-name convention | [Get Class Records](https://joshclose.github.io/CsvHelper/examples/reading/get-class-records/) |
| Get Dynamic Records | `GetRecords<dynamic>()` and its all-`string` result | [Get Dynamic Records](https://joshclose.github.io/CsvHelper/examples/reading/get-dynamic-records/) |
| Get Anonymous Type Records | Projecting into an anonymous shape | [Get Anonymous Type Records](https://joshclose.github.io/CsvHelper/examples/reading/get-anonymous-type-records/) |
| Enumerate Class Records | Deferred enumeration and its memory consequence | [Enumerate Class Records](https://joshclose.github.io/CsvHelper/examples/reading/enumerate-class-records/) |
| Reading by Hand | `ReadHeader()`/`Read()`/`GetField<T>()` | [Reading by Hand](https://joshclose.github.io/CsvHelper/examples/reading/reading-by-hand/) |
| Reading Multiple Data Sets | Several tables in one file, separated by blank lines | [Reading Multiple Data Sets](https://joshclose.github.io/CsvHelper/examples/reading/reading-multiple-data-sets/) |
| Reading Multiple Record Types | Interleaved rows with a discriminator column | [Reading Multiple Record Types](https://joshclose.github.io/CsvHelper/examples/reading/reading-multiple-record-types/) |

## Writing — distilled in [writing.md](writing.md)

| Page | Holds | Source |
|---|---|---|
| Writing | Entry point for the writing topics | [Writing](https://joshclose.github.io/CsvHelper/examples/writing/) |
| Write Class Objects | `WriteRecords` over a typed collection | [Write Class Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-class-objects/) |
| Write Dynamic Objects | Header inference from a dynamic record | [Write Dynamic Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-dynamic-objects/) |
| Write Anonymous Type Objects | Writing an anonymous shape | [Write Anonymous Type Objects](https://joshclose.github.io/CsvHelper/examples/writing/write-anonymous-type-objects/) |
| Appending to an Existing File | Suppressing the second header write | [Appending to an Existing File](https://joshclose.github.io/CsvHelper/examples/writing/appending-to-an-existing-file/) |

## Mapping — distilled in [class-maps.md](class-maps.md) and [attributes.md](attributes.md)

| Page | Holds | Source |
|---|---|---|
| Configuration | Entry point for configuration topics | [Configuration](https://joshclose.github.io/CsvHelper/examples/configuration/) |
| Class Maps | Registering and structuring a `ClassMap<T>` | [Class Maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/) |
| Mapping Properties | The `Map(m => m.Property)` call shape | [Mapping Properties](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-properties/) |
| Mapping by Name / Alternate Names / Duplicate Names | Header-name matching, fallbacks, and disambiguation | [Mapping by Name](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-name/), [Alternate Names](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-alternate-names/), [Duplicate Names](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-duplicate-names/) |
| Mapping by Index | Position-based mapping for headerless files | [Mapping by Index](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/mapping-by-index/) |
| Auto Mapping | `AutoMap` plus targeted overrides | [Auto Mapping](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/auto-mapping/) |
| Ignoring Properties / Constant Value / Optional Maps | Properties with no column, a fixed value, or an absent column | [Ignoring Properties](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/ignoring-properties/), [Constant Value](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/constant-value/), [Optional Maps](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/optional-maps/) |
| Type Conversion / Inline Type Conversion | Per-property converter assignment and inline `.Convert` | [Type Conversion](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/type-conversion/), [Inline Type Conversion](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/inline-type-conversion/) |
| Validation | `.Validate()` predicates on the raw field | [Validation](https://joshclose.github.io/CsvHelper/examples/configuration/class-maps/validation/) |
| Attributes | The attribute equivalents of the above | [Attributes](https://joshclose.github.io/CsvHelper/examples/configuration/attributes/) |

## Type conversion and other — distilled in [type-conversion.md](type-conversion.md)

| Page | Holds | Source |
|---|---|---|
| Type Conversion | How converters read and write | [Type Conversion](https://joshclose.github.io/CsvHelper/examples/type-conversion/) |
| Type Converter Options | Date/number/boolean formatting without a custom converter | [Type Converter Options](https://joshclose.github.io/CsvHelper/examples/type-conversion/type-converter-options/) |
| Custom Type Converter | `DefaultTypeConverter`/`ITypeConverter` and registration | [Custom Type Converter](https://joshclose.github.io/CsvHelper/examples/type-conversion/custom-type-converter/) |
| CsvDataReader | `IDataReader` adapter for `DataTable.Load` | [CsvDataReader](https://joshclose.github.io/CsvHelper/examples/csvdatareader/) |
| Migration / Change Log | Breaking changes between major versions | [Migration](https://joshclose.github.io/CsvHelper/migration/), [Change Log](https://joshclose.github.io/CsvHelper/change-log/) |
