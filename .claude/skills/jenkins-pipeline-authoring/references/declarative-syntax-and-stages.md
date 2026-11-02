# Declarative Syntax and Stages

Sources: [a] book/pipeline/syntax/, [b] pipeline/steps/workflow-basic-steps/, [c] pipeline/steps/ plugin pages — paths below the SKILL.md `Docs:` base.

Directives sit in a fixed order inside `pipeline { }`; a misplaced one is rejected in seconds, not forty minutes into a build.

Skeleton: [Jenkinsfile](../scripts/Jenkinsfile) (directive order, `options`, `parameters`, `triggers`, per-stage agents, `post`).

## Directives [a]

| Directive | Fact that decides |
|---|---|
| `agent` | `none` at top level forces per-stage agents; correct for multi-platform |
| `options` | `timeout`, `disableConcurrentBuilds`, `buildDiscarder`, `timestamps`, `retry`, `skipDefaultCheckout`; top level = whole run, or inside one `stage` |
| `parameters` | `params.NAME`; a `password` parameter is a typed value, not a credential |
| `triggers` | `cron`, `pollSCM`; `H` spreads load instead of firing at :00 |
| `environment` | At stage level applies to that stage only |
| `when` | `branch`, `expression`, `changeset`, `allOf`/`anyOf`/`not`; skips without failing |
| `parallel` | Sibling stages; add `failFast true` when one failure makes the rest pointless |
| `post` | `always`, `success`, `failure`, `unstable`, `changed`, `cleanup` (runs last) |

## Bounding a run

| Option | Prevents |
|---|---|
| `timeout` | A hung batchmode editor holding an agent; default is no limit |
| `disableConcurrentBuilds()` | The same job racing itself over a workspace or licence seat |
| `buildDiscarder(logRotator(...))` | Retained artifacts filling the controller disk, which stops every job |
| `retry(n)` | Reserve for a flaky network step; on a build step it reruns a deterministic failure |

## The human gate

```groovy
stage('Distribute to testers') {
    steps {
        timeout(time: 30, unit: 'MINUTES') {            // unanswered prompt must release the agent
            input message: 'Distribute this build to the QA group?', ok: 'Distribute'
        }
        // upload step, per `firebase-app-distribution`
    }
}
```

**Caveat:** an un-timed `input` holds its executor indefinitely. Place it before the outward action, never after.

## Environment values

`env.BUILD_NUMBER` (version code / iOS build number, per `unity-batchmode-cli`), `env.BRANCH_NAME` (multibranch), `env.GIT_COMMIT`, `env.WORKSPACE` (`-projectPath`), `currentBuild.result` (inside `post`).

## Plugins behind the steps [b][c]

| Step | Plugin |
|---|---|
| `withCredentials` | Credentials Binding |
| `lock`, `milestone` | Lockable Resources, Pipeline Milestone |
| `junit` | JUnit |
| `archiveArtifacts`, `stash`, `unstash`, `input`, `timeout`, `retry` | Pipeline: Basic Steps |
| `cleanWs` | Workspace Cleanup |
| `sh` | Pipeline: Nodes and Processes |

State the plugin dependencies in the pipeline's own documentation; on a fresh controller a missing plugin reads as a syntax error.
