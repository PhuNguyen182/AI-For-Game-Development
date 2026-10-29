# Artifacts, Test Reports and Notifications

Sources: [a] pipeline/steps/junit/, [b] pipeline/steps/workflow-basic-steps/, [c] book/pipeline/syntax/ (post) — below the SKILL.md `Docs:` base.

Jenkins calls a build successful when nothing was tested, produced or published unless told otherwise.

## Unity writes NUnit 3, not JUnit

`-testResults` output (see `unity-test-framework`) is NUnit 3 XML; `junit` parses JUnit XML, and the mismatch surfaces as "no test results found".

| Route | How |
|---|---|
| xUnit plugin, NUnit-3 type | Reads Unity's XML directly; fewest parts if installed |
| Convert, then `junit` | Transform NUnit 3 to JUnit XML in a step [a] |

Check which publisher the controller has and state the dependency. The empty-results rule below applies to both.

## Publishing

```groovy
post {
    always {
        junit testResults: 'ci/results/*.xml', allowEmptyResults: false, keepLongStdio: true
        archiveArtifacts artifacts: 'ci/logs/**', allowEmptyArchive: true
    }
    success {
        archiveArtifacts artifacts: 'build/**/*.apk, build/**/*.aab', fingerprint: true, onlyIfSuccessful: true
    }
}
```

| Parameter | Set | Why |
|---|---|---|
| `allowEmptyResults` | `false` | Default tolerance turns a crashed test stage green |
| `keepLongStdio` | `true` | Unity writes the failure detail to stdout; truncated by default |
| `fingerprint` | `true` | Traces an artifact to its run |
| `onlyIfSuccessful` | `true` for build output | A failed run's partial artifact gets installed |
| `allowEmptyArchive` | `true` only for logs | A missing artifact should fail the run |

## Build status [c]

| Result | Set by | Downstream |
|---|---|---|
| `SUCCESS` | nothing failed | `post { success }` |
| `UNSTABLE` | a test publisher finding failed tests, not a failing step | `post { failure }` does **not** run; `post { unstable }` does |
| `FAILURE` | non-zero step exit, or the publisher objecting | `post { failure }` |
| `ABORTED` | timeout, manual stop, unanswered `input` | handle in `always` |

**Caveat:** a failing test gives `UNSTABLE`, so a distribution stage guarded only against `FAILURE` uploads a build with failed tests. Guard on `currentBuild.result == 'SUCCESS'`, or fail the run on the test stage's exit status.

## Notifications

- Notify from `post` on `failure` **and** `unstable`; add `changed` so a fix is reported too.
- Include run URL, branch, commit and artifact version; never a credential or secret-file content.

## Not evidence

- An artifact at a path (may be the previous run's, per `unity-batchmode-cli`).
- A stage skipped by `when`: skipped is not passed; the report says which.
- A publisher that found no results, whatever the status.
- A green run whose test stage was disabled (a weakened assertion, per `qa-standards`).
