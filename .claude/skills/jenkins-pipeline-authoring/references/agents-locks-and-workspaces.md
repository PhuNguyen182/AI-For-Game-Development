# Agents, Locks and Workspaces

Sources: [a] book/pipeline/syntax/ (agent), [b] pipeline/steps/lockable-resources/, [c] pipeline/steps/workflow-basic-steps/ (stash) — below the SKILL.md `Docs:` base.

## Labels

| Stage | Needs | Label |
|---|---|---|
| Edit/Play Mode tests | Unity of the pinned version | `linux && unity` |
| Android build | Unity + Android module, JDK, SDK, NDK | `linux && unity && android` |
| PC build | standalone module for target OS | `linux && unity` or `windows && unity` |
| iOS build and signing | macOS, Xcode, keychain; no substitute | `macos && xcode` |
| Distribution upload | network and CLI only | any build agent |

Use capability expressions (`&&`, `||`, `!`), not host names: a host name breaks when the host is rebuilt and blocks a second agent from taking load.

```groovy
pipeline {
    agent none
    stages {
        stage('Android') { agent { label 'linux && unity && android' } steps { /* ... */ } }
        stage('iOS')     { agent { label 'macos && xcode' }           steps { /* ... */ } }
    }
}
```

## Locks [b]

| Resource | Lock as |
|---|---|
| Unity project path (two editors corrupt `Library/`) | `lock('unity-project-<name>')` |
| Licence seats (finite pool, per `unity-batchmode-cli`) | `lock(label: 'unity-license', quantity: 1)` |
| Physical test device | `lock('device-<id>')` |

```groovy
lock(resource: 'unity-project-hergarden') { sh './ci/build-android.sh' }
```

**Caveat:** `disableConcurrentBuilds()` stops one job racing itself; only a lock stops different jobs racing over a resource.

## Workspaces

| Fact | Consequence |
|---|---|
| Each agent has its own workspace; a per-stage agent gets a new empty directory | A Linux file does not exist on macOS |
| Workspace persists between runs on one agent | Warm `Library/` possible, and a stale one |
| `cleanWs()` empties it; `deleteDir()` removes the current dir | Cleaning in `post { cleanup }` costs the next run its cache; do it deliberately |
| Stash is scoped to one run | For moving files between stages, never storage |

```groovy
stash name: 'android-artifact', includes: 'build/android/**'   // producing stage
unstash 'android-artifact'                                       // consuming stage
```

Stashes travel through the controller: archive hundreds of MB (an `.aab` plus symbols) on the producing agent and fetch it instead.

## Checkout

- Declarative checks out on every agent; suppress with `options { skipDefaultCheckout() }` and call `checkout scm`.
- A per-stage agent clones again on that node.
- Git LFS content is not fetched unless the job is configured for it; placeholders look like asset corruption (`git-unity-repo`).
