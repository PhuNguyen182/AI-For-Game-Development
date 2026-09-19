# Root Links — Unity Test Framework 2.0

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to `com.unity.test-framework@2.0`, an
experimental release whose manual is missing pages that exist in 1.x. This
package is a customised NUnit integration, so plain NUnit attributes and
assertion style come from NUnit's own documentation and are deliberately not
restated here.

## Roots

| Root | Holds | Source |
|---|---|---|
| Manual | Workflows, execution order, command line, version 2.0 changes | [Test Framework overview](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/index.html) |
| Feature hub | Links from every feature to its manual or API page | [Test Framework features](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/utf-features.html) |
| `UnityEngine.TestTools` | Authoring attributes, assertions, comparers — Editor and Player | [UnityEngine.TestTools](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.html) |
| `UnityEditor.TestTools` | Editor-only build-modification attributes for the test Player | [UnityEditor.TestTools](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.html) |
| `UnityEditor.TestTools.TestRunner.Api` | Programmatic test running, Editor-only | [TestRunner.Api](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.html) |
| `UnityEngine.TestRunner` | The low-level callback pair that also runs inside a built Player | [UnityEngine.TestRunner](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.html) |

## Pages that do not exist at this version

| Expected page | Where the content actually lives | Source |
|---|---|---|
| A manual page for custom assertions | The log assertion API page | [LogAssert](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.LogAssert.html) |
| A manual page for conditional ignore | The attribute's own API page | [ConditionalIgnoreAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.ConditionalIgnoreAttribute.html) |
| A manual page for custom yield instructions | The interface's API page | [IEditModeTestYieldInstruction](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html) |

A missing manual page here means the page moved, not that the feature was
removed — check the API page before concluding a capability does not exist.

## NUnit, consulted rather than restated

| Subject | Source |
|---|---|
| Core attributes and assertions this package extends | [NUnit documentation](https://docs.nunit.org/) |
| Parameterized test sources | [Parameterized tests](https://docs.nunit.org/articles/nunit/technical-notes/usage/Parameterized-Tests.html) |
| Setup and teardown semantics this package interleaves with | [SetUp and TearDown](https://docs.nunit.org/articles/nunit/technical-notes/usage/SetUp-and-TearDown.html) |
| The results schema the command line writes | [Test result XML format](https://docs.nunit.org/articles/nunit/technical-notes/usage/Test-Result-XML-Format.html) |

Keep the `@2.0` segment when following any link from this skill. Read the
installed version from `Packages/manifest.json` and substitute it if it
differs, since this release's page set is not identical to 1.x's.
