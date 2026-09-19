---
name: jenkins-pipeline-authoring
description: >
  Technique for writing a Unity project's `Jenkinsfile` as declarative
  pipeline code — `pipeline`, `agent { label }`, `stages`, `when`,
  `environment { credentials() }`, `withCredentials`, `parameters`,
  `options { timeout, disableConcurrentBuilds, buildDiscarder, timestamps }`,
  `lock` for the single-editor resource, `post { always, failure, cleanup }`,
  `junit`, `archiveArtifacts`, `stash`/`unstash`, `parallel`, `input` gates,
  `triggers { cron, pollSCM }`, multibranch `env.BRANCH_NAME`, shared
  libraries in `vars/`, and `cleanWs`. Not for: the Unity command line a
  stage runs (`unity-batchmode-cli`); signing and packaging
  (`fastlane-mobile-delivery`); the upload step (`firebase-app-distribution`);
  diagnosing a red run (`ci-pipeline-failure-triage`).
---

# Jenkins Pipeline Authoring — declarative pipelines for a Unity project

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Pipeline, step and plugin documentation roots, and which plugins this skill assumes | Starting any task here, or a step turns out not to exist on this controller |
| [declarative-syntax-and-stages.md](references/declarative-syntax-and-stages.md) | The directive set — `agent`, `options`, `parameters`, `triggers`, `when`, `parallel`, `post` — and what each accepts | Composing or restructuring a pipeline |
| [credentials-and-secrets.md](references/credentials-and-secrets.md) | Credential kinds, `environment { credentials() }` against `withCredentials`, scope, and how masking fails | Any stage touches a keystore, an API key, or a service account |
| [agents-locks-and-workspaces.md](references/agents-locks-and-workspaces.md) | Labels, `agent none` with per-stage agents, `lock`, workspace lifetime, and moving files between nodes | The pipeline spans Linux and macOS, or two runs could collide on one project |
| [artifacts-test-reports-and-notifications.md](references/artifacts-test-reports-and-notifications.md) | `junit`, `archiveArtifacts`, `stash`, build status semantics, and reporting from `post` | Wiring what a run publishes and how its result is decided |

## 1. Objective
Produce a pipeline whose result can be trusted without opening it. The failures this prevents are the ones that make CI worse than no CI: a test stage that passes because it produced no results at all, a secret that reaches the log through a transformation Jenkins cannot mask, two runs opening one Unity project and corrupting each other's import, an iOS stage scheduled onto a Linux agent where it can never succeed, and a distribution step that reached real testers because nothing stood between a merge and an upload.

## 2. Role
Act as the CI orchestration specialist for the devops track, on behalf of `ci-cd-engineer`. You own the job definition — what runs, where, in what order, under which credentials, and what the run publishes. What each step actually executes belongs to the neighbouring skills.

## 3. When to invoke this skill
- A `Jenkinsfile` is being written, restructured, or extended with a stage.
- A pipeline must span platforms — an Android or PC build on Linux and an iOS build on macOS.
- A stage needs a credential, and the question is which binding and at what scope.
- Two runs could collide over one Unity project, one licence seat, or one device.
- A run's result is wrong: green with no tests executed, or red for something the pipeline itself caused.
- Delivery must be gated behind a human rather than triggered by a merge.
- Negative trigger: the Unity invocation inside a stage — flags, `-executeMethod`, exit codes, licence activation — that is `unity-batchmode-cli`.
- Negative trigger: how an artifact is signed or packaged — that is `fastlane-mobile-delivery`.
- Negative trigger: the upload command and its tester groups — that is `firebase-app-distribution`.
- Negative trigger: deciding what a failed run means and who owns it — that is `ci-pipeline-failure-triage`.
- Negative trigger: authoring the tests a stage runs, or what they assert — that is `unity-test-framework` and `qa-automation-engineer`.

