# Text and TextMesh Pro Animation

Sources (under the Docs base): text-animation, textmesh-pro-character-animation, integration-zstring; source `Runtime/LMotion.CreateString.cs`, `Extensions/TextMeshPro/LitMotionTextMeshProExtensions.cs`, `MotionBuilderExtensions.cs`.

Two independent features: a string tween (`LMotion.String`) and a numeric motion bound to a text display (`BindToText`).

## String motions

`LMotion.String.Create32Bytes/64/128/512/4096Bytes` produce `FixedString{N}Bytes` with `StringOptions`. `FixedString` has fixed capacity: pick the smallest size that fits the longest string.

```csharp
LMotion.String.Create128Bytes("", "<color=red>Zero</color> Allocation Tween!", 5f)
    .WithRichText().WithScrambleChars(ScrambleMode.Lowercase).BindToText(text);
```

| Method | Fact |
|---|---|
| `WithRichText(bool = true)` | Advances past rich-text tags instead of counting them as characters |
| `WithScrambleChars(ScrambleMode)` | Fills unrevealed characters: `None` (default, blank), `Uppercase`, `Lowercase`, `Numerals`, `All` |
| `WithScrambleChars(FixedString64Bytes)` | Same, from a custom character set |
| `WithRandomSeed(uint)` | Deterministic scramble |

**Caveat:** the docs page calls this `WithScrambleMode`; the shipped API (`MotionBuilderExtensions.cs`) is `WithScrambleChars`.

## Numeric readout

`BindToText` takes `int`/`long`/`float` motions and targets `Text` or `TMP_Text`; the optional format string is `string.Format`-style.

```csharp
LMotion.Create(0, 999, 2f).BindToText(text);
LMotion.Create(0f, 100000f, 2f).BindToText(text, "{0:N2}");
```

**Caveat:** the formatted overload uses `string.Format`, which boxes and allocates every update. With ZString installed LitMotion uses `ZString.Format()` (and `SetTextFormat()` for `TMP_Text`), which is allocation-free; add `LITMOTION_SUPPORT_ZSTRING` if ZString came via `.unitypackage`.

## TMP per-character

Index into `TMP_Text.textInfo`: `BindToTMPChar{Color,Position,Rotation,EulerAngles,Scale}(text, charIndex)` with the usual axis families (`Color` has `R/G/B/A`; `BindToTMPCharScaleXYZ(float)` is uniform), plus `BindToTMPChar<TValue,...>(text, charIndex, TMPCharacterMotionUpdateAction<TValue>)` for custom. Text-level: `BindToFontSize`, `BindToColor`, `BindToCharacterSpacing`, `BindToWordSpacing`, `BindToLineSpacing`, `BindToParagraphSpacing`, `BindToMaxVisibleCharacters/Lines/Words`.

```csharp
for (int i = 0; i < text.textInfo.characterCount; i++)
    LMotion.Create(Color.white, Color.red, 1f).WithDelay(i * 0.1f).BindToTMPCharColor(text, i);
```

**Caveat:** per-character state reverts to mesh defaults when the text is rewritten or `ForceMeshUpdate()` is called.
