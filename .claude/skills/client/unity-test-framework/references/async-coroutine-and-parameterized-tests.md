# Async, Coroutine & Parameterized Tests

Source: [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html), async tests manual page (`reference-async-tests.html`), [`UnityTestAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityTestAttribute.html), [`IEditModeTestYieldInstruction`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html), [`ParameterizedIgnoreAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.ParameterizedIgnoreAttribute.html).

## Coroutine tests — `[UnityTest]`

See [attributes-reference.md](attributes-reference.md) for the attribute itself and its two canonical examples. The key mental model: a `[UnityTest]` method returning `IEnumerator` behaves as a real coroutine in Play Mode, and as a step through `EditorApplication.update` in Edit Mode.

## Async `Task`-based tests (added in 2.0)

Test methods can be `async Task` instead of a plain synchronous method or an `IEnumerator` coroutine:

```csharp
[Test]
public async Task MakeBreakfast_InTheMorning_IsEdible()
{
    // test implementation
}
```

**Execution model (verbatim):** "Async code is run on the main thread and Unity Test Framework will `await` it by checking if the task is done on each update for Play Mode or on each `EditorApplication.update` outside Play Mode." So an `async Task` test is still driven by Unity's own update pump, not a separate thread pool — it does not give you true background-thread concurrency by itself, only the ability to `await` other awaitables (I/O, other `Task`s) without blocking the test method's caller.

Typical pattern shown in the docs: kick off multiple `Task`s without blocking, then use `Task.WhenAny()` to await and process each as it completes, logging progress — the same idiom Microsoft's own async docs use, not something UTF-specific beyond the fact that the test method itself can be `async Task`.

This feature was tagged experimental at the time this skill was authored (docs version `2.0.1-exp.2`) — validate current async-test behavior (timeout semantics, exception propagation) against whatever UTF version the project actually has installed, and don't assume feature-parity with `[UnityTest]` coroutine tests (e.g. `[Timeout]` interaction with `async Task` tests isn't separately documented here — it's inherited from plain NUnit, not restated as Unity-specific behavior anywhere in this manual).

## Parameterized tests

Supported NUnit attributes for a plain `[Test]`: **`[TestCase]`** and **`[ValueSource]`**.

**Critical limitation (verbatim):** "With a `UnityTest` only `ValueSource` is supported." — a `[UnityTest]` coroutine test cannot use `[TestCase]`/`[TestCaseSource]` for parameterization, only `[ValueSource]`.

```csharp
static int[] values = new int[] { 1, 5, 6 };

[UnityTest]
public IEnumerator MyTestWithMultipleValues([ValueSource(nameof(values))] int value)
{
    yield return null;
}
```

`ParameterizedIgnoreAttribute` lets you skip a specific parameterized test case based on the arguments it was invoked with, rather than ignoring the whole parameterized test:

```csharp
// Conceptual usage — check the current NUnit/UTF version's exact overload
// before relying on a specific constructor signature; the manual page
// links to the API page without an inline usage sample.
[UnityTest]
[ParameterizedIgnore(typeof(MyTests), nameof(MyTests.MyTestWithMultipleValues))]
public IEnumerator MyTestWithMultipleValues([ValueSource(nameof(values))] int value)
{
    yield return null;
}
```

**Known limitation to combine with the above:** runtime-generated parameterized-test arguments don't function properly in this package (see [getting-started-and-workflows.md](getting-started-and-workflows.md)'s Known Limitations) — build parameter sources from compile-time-known static data (a `static` array/field, as in the example above), not data computed at test-discovery time from something only available at runtime.

## Custom Edit Mode yield instructions

`UnityEngine.TestTools.IEditModeTestYieldInstruction` — implement this to write your own multi-frame Edit Mode yield instruction. Members: `ExpectDomainReload` (bool), `ExpectedPlaymodeState` (bool), `Perform()`.

Four built-in implementations, all in `UnityEngine.TestTools`:
- **`EnterPlayMode`** — yield this from an Edit Mode `[UnityTest]` to switch into Play Mode mid-test.
- **`ExitPlayMode`** — the inverse, switch back to Edit Mode.
- **`RecompileScripts`** — wait for a script recompilation to complete.
- **`WaitForDomainReload`** — wait through a domain reload.

```csharp
[UnityTest]
public IEnumerator PlayOnAwakeDisabled_DoesntPlayWhenEnteringPlayMode()
{
    var videoPlayer = PrefabUtility.InstantiatePrefab(
        m_VideoPlayerPrefab.GetComponent<VideoPlayer>()) as VideoPlayer;

    videoPlayer.playOnAwake = false;

    yield return new EnterPlayMode();

    var videoPlayerGO = GameObject.Find(m_VideoPlayerPrefab.name);

    Assert.IsFalse(videoPlayerGO.GetComponent<VideoPlayer>().isPlaying);

    yield return new ExitPlayMode();

    Object.DestroyImmediate(GameObject.Find(m_VideoPlayerPrefab.name));
}
```

**Guardrail — `GameObject.Find` in this example is intentional, not a rule violation.** `performance-and-algorithms.md`'s "never use `Find`/`FindObjectOfType` at runtime" rule targets **shipped production hot-path code**. Test code under this skill is never shipped and is not a per-frame hot path — using `GameObject.Find`/`Object.FindObjectOfType` to locate a scene object spawned inside a Play Mode test is an accepted, common UTF idiom (Unity's own docs use it), not a violation. Don't let this precedent leak into `Game.Client.*`/`Game.Core.*` production code, and don't cite this example to justify `Find` calls outside test assemblies.
