# Platform, Build and Command Line — Player runs and headless CI

Sources: [Test Framework command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html), [Running Play Mode tests in a player](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-playmode-test-standalone.html), [UnityPlatformAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityPlatformAttribute.html), [RequirePlatformSupportAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.RequirePlatformSupportAttribute.html), [TestPlayerBuildModifierAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestPlayerBuildModifierAttribute.html), [Test result XML format](https://docs.nunit.org/articles/nunit/technical-notes/usage/Test-Result-XML-Format.html).
Covers: SKILL.md §4 — **"Scope a CI run with filters, and pair the run flag with batch mode"**.

How a run is scoped, where it executes, and what it writes out. Producing a
real platform build is `build-run-engineer`'s work on the GD's explicit
request — everything here is the configuration that role executes, not an
instruction to run it from this skill.

## Where the tests execute

| Location | What it exercises | Source |
|---|---|---|
| Editor | The fastest route, and the only one for Edit Mode; it does not exercise platform-specific runtime behaviour | [Running Play Mode tests in a player](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-playmode-test-standalone.html) |
| Standalone Player | Builds and runs Play Mode tests in an actual player, which is where scripting-backend and platform differences finally appear | [Running Play Mode tests in a player](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-playmode-test-standalone.html) |
| Build modifier | Adjusts the Player build options, or splits building from running so the build can be produced on one machine and run on another | [TestPlayerBuildModifierAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestPlayerBuildModifierAttribute.html) |

## Platform gating

| Attribute | Gates on | Source |
|---|---|---|
| Platform restriction | The platform the test is currently running on | [UnityPlatformAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityPlatformAttribute.html) |
| Platform support requirement | Whether the Editor has build support for a platform installed, which is what stops a CI agent failing on a module it was never given | [RequirePlatformSupportAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.RequirePlatformSupportAttribute.html) |

## Command-line surface

| Argument | What it decides | Source |
|---|---|---|
| Run tests | Required — nothing runs without it, whatever else is passed | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Batch mode | Removes the need for interactive input, which is what makes the run unattended; pair it with the run flag every time | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Test platform | Edit Mode, Play Mode, or a build target; it defaults to Edit Mode, so an unspecified platform silently runs the wrong half of the suite | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Test filter | Names or a regular expression against the full test name, with negation and parameterized-case syntax supported | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Test category | Category list, also with negation; combined with a filter, only tests matching both run — which is how an over-scoped run silently becomes an empty one | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Assembly names and assembly type | Restricts the run to named assemblies, or to Editor-only against Editor-and-platform assemblies | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Test results path | Where the report is written; without it there is nothing for CI to consume | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Run synchronously | Runs Edit Mode tests inside a single Editor update, and thereby excludes every multi-frame test from the run | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Player heartbeat timeout | How long the Editor waits for a Player run to report in before giving up — the setting behind an unexplained CI hang on a slow device | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Build player path | Where the test Player is written, rather than a temporary directory that CI cannot collect from | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |
| Ordered test list file | Runs named tests in an exact order, for reproducing an order-dependent failure | [Command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html) |

**Critical caveat**: the filter and the category argument intersect rather
than union. Passing both with no overlap produces a successful run of zero
tests, which reads as everything passing.

| Output | Format | Source |
|---|---|---|
| Results file | Standard NUnit result XML, so any CI reporter that understands NUnit consumes it without a Unity-specific parser | [Test result XML format](https://docs.nunit.org/articles/nunit/technical-notes/usage/Test-Result-XML-Format.html) |
