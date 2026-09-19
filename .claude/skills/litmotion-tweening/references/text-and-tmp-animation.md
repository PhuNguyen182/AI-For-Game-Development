# Text & TextMesh Pro Animation — String Motions, Numeric Formatting, Per-Character

Sources: [Text Animation](https://annulusgames.github.io/LitMotion/articles/en/text-animation.html), [TextMesh Pro Character Animation](https://annulusgames.github.io/LitMotion/articles/en/textmesh-pro-character-animation.html), [ZString](https://annulusgames.github.io/LitMotion/articles/en/integration-zstring.html), verified against [`LitMotionTextMeshProExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/TextMeshPro/LitMotionTextMeshProExtensions.cs), [`LMotion.CreateString.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LMotion.CreateString.cs).
Covers: SKILL.md §4 — **"Bind with a built-in `LitMotion.Extensions` `BindTo*` method before writing a manual `Bind()` lambda"**.

Text motions come in two independent flavors: a genuine string tween (typing
a string in) via `LMotion.String`, and a numeric motion bound to a text
component's display via `BindToText` — they can be combined but are not the
same feature.

## String motions — `LMotion.String`

| Factory | Value type | Source |
|---|---|---|
| `Create32Bytes` / `Create64Bytes` / `Create128Bytes` / `Create512Bytes` / `Create4096Bytes` | `FixedString{N}Bytes`, `StringOptions` | [`LMotion.CreateString.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LMotion.CreateString.cs) |

Pick the smallest byte size that fits the longest string the motion will
ever hold — `FixedString` is a fixed-capacity unmanaged buffer, not a
growable string.

```csharp
TMP_Text text;
LMotion.String.Create128Bytes("", "<color=red>Zero</color> Allocation <i>Text</i> Tween!", 5f)
    .WithRichText()
    .WithScrambleChars(ScrambleMode.Lowercase)
    .BindToText(text);
```

| `StringOptions` `With-` method | Effect | Source |
|---|---|---|
| `WithRichText(bool = true)` | Advances characters correctly past rich-text tags instead of counting them as visible characters | [Text Animation](https://annulusgames.github.io/LitMotion/articles/en/text-animation.html) |
| `WithScrambleChars(ScrambleMode)` | Fills not-yet-revealed characters with random ones (table below) | [`MotionBuilderExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionBuilderExtensions.cs) |
| `WithScrambleChars(FixedString64Bytes customChars)` | Same, sampling from a caller-supplied character set instead of a built-in mode | same |
| `WithRandomSeed(uint)` | Deterministic scramble randomness | same |

| `ScrambleMode` | Fills with | Source |
|---|---|---|
| `None` (default) | Nothing (blank) | [Motion Configuration](https://annulusgames.github.io/LitMotion/articles/en/motion-configuration.html) |
| `Uppercase` / `Lowercase` / `Numerals` | That character class | same |
| `All` | Upper/lower/numeral mix | same |

**Critical caveat**: the docs page names this setting `WithScrambleMode`; the shipped API is `WithScrambleChars` (confirmed in `MotionBuilderExtensions.cs`) — use the source-verified name.

## Binding a numeric motion to text — `BindToText`

For `Text`/`TMP_Text`, an `int`/`long`/`float` motion binds directly with
zero allocation via `BindToText`, with an optional format string.

```csharp
TMP_Text text;
LMotion.Create(0, 999, 2f).BindToText(text);                 // plain int display
LMotion.Create(0f, 100000f, 2f).BindToText(text, "{0:N2}");  // "{0:N2}" comma+2-decimal formatting
```

**Critical caveat**: the formatted overload calls `string.Format()` internally, which boxes the numeric value and allocates every update. Installing ZString removes this: `LitMotion` then uses `ZString.Format()` and, for `TMP_Text` specifically, `TMP_Text.SetText()` via ZString's `SetTextFormat()` extension — fully zero-allocation. Add `LITMOTION_SUPPORT_ZSTRING` to Scripting Define Symbols if ZString was imported via `.unitypackage` rather than Package Manager.

## TextMesh Pro per-character animation

Animates individual characters' color/position/rotation/scale independent of
the string content, by index into `TMP_Text.textInfo`.

| Property | Full + axis members | Source |
|---|---|---|
| Color | `BindToTMPCharColor` (`Color`), `+R/G/B/A` (`float`) | [`LitMotionTextMeshProExtensions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/Extensions/TextMeshPro/LitMotionTextMeshProExtensions.cs) |
| Position | `BindToTMPCharPosition` (`Vector3`) + `X/Y/Z/XY/YZ/XZ` | same |
| Rotation | `BindToTMPCharRotation` (`Quaternion`), `BindToTMPCharEulerAngles` (`Vector3`) + axis family | same |
| Scale | `BindToTMPCharScale` (`Vector3`) + axis family, `BindToTMPCharScaleXYZ(float)` for uniform | same |
| Custom | `BindToTMPChar<TValue,...>(text, charIndex, TMPCharacterMotionUpdateAction<TValue>)` | same |
| Text-level (not per-char) | `BindToFontSize`, `BindToColor(+RGBA)`, `BindToCharacterSpacing`, `BindToWordSpacing`, `BindToLineSpacing`, `BindToParagraphSpacing`, `BindToMaxVisibleCharacters/Lines/Words` | same |

```csharp
TMP_Text text;
for (int i = 0; i < text.textInfo.characterCount; i++)
{
    LMotion.Create(Color.white, Color.red, 1f)
        .WithDelay(i * 0.1f)
        .WithEase(Ease.OutQuad)
        .BindToTMPCharColor(text, i);

    LMotion.Punch.Create(Vector3.zero, Vector3.up * 30f, 1f)
        .WithDelay(i * 0.1f)
        .BindToTMPCharPosition(text, i);
}
```

**Critical caveat**: per-character state is preserved while the motion plays, but reverts to the mesh's defaults once the text is rewritten or `ForceMeshUpdate()` is called — the character motion does not survive a text content change.
