# Agents, Locks and Workspaces — where a stage runs and what it collides with

Source: [Pipeline syntax — agent](https://www.jenkins.io/doc/book/pipeline/syntax/), [Lockable Resources plugin](https://www.jenkins.io/doc/pipeline/steps/lockable-resources/), [Pipeline: Basic Steps — stash](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/).
Covers: SKILL.md §4 — **"Choose the agent by label, and give every platform-bound stage the label its toolchain requires"**, **"Serialise everything that opens the Unity project behind a named lock"**.

Placement and contention, which are the same problem seen from two sides: a stage must land on a node that
can do the work, and must not land there at the same time as something it would corrupt. Both failures are
invisible in the pipeline file and obvious only in a run that already wasted an hour.

## Labels — what each stage requires

| Stage | Needs | Label expression |
|---|---|---|
| Edit Mode / Play Mode tests | A Unity editor of the pinned version | `linux && unity` |
| Android build | Unity plus the Android module, JDK, SDK, NDK | `linux && unity && android` |
| PC build | Unity plus the standalone module for the target OS | `linux && unity` (or `windows && unity` for a native Windows build) |
| iOS build and signing | **macOS**, Xcode, and a keychain — no substitute exists | `macos && xcode` |
| Distribution upload | Network access and the CLI, nothing platform-bound | any build agent |

Label expressions combine with `&&`, `||` and `!`. Prefer a capability expression (`unity && android`) over a
machine name: naming a host makes the pipeline fail the day that host is rebuilt, and prevents a second agent
from ever taking the load.

```groovy
pipeline {
    agent none                                   // forces every stage to declare where it belongs
    stages {
        stage('Android') { agent { label 'linux && unity && android' } steps { /* … */ } }
        stage('iOS')     { agent { label 'macos && xcode' }           steps { /* … */ } }
    }
}
```

## Locks — the contention a Unity pipeline actually has

| Resource | Why it is contended | Lock as |
|---|---|---|
| The Unity project path | Two editors on one `Library/` corrupt each other's import; the damage surfaces later in an unrelated run | `lock('unity-project-<name>')` |
| Licence seats | A finite pool shared across jobs and people, per `unity-batchmode-cli` | `lock(label: 'unity-license', quantity: 1)` |
| A physical test device | One USB device, one run | `lock('device-<id>')` |

```groovy
stage('Build Android') {
    agent { label 'linux && unity && android' }
    steps {
        lock(resource: 'unity-project-hergarden') {
            sh './ci/build-android.sh'
        }
    }
}
```

`disableConcurrentBuilds()` stops one *job* racing itself; a lock stops *different* jobs racing over the same
resource. A pipeline that only has the first is protected until someone adds a second job — which is exactly
when nobody is looking for an import corruption.

## Workspaces — separate per node, and not permanent

| Fact | Consequence |
|---|---|
| Each agent has its own workspace; a per-stage agent means a **new, empty** directory | A file produced on the Linux node does not exist on the macOS node |
| The workspace persists between runs on the same agent unless cleaned | This is what makes a warm `Library/` possible, and what makes a stale one possible |
| `cleanWs()` (Workspace Cleanup) empties it; `deleteDir()` removes the current directory | Cleaning in `post { cleanup }` costs the next run its cache — do it deliberately, not by habit |
| A stashed file set is scoped to one run and discarded afterwards | `stash`/`unstash` is for moving files between stages, never for storing anything |

```groovy
stage('Build') {
    agent { label 'linux && unity && android' }
    steps {
        sh './ci/build-android.sh'
        stash name: 'android-artifact', includes: 'build/android/**'
    }
}
stage('Distribute') {
    agent { label 'linux' }
    steps {
        unstash 'android-artifact'
        // … upload, per `firebase-app-distribution`
    }
}
```

Keep stashes small — they travel through the controller. A multi-hundred-megabyte artifact is better archived
on the producing agent and fetched by the consuming stage, and an `.aab` plus its symbol package is already
at that size.

## Checkout behaviour worth knowing

| Behaviour | Detail |
|---|---|
| Declarative checks out the SCM automatically on every agent | Suppress with `options { skipDefaultCheckout() }` and call `checkout scm` where you want it |
| A per-stage agent checks out again, on that node | The macOS stage gets its own clone; anything generated on Linux must be stashed or archived to reach it |
| Git LFS content is not fetched unless the job is configured for it | A Unity project using LFS builds with placeholder files and fails in ways that look like asset corruption — see `git-unity-repo` |