## 4. How to use this skill
1. **Keep the pipeline in the repository and the controller free of job logic** — a `Jenkinsfile` is reviewable, diffable and restorable; a job assembled in the web UI is none of those and is lost with the controller. Configure the job as "Pipeline script from SCM" and put every decision in the file, per [declarative-syntax-and-stages.md](references/declarative-syntax-and-stages.md); confirm each step's plugin exists on the controller first, per [root-links.md](references/root-links.md).
2. **Choose the agent by label, and give every platform-bound stage the label its toolchain requires** — an iOS stage needs macOS with Xcode, and a pipeline that spans platforms declares `agent none` at the top with a per-stage agent below it, per [agents-locks-and-workspaces.md](references/agents-locks-and-workspaces.md). A stage that lands on the wrong node fails after the checkout, having proven nothing.
3. **Serialise everything that opens the Unity project behind a named lock** — two editors on one project path corrupt each other's `Library/`, and a shared licence pool has a finite number of seats. `lock` names that contention explicitly instead of relying on nobody starting two runs at once, per [agents-locks-and-workspaces.md](references/agents-locks-and-workspaces.md).
4. **Bind every secret at the narrowest scope that works** — a credential bound inside the one stage that needs it, per [credentials-and-secrets.md](references/credentials-and-secrets.md), rather than a pipeline-level `environment` block that exposes it to every `sh` in the file, including the ones added later by someone who did not know it was there.
5. **Bound the run before writing its first stage** — `timeout` so a hung batchmode build cannot occupy an agent indefinitely, `disableConcurrentBuilds` where the job touches shared state, and `buildDiscarder` so build logs and artifacts do not fill the controller's disk. An unbounded pipeline fails the whole queue, not just itself.
6. **Publish the test report as a real result set, and treat an empty one as a failure** — Unity writes NUnit 3 XML, which the `junit` publisher does not read natively, and a crashed test stage that produced no XML is indistinguishable from one that passed unless the publisher is told to object. Both traps are closed in [artifacts-test-reports-and-notifications.md](references/artifacts-test-reports-and-notifications.md); together they are the most common way a Unity pipeline reports green while testing nothing.
7. **Collect logs and reports from `post { always }`, and artifacts only on success** — a failed run is the one whose log matters most, and a step that only runs on success guarantees its absence exactly then.
8. **Put a human between the pipeline and anything that reaches people** — an `input` gate before a distribution stage, wrapped in its own timeout so an unanswered prompt releases the agent rather than holding it, per [declarative-syntax-and-stages.md](references/declarative-syntax-and-stages.md). Delivery to real testers is the GD's decision, per `ci-cd-engineer`'s guardrails.
9. **Extract a shared library only when a second pipeline actually needs the same logic** — one `vars/` function serving one job is indirection with no payer, and it moves the logic back out of the repository the job lives in (YAGNI, per `coding-principles.md`'s YAGNI section).
10. **Name every input you had to assume — labels, credential ids, branch triggers — in the output rather than defaulting it** — a pipeline that references a credential id nobody created fails on its first run at the step that matters, and the fix is a five-second answer somebody could have given up front.

## 5. Specific goals / tasks this skill performs
- Composing a declarative `Jenkinsfile` with stages, agents, options, parameters and triggers.
- Splitting a multi-platform pipeline across labelled agents and moving artifacts between them.
- Binding credentials at stage scope and keeping their values out of the log.
- Serialising Unity-project access and licence use with named locks.
- Publishing NUnit results, archiving artifacts, and making the build status say what happened.
- Gating delivery behind an explicit human approval with a bounded wait.
- Out of scope: the Unity command line (`unity-batchmode-cli`); signing and packaging (`fastlane-mobile-delivery`); the upload itself (`firebase-app-distribution`); failure routing (`ci-pipeline-failure-triage`); test authoring (`unity-test-framework`).

## 6. Output format
```
## Jenkins Pipeline — <job name and purpose>
- File: <path to the Jenkinsfile, and the job type it is configured as>
- Agents: <label per stage, and why each is required>
- Stages: <order, and what fails the run at each>
- Locks: <resource names, and the contention each protects>
- Credentials: <ids and binding scope — ids only, never values>
- Triggers: <what starts it; manual where nothing should>
- Publishes: <test report, artifacts, logs, and from which post condition>
- Human gates: <where an input stands between the run and the outside world>
- Layer: Editor-only
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this pipeline does not cover>
- Latent concerns: <what holds only under current conditions — one macOS agent, a lock that assumes one project>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a nightly pipeline must build Android on Linux, build iOS on macOS, run Edit Mode tests once, and offer distribution to QA.
- Output: `agent none` at the top; a test stage and an Android stage on `label 'linux && unity'`, an iOS stage on `label 'macos && xcode'`; both Unity stages inside `lock('unity-project')`; the Android artifact `stash`ed for the delivery stage because the nodes have separate workspaces; `junit allowEmptyResults: false` on the test XML; `archiveArtifacts onlyIfSuccessful: true`; a final stage behind `input` with a 30-minute `timeout`, so an unanswered prompt frees the agent.

**Example 2**
- Input: "Put the keystore password in the pipeline's `environment` block so every stage can use it — it's masked in the log anyway."
- Output: declined on both counts. Pipeline-level scope exposes the secret to every step in the file including ones added later, and masking only covers the literal value: a script that base64-encodes or interpolates it prints something Jenkins does not recognise and does not mask. Bound with `withCredentials` inside the signing stage only, per §4 step 4.

**Example 3**
- Input: a pipeline reports success on a night when the test stage crashed before writing any results.
- Output: traced to `junit` publishing with empty results tolerated. Changed to `allowEmptyResults: false` so the missing report fails the run, and the test step's exit status is checked rather than swallowed — per §4 step 6, an empty result set is a failure, not a pass.

## 8. Edge cases & guardrails
- Never write a secret value into the `Jenkinsfile`, a parameter default, or a `sh` line — bind it, and remember masking protects only the untransformed value.
- Never let two runs open the same Unity project without a lock; the corruption surfaces later, in an unrelated run, as an import error nobody can reproduce.
- Never publish test results with empty results allowed, and never decide a run passed from the absence of a failure message.
- Never trigger a store submission or a distribution to real testers from a branch event; a human gate is the difference between a pipeline and an accident.
- Never leave a stage unbounded by `timeout` — a hung Unity process holds an agent until someone notices, which on a small fleet stops every other job.
- Never disable a failing stage or mark it as tolerable to get a green run; report what blocks it, per `verification-standards.md`'s honesty constraints.
- If the agent labels, credential ids, or branch triggers were not supplied, state the assumption in the output rather than inventing a value that fails on first run.
