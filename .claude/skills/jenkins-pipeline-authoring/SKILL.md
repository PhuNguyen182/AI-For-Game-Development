---
name: jenkins-pipeline-authoring
description: "Write a Unity project's declarative Jenkinsfile: agent labels, stages, withCredentials, parameters, lock, stash, junit/NUnit reports, input gate, shared libraries. Use when authoring Jenkins CI."
user-invocable: false
---

# Jenkins Pipeline Authoring

Not for: the Unity command line a stage runs (`unity-batchmode-cli`), signing and packaging (`fastlane-mobile-delivery`), the upload step (`firebase-app-distribution`), diagnosing a red run (`ci-pipeline-failure-triage`), authoring the tests (`unity-test-framework`).
Docs: base https://www.jenkins.io/doc/ — `book/pipeline/` (syntax, shared libraries), `book/using/using-credentials/`, `pipeline/steps/` (steps, by plugin) — unversioned, tracks current LTS. A step is rejected as unknown when its plugin is missing, not for syntax: check the controller's plugins first.

| Reference | Read when |
|---|---|
| [declarative-syntax-and-stages.md](references/declarative-syntax-and-stages.md) | Composing or restructuring a pipeline, bounding a run, adding the `input` gate, or checking which plugin provides a step |
| [credentials-and-secrets.md](references/credentials-and-secrets.md) | A stage touches a keystore, API key or service account |
| [agents-locks-and-workspaces.md](references/agents-locks-and-workspaces.md) | The pipeline spans Linux and macOS, or two runs could collide on one project |
| [artifacts-test-reports-and-notifications.md](references/artifacts-test-reports-and-notifications.md) | Wiring test reports, archives and notifications, or deciding build status |

## Steps
1. **Keep job logic in the repository** — configure the job as "Pipeline script from SCM"; no logic in the web UI. Confirm each step's plugin exists on the controller.
2. **Pick agents by capability label** — `agent none` at the top, a per-stage agent below; an iOS stage needs `macos && xcode`. Per [agents-locks-and-workspaces.md](references/agents-locks-and-workspaces.md).
3. **Wrap every stage that opens the Unity project in a named `lock`** — two editors on one `Library/` corrupt each other, and licence seats are finite. Per the same file.
4. **Bind each secret at stage scope with `withCredentials`**, never a pipeline-level `environment` block. Per [credentials-and-secrets.md](references/credentials-and-secrets.md).
5. **Bound the run first** — `timeout`, `disableConcurrentBuilds`, `buildDiscarder`. Per [declarative-syntax-and-stages.md](references/declarative-syntax-and-stages.md).
6. **Publish tests so an empty result set fails** — Unity writes NUnit 3, which `junit` does not read natively. Per [artifacts-test-reports-and-notifications.md](references/artifacts-test-reports-and-notifications.md).
7. **Collect logs and reports in `post { always }`, build artifacts only on success.**
8. **Put an `input` gate, wrapped in `timeout`, before any stage that reaches people** — delivery to testers is the GD's decision (`ci-cd-engineer`).
9. **Extract a shared library only when a second pipeline needs the same logic** (YAGNI).
10. **List every assumed label, credential id and trigger in the output**; never invent a value that fails on first run.

## Never
- Write a secret value into the `Jenkinsfile`, a parameter default or a `sh` line.
- Trigger a store submission or tester distribution from a branch event.
- Leave a stage unbounded by `timeout`.
- Disable a failing stage or tolerate its failure to get green; report what blocks it.
- Decide a run passed from the absence of a failure message.

## Output
```
## Jenkins Pipeline — <job and purpose>
- File: <Jenkinsfile path, job type>
- Agents: <label per stage, why>
- Stages: <order, what fails the run at each>
- Locks: <resource, contention protected>
- Credentials: <ids and binding scope — never values>
- Triggers: <what starts it; manual where nothing should>
- Publishes: <reports, artifacts, logs, post condition>
- Human gates: <where an input stands before the outside world>
- Assumed: <labels, ids, triggers not supplied>
- Known limitations: <...>
```

## Example
- "Put the keystore password in the `environment` block, it's masked anyway" → declined: pipeline scope exposes it to every step, and masking misses any transformed value (base64, interpolation). Bound with `withCredentials` in the signing stage only.
