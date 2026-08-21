# Execution Order, Setup and Cleanup — the pipeline and domain reloads

Sources: [Setup and cleanup at build time](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-setup-and-cleanup.html), [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html), [SetUp and TearDown](https://docs.nunit.org/articles/nunit/technical-notes/usage/SetUp-and-TearDown.html).
Covers: SKILL.md §4 — **"Settle the execution order before debugging a setup interaction"**.

The exact order in which Unity's hooks and NUnit's own interleave, and what a
domain reload does to each. Most reports of a fixture behaving unpredictably
resolve here rather than in the code under test.

## Ordered pipeline around one test

| Step | Hook | Source |
|---|---|---|
| 1 | NUnit context-applying attributes | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 2 | Outer Unity test action, before phase | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 3 | Unity setup methods | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 4 | NUnit setup and teardown wrappers | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 5 | NUnit setup methods | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 6 | NUnit action attributes, before phase | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 7 | NUnit test-method wrappers | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 8 | The test method itself | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 9 | NUnit action attributes, after phase | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 10 | NUnit teardown methods | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 11 | Unity teardown methods | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| 12 | Outer Unity test action, after phase | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |

| Rule | Consequence | Source |
|---|---|---|
| Unity setup runs before NUnit setup | Anything NUnit setup depends on must not be established by Unity setup after it, which is the opposite of the intuitive reading | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| Inheritance direction | NUnit setup runs base to derived and teardown derived to base, unchanged by this package | [SetUp and TearDown](https://docs.nunit.org/articles/nunit/technical-notes/usage/SetUp-and-TearDown.html) |
| Outer actions bracket everything | They are the outermost pair, so they are where entering and leaving Play Mode around a whole test belongs | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |

## Domain reloads

| Hook | Behaviour after a reload | Source |
|---|---|---|
| NUnit setup and one-time setup | Re-run before the code that triggered the reload continues | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |
| Unity setup | Does not re-run; if it was the hook that triggered the reload, only the code after its yield continues | [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) |

**Critical caveat**: this asymmetry is the sharpest edge in the framework.
State established before the yield in a Unity setup is gone after the reload
and is not re-established, while an NUnit setup beside it runs again. A
fixture that looks half-initialised is this, not a race.

## Build-time setup and cleanup

| Interface and attribute | What it decides | Source |
|---|---|---|
| Prebuild setup | Runs before the test Player is built, which is the only place to stage assets or files a Player run will need | [Setup and cleanup at build time](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-setup-and-cleanup.html) |
| Post-build cleanup | Runs after the build, and is what keeps a staged asset from being committed or shipped by accident | [Setup and cleanup at build time](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-setup-and-cleanup.html) |
| Scope | Attached per test or per fixture, so an expensive stage can be limited to the tests that need it rather than every run | [Setup and cleanup at build time](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-setup-and-cleanup.html) |
