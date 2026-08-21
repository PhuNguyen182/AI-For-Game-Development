# Root Links — .NET (BCL) Memory and Collections

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to the .NET Base Class Library
documentation on Microsoft Learn. Anything this skill cites resolves under
one of these roots; anything that does not is out of scope for the skill,
not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| .NET fundamentals/standard | `Span<T>`/`Memory<T>` usage guidelines, thread-safe collections guidance | [Memory<T> and Span<T> usage guidelines](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/memory-t-usage-guidelines) |
| C# language guide | `stackalloc` expression reference | [stackalloc expression](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/stackalloc) |
| API reference | `Span<T>`/`Memory<T>`/`ArrayPool<T>`/`System.Collections.Immutable`/`System.Collections.Concurrent` member docs | [.NET API browser](https://learn.microsoft.com/en-us/dotnet/api/) |

Conceptual and language-guide pages in this folder are unversioned by URL —
they describe current, stable C#/.NET language and library behavior, not a
specific release. API reference pages ARE versioned through Microsoft
Learn's `?view=` query parameter; every API reference link in this folder is
pinned to `?view=netstandard-2.1` — the API surface Unity's default Player
Settings → Api Compatibility Level actually ships, not the newest .NET
release. Confirm the project's real compatibility level before assuming a
member shown on a page's *current* view is available at netstandard-2.1; the
page's own version selector shows this. Consult the live site for anything
not covered here — .NET adds APIs between releases.
