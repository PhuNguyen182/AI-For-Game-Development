# Declarative Syntax and Stages — the directive set a Unity pipeline uses

Source: [Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/), [Using a Jenkinsfile](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/), [Pipeline: Basic Steps](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/).
Covers: SKILL.md §4 — **"Keep the pipeline in the repository and the controller free of job logic"**, **"Bound the run before writing its first stage"**, **"Put a human between the pipeline and anything that reaches people"**.

The directives a Unity build pipeline actually uses, and what each one accepts. Declarative pipeline is a
fixed structure rather than a script: directives appear in a defined order inside `pipeline { }`, and a
directive in the wrong place is rejected before anything runs — which is the point, because that rejection
happens in seconds rather than forty minutes into a build.

## Skeleton

```groovy
pipeline {
    agent none                                     // per-stage agents; see agents-locks-and-workspaces.md
    options {
        timeout(time: 90, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '10'))
        timestamps()
    }
    parameters {
        choice(name: 'PLATFORM', choices: ['android', 'ios', 'windows'], description: 'Target to build')
        booleanParam(name: 'DEVELOPMENT_BUILD', defaultValue: true, description: 'Development configuration')
    }
    triggers { cron('H 2 * * 1-5') }               // omit entirely for a manual-only job
    stages {
        stage('Test')      { agent { label 'linux && unity' } steps { /* … */ } }
        stage('Build')     { agent { label 'linux && unity' } steps { /* … */ } }
        stage('Distribute') {
            when { expression { params.PLATFORM != 'windows' } }
            steps { /* … */ }
        }
    }
    post {
        always  { /* logs and reports */ }
        success { /* artifacts */ }
        cleanup { /* workspace */ }
    }
}
```

## Directives

| Directive | Accepts | Notes | Source |
|---|---|---|---|
| `agent` | `any`, `none`, `{ label 'x' }`, `{ docker … }` | `none` at top level forces every stage to declare its own — correct for a multi-platform pipeline | [Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) |
| `options` | `timeout`, `disableConcurrentBuilds`, `buildDiscarder`, `timestamps`, `retry`, `skipDefaultCheckout` | Applies to the whole run at top level, or to one stage inside `stage { options { } }` | same |
| `parameters` | `string`, `booleanParam`, `choice`, `password` | Reachable as `params.NAME`. A `password` parameter is not a credential — it is a value someone typed, with none of the storage guarantees | same |
| `triggers` | `cron('H 2 * * *')`, `pollSCM('H/15 * * * *')` | `H` spreads load across the hour rather than firing every job at :00. Omit the directive for a manual-only pipeline | same |
| `environment` | `KEY = 'value'`, `KEY = credentials('id')` | At stage level it applies to that stage only — the scope that matters for secrets | same |
| `when` | `branch`, `expression`, `changeset`, `allOf`/`anyOf`/`not` | Skips a stage without failing the run; the mechanism for "only on `main`" | same |
| `parallel` | Sibling stages inside `stage { parallel { } }` | Add `failFast true` when one failure makes the rest pointless | same |
| `post` | `always`, `success`, `failure`, `unstable`, `changed`, `cleanup` | `always` runs whatever happened; `cleanup` runs last, after the others | same |

## Bounding a run

| Option | Prevents | Source |
|---|---|---|
| `timeout` | A hung batchmode editor holding an agent until a human notices — the default is no limit at all | [Pipeline: Basic Steps](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/) |
| `disableConcurrentBuilds()` | Two runs of the same job racing over one workspace or one licence seat | [Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) |
| `buildDiscarder(logRotator(...))` | Retained artifacts filling the controller's disk, which takes down every job at once | same |
| `retry(n)` | Nothing worth having, applied to a build step — retrying a deterministic failure wastes an agent three times. Reserve it for a genuinely flaky network step | [Pipeline: Basic Steps](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/) |

## The human gate

```groovy
stage('Distribute to testers') {
    steps {
        timeout(time: 30, unit: 'MINUTES') {            // an unanswered prompt must release the agent
            input message: 'Distribute this build to the QA group?', ok: 'Distribute'
        }
        // … the upload step, per `firebase-app-distribution`
    }
}
```

`input` pauses the run until a person answers. Two rules make it safe: wrap it in `timeout`, because an
un-timed prompt holds its executor indefinitely and a small fleet stalls behind it; and place it *before* the
step that reaches the outside world, never after, since approval is only meaningful ahead of the action.

## Useful environment values

| Value | Holds | Typical use |
|---|---|---|
| `env.BUILD_NUMBER` | The job's monotonic run counter | The Android version code and iOS build number, per `unity-batchmode-cli` |
| `env.BRANCH_NAME` | The branch, in a multibranch job | `when { branch 'main' }` gating |
| `env.GIT_COMMIT` | The checked-out commit | Release notes and traceability from an artifact back to a commit |
| `env.WORKSPACE` | The absolute workspace path | `-projectPath` for the Unity invocation |
| `currentBuild.result` | The result so far, inside `post` | Deciding what to report and where |
