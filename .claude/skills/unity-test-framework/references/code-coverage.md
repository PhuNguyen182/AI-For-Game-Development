# Code Coverage

Package `com.unity.testtools.codecoverage`. It shows which lines the tests executed; it "does not measure the quality of tests" [m]. Use it to find missing tests and to show a test reaches a fix, never to prove behaviour.

Sources: [m] `https://docs.unity3d.com/Packages/com.unity.testtools.codecoverage@1.3/manual/`. [c] plugin skill `unity:unity-cli` → references/build-run-test.md. [s] package 1.3.0 source. [r] ran 2026-11-03: Unity 6000.0.83f1, Test Framework 1.6.0, package 1.3.0, CLI 1.0.0-beta.14, on a scratch project.

## Installed?
Read `Packages/manifest.json`, then `Packages/packages-lock.json` (transitive), for the package id [c].

| State | Do |
|---|---|
| Absent | Tests run as usual; report `Code coverage: not installed`. Never add it unasked: that is a `Packages/` change for the GD |
| Present, no Editor open | Commands below |
| Present, Editor open | `unity test` refuses the project. `Needs GD: close the Editor`, or report `not run: Editor open` |

Never switch coverage on inside a live Editor from an agent: on a Release-mode Editor the first results write opens a modal dialog [s].

## When
| Moment | Run |
|---|---|
| `/qa`, last run of `qa-automation-engineer` | Both modes, merged |
| `/fix` step 6 | The regression test alone (`--filter`) |
| Implementer, Editor closed | Optional: their own test assemblies |
| `/feature` step 4 per-implementer test run | No; it would add a Debug compile per implementer |
| Performance measurement, Player, device | Never (Traps) |

## Commands
Wipe the output directory first, then run both modes; the last run carries the report option and merges every result under the output directory [r]. `<o>` sits outside `Assets/`; the default is `<project>/CodeCoverage`, git-ignored (`git-unity-repo`).

```
F='assemblyFilters:+<Feature asmdef prefix>.*,-*.Tests.*'
unity test <project> --mode EditMode --json --output <results>/editmode.xml --coverage --coverage-output <o> \
  --coverage-options "generateAdditionalMetrics;dontClear;$F" -- -debugCodeOptimization
unity test <project> --mode PlayMode --json --output <results>/playmode.xml --coverage --coverage-output <o> \
  --coverage-options "generateHtmlReport;generateAdditionalMetrics;dontClear;$F" -- -debugCodeOptimization
```

- **Confirm it ran:** `data.coverage.enabled` is `true` in the JSON [r]; `false` means the package is missing and nothing was collected [c].
- **Regression test:** one EditMode or PlayMode run with `--filter <full test name>` and `generateHtmlReport` [r]. The figures describe that test only.
- **Burst code:** add `--burst-disable-compilation` after `--` or jobs are not fully covered [m]. The flag reached the Editor in [r]; no Burst job was measured.
- **Classic batchmode (`unity-batchmode-cli`):** `-runTests -testPlatform <mode> -debugCodeOptimization -enableCodeCoverage -coverageResultsPath <o> -coverageOptions "..."`; no `-quit` with `-runTests`.

| `-coverageOptions` | Effect |
|---|---|
| `generateHtmlReport` | `Report/index.htm`. Any report option also writes the `Summary.*` files; without one there is no `Report/` [s] |
| `generateAdditionalMetrics` | Cyclomatic Complexity and Crap Score per method [m] |
| `generateTestReferences` | "Coverage by test methods" in the HTML report [m]; not run in [r] |
| `generateAdditionalReports` | SonarQube, Cobertura, LCOV [m]; not run in [r] |
| `generateBadgeReport` | SVG and PNG badges [m]; not run in [r] |
| `dontClear` | Accumulates across sessions. Needed for the merge: on Test Framework 2.0 both modes share one folder [s] |
| `assemblyFilters:` | `+` / `-`, globs, `<all>`, `<assets>`, `<packages>`. Default is only `Assets/` assemblies, test assemblies included [m]; `-*.Tests.*` removed them [r] |
| `pathFilters:` | `+` / `-`, `*` one level, `**` recursive, applied in order [m]; use for generated code |

