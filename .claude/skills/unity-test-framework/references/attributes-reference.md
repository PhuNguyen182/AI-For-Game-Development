# Attributes Reference — Unity's additions on top of NUnit

Sources: [Custom attributes](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-custom-attributes.html), [UnityEngine.TestTools](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.html), [UnityEditor.TestTools](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.html), [UnityEngine.TestRunner](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.html), [UnityTestAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityTestAttribute.html).
Covers: SKILL.md §4 — **"Pick the attribute from Unity's own catalog rather than assuming an NUnit equivalent applies"**.

What each Unity-authored attribute changes about how a test runs, and which
NUnit attributes do not survive the crossing. Plain NUnit attributes that
behave normally here are deliberately absent — consult NUnit's own docs for
those, per [root-links.md](root-links.md).

## Test declaration

| Attribute | What it changes | Source |
|---|---|---|
| `UnityTest` | Turns the test into a coroutine that can skip frames and yield Unity instructions — the only way an assertion spans more than one frame | [UnityTestAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityTestAttribute.html) |
| `UnitySetUp`, `UnityTearDown` | Setup and teardown that may yield; they interleave with NUnit's own hooks in a fixed order and do not survive a domain reload the same way — see [execution-order-and-setup-cleanup.md](execution-order-and-setup-cleanup.md) | [Custom attributes](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-custom-attributes.html) |
| `RequiresPlayMode` | Declares, at assembly, fixture or test scope, whether the scope needs Play Mode — the mechanism that removed the need for separate assemblies per mode | [Custom attributes](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-custom-attributes.html) |

## Skipping

| Attribute | Skips based on | Source |
|---|---|---|
| `ConditionalIgnore` | A condition registered at runtime, so the same test can be skipped on a machine or configuration that cannot support it | [ConditionalIgnoreAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.ConditionalIgnoreAttribute.html) |
| `ParameterizedIgnore` | Specific argument values, so one case of a parameterized test is skipped while the rest run | [Custom attributes](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-custom-attributes.html) |
| `UnityPlatform` | The platform the test is running on | [UnityPlatformAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityPlatformAttribute.html) |
| `RequirePlatformSupport` | Whether Player build support for a platform is installed — a different question from which platform is running | [RequirePlatformSupportAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.RequirePlatformSupportAttribute.html) |

**Critical caveat**: the manual's own attribute table omits the runtime
conditional-ignore attribute even though it ships in the API. Treat the
namespace pages, not that table, as the authoritative catalog.

## Build and run hooks

| Attribute | What it changes | Source |
|---|---|---|
| `PrebuildSetup`, `PostBuildCleanup` | Run code against the Editor or the file system around building the test Player — see [execution-order-and-setup-cleanup.md](execution-order-and-setup-cleanup.md) | [Custom attributes](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-custom-attributes.html) |
| `TestPlayerBuildModifier` | Modifies the Player build options, or splits build from run; it lives in the Editor tools namespace rather than the runner API namespace, which is the usual lookup mistake | [TestPlayerBuildModifierAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestPlayerBuildModifierAttribute.html) |
| `TestRunCallback` | Subscribes a type to test progress at assembly scope, through the callback interface that also works inside a Player — see [scripting-api-test-runner-api.md](scripting-api-test-runner-api.md) | [TestRunCallbackAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.TestRunCallbackAttribute.html) |

## Logging and values

| Attribute | What it changes | Source |
|---|---|---|
| `TestMustExpectAllLogs` | Every log entry must be expected or the test fails, which converts stray logging into a failure instead of noise | [TestMustExpectAllLogsAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.TestMustExpectAllLogsAttribute.html) |
| `PreservedValues` | Supplies literal arguments for one parameter, in a form that survives code stripping in a Player build where NUnit's own equivalent may not | [PreservedValuesAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.PreservedValuesAttribute.html) |

## NUnit attributes that do not survive

| Attribute | Behaviour here | Source |
|---|---|---|
| `Repeat` | Not supported in combination with the coroutine test attribute | [UnityTestAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityTestAttribute.html) |
| `Retry` | Throws in Play Mode rather than retrying | [UnityTestAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityTestAttribute.html) |
| `TestCase` and `TestCaseSource` | Unsupported on the coroutine test attribute, which accepts only the value-source form — see [async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md) | [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html) |
