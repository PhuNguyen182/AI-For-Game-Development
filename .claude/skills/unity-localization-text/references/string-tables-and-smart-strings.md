# String Tables and Smart Strings

Sources, below the `Docs:` base: [a] `manual/StringTables.html`, [b] `manual/Scripting.html`, [c] `api/UnityEngine.Localization.Settings.LocalizationSettings.html`, [d] `api/UnityEngine.Localization.Components.LocalizeStringEvent.html`, [e] `manual/Smart/SmartStrings.html`, [f] `manual/Smart/Plural-Formatter.html`, [g] `manual/LocalizationSettings.html`, [h] `manual/UIToolkit.html`, [i] `changelog/CHANGELOG.html`. Elsewhere: [j] https://docs.unity.com/en-us/engine/6000.7/manual/localization.md, [k] https://docs.unity3d.com/Packages/com.unity.localization@2.0/manual/upgrade-guide.html.

## Version gate

| Subject | Fact that decides |
|---|---|
| `com.unity.localization` 1.5.13 | Latest 1.5 release (2026-09-02) [i]; every API name below is 1.5's |
| Unity 6.7+ (Beta) | Ships Localization Runtime as a built-in package, enabled by default; package 2.0 is needed only to load through Addressables or import/export CSV and XLIFF [j] |
| Package 2.0 upgrade wizard | One-way: saves scenes and prefabs, replaces `LocalizeStringEvent` with built-in equivalents, keeps `GetLocalizedString` working through a redirect layer; locale fallbacks do not carry over; built-in Smart Strings do not read doubled braces as escapes [k] |

## Tables

| Subject | Fact that decides |
|---|---|
| String Table Collection | Editor-only asset grouping one String Table per Locale, all sharing one Shared Table Data [a] |
| Shared Table Data | Holds key names, their Key Ids and shared metadata; per-locale metadata is visible only to its own table [a] |
| Entry references | Inspector and UI Builder store table GUID and entry Id by default (Edit > Preferences > Localization changes it) [h]; a reference by key name breaks when the key is renamed |
| Preload | Off by default; a table not preloaded loads asynchronously on first request, so a string may not be available that frame [a]. Preload Behavior: No Preloading, Preload Selected Locale, Preload Selected Locale And Fallbacks, Preload All Locales [g] |
| No Translation Found Format | The text returned for a missing entry: it reaches the player's screen [g]. Detect gaps with `unity:localization` §5 |

## Initialization and locale change

| Subject | Fact that decides |
|---|---|
| `LocalizationSettings.InitializationOperation` | The system "may not be immediately ready": yield it in a coroutine or await the handle before the first read [b][c]. Since 1.5.0-pre.6 it fails when any sub-operation fails [i]: check its status, not only completion |
| `SelectedLocale` | Reading it before initialization forces all locales to load and blocks until they do [c] |
| `SelectedLocaleAsync` | Waits only for locale initialization, not the whole operation [c] |
| Initialize Synchronously | Blocks the main thread until initialization finishes; ignored on WebGL. `WaitForCompletion` is unsupported on WebGL [c][g] |
| Asynchronous Behaviour (String Database) | 1.5 global switch to force `WaitForCompletion` instead of per-`LocalizedString` flags [g][i] |
| `LocalizationSettings.SelectedLocaleChanged` | Raised whenever `SelectedLocale` changes [c] |
| `LocalizedString.StringChanged` | Calls the handler at subscription if the table is loaded, else when it becomes available, and again on every locale change [b] |
| `LocalizedString.Arguments` + `RefreshString()` | Supply format arguments; `RefreshString()` regenerates after their values change [b] |
| `LocalizeStringEvent` | `OnUpdateString` fires when the string is available and on each `StringChanged`; `RefreshString()`, `SetEntry(string)`, `SetTable(string)` [d]. Persistent-listener wiring and its call state → `unity:localization` §5 |
| UI Toolkit binding (Unity 6+) | `label.SetBinding("text", new LocalizedString("Table", "Entry"))`, or a UXML `<Bindings>` block with `table`/`entry`; local variables in a nested `<variables>` element; at runtime `GetBinding("text") as LocalizedString` and set the variable. Fonts bind through `LocalizedFont` / `LocalizedTmpFont` [h] |

## Smart Strings

| Subject | Fact that decides |
|---|---|
| Marking | Per entry: ⋮ → Smart Format in the Tables window, the Smart field in the Localized String editor, or `entry.IsSmart = true` in an Editor script [e] |
| Selectors | `{Name}` reads a property of argument 0; `{1.City}` indexes an argument; scopes nest: `{User.Address:{City}}` [e] |
| Variables | Local Variables on the `LocalizedString`; the Persistent Variables source supplies arguments without script [e] |
| Culture | Numbers, dates and currency format with the table's Locale culture [e]: pass raw values, never a pre-formatted `ToString()` |
| Plural | `{0:plural:…}` or `{0:p:…}`, forms separated by `\|`, e.g. `{0:p:{} manzana\|{} manzanas}`. Uses the CLDR rules of the table's locale; a format option such as `(en)` overrides. Tags zero, one, two, few, many, other; `other` is required. Russian takes three forms [f] |
| Parse errors | Smart Format Error Action defaults to ThrowError (also OutputErrorInResult, Ignore, MaintainTokens) [g]: a malformed placeholder in one translation throws at runtime in that locale only |

Unverified: whether synchronous `StringDatabase.GetLocalizedString` forces `WaitForCompletion` before initialization (and so fails on WebGL); what an entry not marked Smart renders for `{...}`; the delegate type of `SelectedLocaleChanged` (`Action<Locale>` assumed).
