# Coroutine, Async and Parameterized Tests — spanning frames and multiplying cases

Sources: [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html), [UnityTestAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityTestAttribute.html), [IEditModeTestYieldInstruction](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html), [What's new in 2.0](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/whats-new.html).
Covers: SKILL.md §4 — **"Reach for a coroutine test only when the assertion genuinely spans frames"**, **"Parameterize with the source the chosen test attribute actually supports"**.

The three ways a test can outlive a single call, and the parameterization
rules that differ from plain NUnit. Which mode the test runs in is settled in
[getting-started-and-workflows.md](getting-started-and-workflows.md).

## Tests that span time

| Form | What it buys | Use when | Source |
|---|---|---|---|
| Plain test | Runs and returns inside one call | The assertion holds immediately — the default, and cheaper than the alternatives | [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html) |
| Coroutine test | Yields between frames, and in Edit Mode can yield the framework's own instructions | Physics has to step, an animation has to advance, or a state machine ticks over several frames | [UnityTestAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityTestAttribute.html) |
| Async task test | Awaits production code that is itself asynchronous, without wrapping it in a coroutine | The code under test returns a task, added in version 2.0 | [What's new in 2.0](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/whats-new.html) |

**Critical caveat**: a same-frame assertion wrapped in a frame yield is slower
and no more correct. The yield is justified by something that must actually
advance, not by the test happening to live in Play Mode.

## Edit Mode yield instructions

| Instruction | Effect | Source |
|---|---|---|
| Enter Play Mode | Transitions the Editor into play from inside an Edit Mode test, which triggers a domain reload — see [execution-order-and-setup-cleanup.md](execution-order-and-setup-cleanup.md) | [IEditModeTestYieldInstruction](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html) |
| Exit Play Mode | Transitions back out, and belongs in the matching teardown so a failed test does not leave the Editor in play | [IEditModeTestYieldInstruction](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html) |
| Recompile scripts | Forces a compilation pass, for testing code that reacts to compilation | [IEditModeTestYieldInstruction](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html) |
| Wait for domain reload | Blocks until a reload triggered elsewhere finishes, which is how a test avoids asserting against a half-reloaded domain | [IEditModeTestYieldInstruction](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html) |
| The interface itself | Implementing it produces a custom instruction, for a wait condition the built-in set does not express | [IEditModeTestYieldInstruction](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html) |

## Parameterization

| Source | Works with | Consequence | Source |
|---|---|---|---|
| Test case attribute | Plain tests only | Ignored on a coroutine test, so cases appear authored and never run while the suite still reports green | [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html) |
| Test case source attribute | Plain tests only | Same silent outcome on a coroutine test | [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html) |
| Value source attribute | Plain and coroutine tests | The only parameterization a coroutine test accepts | [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html) |
| Preserved values attribute | Plain and coroutine tests | Literal arguments in a form that survives code stripping in a Player build | [PreservedValuesAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.PreservedValuesAttribute.html) |

| Rule | Consequence | Source |
|---|---|---|
| Arguments computed at discovery time | Unreliable in this package — build cases from static, compile-time-known data instead | [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html) |
| Skipping one case | Use the parameterized ignore attribute rather than branching inside the test body, so the skipped case is reported as skipped rather than as a pass | [Custom attributes](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-custom-attributes.html) |
