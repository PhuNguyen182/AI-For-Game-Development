# Sequences — Composing Multiple Tweens

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php).
Covers: SKILL.md §4 — "Compose multi-step animation through a Sequence, not chained coroutines".

## Creating a Sequence

```csharp
Sequence seq = DOTween.Sequence();
seq.Append(transform.DOMoveX(45, 1));                                   // added after current duration
seq.Append(transform.DORotate(new Vector3(0, 180, 0), 1));               // added after the move
seq.Insert(0, transform.DOScale(new Vector3(3, 3, 3), seq.Duration()));  // overlaps from time 0
seq.PrependInterval(1);                                                 // delay before the whole sequence starts
```

| Method | Effect |
|---|---|
| `Append(tween)` | Adds a tween to play after everything already in the Sequence finishes |
| `Insert(atPosition, tween)` | Places a tween at an explicit time offset — the mechanism for overlapping tweens deliberately |
| `Join(tween)` | Adds a tween starting at the same time as the last one added — the common case of "play these two together" |
| `Prepend(tween)` | Inserts a tween before the Sequence's current start, shifting everything else later |
| `AppendCallback(action)` | Fires a plain callback at that point in the Sequence — see the note below on when this is (and isn't) the right tool |
| `AppendInterval(duration)` / `PrependInterval(duration)` | Adds a pure time gap with no tween, at the end/start |
| `InsertCallback(atPosition, action)` | Fires a callback at an explicit time offset |

A Sequence can nest other Sequences — build a reusable sub-sequence once
and `Append`/`Join`/`Insert` it into a larger one, rather than flattening
every step into one giant Sequence by hand.

## `AppendCallback` vs `async`/`await`

`AppendCallback`/`InsertCallback` are fine for a simple, fire-and-forget
side effect timed within the Sequence (playing a sound, spawning a
particle). For anything with its own branching, error handling, or a
callback that itself needs to await something (an Addressables load, a
network call), prefer `async`/`await` around the Sequence instead —
`await sequence.AsyncWaitForCompletion()` (or the UniTask equivalent, per
[async-and-unitask-integration.md](async-and-unitask-integration.md)) up to
a point, then run the async continuation, rather than nesting complex
logic inside `AppendCallback`. Exceptions thrown inside a plain callback
propagate differently than an `async` method's would — don't rely on a
Sequence callback for anything that needs proper exception propagation to
the caller.
