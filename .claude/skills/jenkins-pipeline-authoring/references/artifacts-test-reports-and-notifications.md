# Artifacts, Test Reports and Notifications — what a run publishes

Source: [JUnit plugin](https://www.jenkins.io/doc/pipeline/steps/junit/), [Pipeline: Basic Steps](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/), [Pipeline syntax — post](https://www.jenkins.io/doc/book/pipeline/syntax/).
Covers: SKILL.md §4 — **"Publish the test report as a real result set, and treat an empty one as a failure"**, **"Collect logs and reports from `post { always }`, and artifacts only on success"**.

What leaves a run, and how the run's own result is decided. The trap this file exists to close: Jenkins is
willing to call a build successful when nothing was tested, nothing was produced, and nothing was published —
every one of those has to be objected to explicitly.

## Unity's test XML is NUnit, not JUnit

Unity's `-testResults` writes **NUnit 3** XML, per `unity-test-framework`. The `junit` step parses JUnit XML.
They are different schemas, and the mismatch usually surfaces as "no test results found" rather than as a
parse error.

| Route | How | Source |
|---|---|---|
| xUnit plugin with the NUnit-3 type | Reads Unity's XML directly; the fewest moving parts when the plugin is installed | [Jenkins plugins](https://plugins.jenkins.io/) |
| Convert, then `junit` | Transform NUnit 3 to JUnit XML in a step, then publish the converted file | [JUnit plugin](https://www.jenkins.io/doc/pipeline/steps/junit/) |

Check which publisher the controller has before writing the stage, and state the dependency in the pipeline's
documentation. Either way, the empty-results rule below applies identically.

## Publishing results

```groovy
post {
    always {
        junit testResults: 'ci/results/*.xml',
              allowEmptyResults: false,        // an empty result set is a failed run, not a passed one
              keepLongStdio: true              // Unity test output is long and is the evidence
        archiveArtifacts artifacts: 'ci/logs/**', allowEmptyArchive: true
    }
    success {
        archiveArtifacts artifacts: 'build/**/*.apk, build/**/*.aab', fingerprint: true, onlyIfSuccessful: true
    }
}
```

| Parameter | Set it to | Why |
|---|---|---|
| `allowEmptyResults` | `false` | The default tolerance turns a crashed test stage into a green build — the single most common false pass in a Unity pipeline |
| `keepLongStdio` | `true` | Unity writes the useful part of a failure to stdout, and the publisher truncates it by default |
| `fingerprint` (archive) | `true` | Ties an artifact to the run that produced it, so a build found later can be traced back |
| `onlyIfSuccessful` (archive) | `true` for build output | A failed run's partial artifact is worse than none — someone will find it and install it |
| `allowEmptyArchive` | `true` **only** for logs | A missing log should not fail a run that already failed; a missing artifact should |

## Build status, and the one everybody forgets

| Result | Set by | What it means downstream |
|---|---|---|
| `SUCCESS` | Nothing failed | `post { success }` runs |
| `UNSTABLE` | **A test publisher finding failed tests** — not by a failing step | `post { failure }` does **not** run; `post { unstable }` does |
| `FAILURE` | A step exiting non-zero, or the publisher objecting | `post { failure }` runs |
| `ABORTED` | Timeout, manual stop, or an unanswered `input` | Neither success nor failure blocks run — handle in `always` |

A failing test therefore produces `UNSTABLE`, and a distribution stage guarded only against `FAILURE` will
happily upload a build whose tests failed. Guard delivery on `currentBuild.result` being `SUCCESS`, or place
the test stage ahead of it and let the stage's own exit status fail the run.

## Reporting out

| Rule | Reason |
|---|---|
| Notify from `post`, covering `failure` **and** `unstable` | Reporting only on failure hides every failed test |
| Include the run URL, the branch, the commit, and the artifact version | A notification nobody can act on is noise, and noise gets muted |
| Never include a credential, a token, or the contents of a secret file | A chat channel is a permanent, searchable, widely-read log |
| Report a fixed run too (`post { changed }`) | Otherwise a channel only ever carries bad news and stops being read |

## What never counts as evidence

- An artifact existing at a path — it may be the previous run's, per `unity-batchmode-cli`.
- A stage that was skipped by `when` — skipped is not passed, and the report must say which it was.
- A publisher that found no results, whatever the build status ended up as.
- A green run on a job whose test stage was disabled to make it green; that is `verification-standards.md`'s
  weakened assertion, and it is a finding rather than a fix.