## Output [r]
```
<o>/<ProjectFolder>-opencov/EditMode|PlayMode/TestCoverageResults_NNNN.xml
<o>/Report/Summary.json | Summary.xml | Summary.md | index.htm | <Assembly>_<Class>.html
```
- **Test Framework 2.0+:** both modes write to `Automated/` instead of `EditMode|PlayMode/` [m][s]; not run in [r].
- **Each session writes two XML files:** all sequence points, then the visited ones. Read the merge, not one file.
- **`Summary.json`:** `summary.linecoverage`, `coveredlines`, `coverablelines`, `methodcoverage`, then per assembly and class. Class level at best.
- **Line level:** [coverage_gaps.py](../scripts/coverage_gaps.py).

## Reading it
Run [coverage_gaps.py](../scripts/coverage_gaps.py) with `--changed <base>` first: changed lines no test executed is the number that drives work. A project-wide percentage changes no decision.

| Output | Means | Do |
|---|---|---|
| `changed, not executed` | No test reached those lines | A criterion covers them → add the test, asserting the behaviour. None does → dead code or a spec gap: report it, add no test |
| `Not in results` | Assembly filtered out, or no coverable line | Check the filter; never read it as covered |
| `STALE` | Source edited after the last run | Re-run; line numbers no longer match |
| Exit 2 | No results, no sequence points, or git failed | No data; never "no gaps" |
| Regression run does not execute the fix's lines | The test does not guard this fix | Back to the test, even when it is green |
| Crap Score high or Cyclomatic Complexity above 15 (Risk Hotspots [m]) with uncovered lines | Hardest code is the untested code | Rank those cases first (`risk-based-test-planning`) |

## What a number does not prove
- **Line, not branch:** branch coverage and NPath are not implemented and always read zero [m]; `coveredbranches` was 0 in [r]. A green line does not show every arm of a condition ran.
- **Executed, not asserted:** a test with no assertion turns lines green.
- **Editor only:** the package supports code run in the Editor, not Standalone/Player [m]. A Unity 6.6 API page mentions a Player build option for desktop [m]; not run, so treat coverage as Editor-only and report no Player figure.
- **No target by default:** no percentage gate unless the GD or `docs/tech-stack.md` states one. A stated one is hard, and only ever on changed lines or named assemblies.

## Traps
| Trap | Result | Do |
|---|---|---|
| `unity test --coverage` without `-debugCodeOptimization` | The CLI does not add it [c]; a Release compile gives inaccurate coverage and a warning [m][s] | Always forward it after `--` [r] |
| Old results with `dontClear` | Accumulated stale lines inflate the merge [m] | Wipe `<o>` before the first mode |
| `--filter`, `--affected`, `--shard`, `--rerun-failed` | Subset figures | Label them; never report as the suite's |
| `--retries` | Coverage comes from the first attempt only [c] | A retry adds nothing |
| Timing or allocation test under coverage | Overhead [m] and Debug compile change the result | Pass/fail of record is the plain run; skip with `[ConditionalIgnore("IgnoreForCoverage", "<why>")]` [m], never loosen |
| Measuring performance with it on | "Adds some overhead" [m] | Never; `performance-budget-verification` |
| `ProjectSettings/Packages/com.unity.testtools.codecoverage/Settings.json` | Appears after a run [r]; not this work's change | Leave unstaged unless the GD adopts project settings |
| Report or XML published | Absolute machine paths and source in the output [r] | Internal artifact only; never committed; `.workflow/evidence/` gets a `.md` citing the numbers |
| Exclusions | `[ExcludeFromCoverage]` (`UnityEngine.TestTools`), or .NET `ExcludeFromCodeCoverage` [m], hide lines from the figure | Only generated or debug-only code, with the reason stated; never to raise a number |
