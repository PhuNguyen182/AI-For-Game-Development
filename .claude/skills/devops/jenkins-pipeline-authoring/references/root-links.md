# Root Links — Jenkins Pipeline documentation and the plugins assumed here

Source: [Jenkins User Handbook — Pipeline](https://www.jenkins.io/doc/book/pipeline/), [Pipeline Steps Reference](https://www.jenkins.io/doc/pipeline/steps/), [Jenkins Plugins index](https://plugins.jenkins.io/).
Covers: SKILL.md §4 — **"Keep the pipeline in the repository and the controller free of job logic"**.

Jenkins documents the pipeline *language* centrally and every *step* in the plugin that provides it, so a
step named here exists only if its plugin is installed on the controller the job runs on. There is no
version to pin: `jenkins.io` documents the current LTS and its plugins independently. When a step is
rejected as unknown, the cause is almost always a missing plugin rather than a syntax error — check the
controller's installed set before rewriting anything.

| Root | Holds | Source |
|---|---|---|
| Pipeline handbook | Concepts, `Jenkinsfile` structure, multibranch, shared libraries | [Pipeline](https://www.jenkins.io/doc/book/pipeline/) |
| Declarative syntax | The complete directive reference — `agent`, `options`, `parameters`, `when`, `post` | [Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) |
| Steps reference | Every step, grouped by the plugin that ships it | [Pipeline steps](https://www.jenkins.io/doc/pipeline/steps/) |
| Credentials | Credential kinds, scopes, and how a job is granted one | [Using credentials](https://www.jenkins.io/doc/book/using/using-credentials/) |
| Shared libraries | `@Library`, `vars/`, and how library code is loaded | [Shared libraries](https://www.jenkins.io/doc/book/pipeline/shared-libraries/) |

## Plugins this skill's steps come from

| Step used here | Plugin | Source |
|---|---|---|
| `withCredentials` | Credentials Binding | [credentials-binding](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/) |
| `lock`, `milestone` | Lockable Resources · Pipeline Milestone | [lockable-resources](https://www.jenkins.io/doc/pipeline/steps/lockable-resources/) |
| `junit` | JUnit | [junit](https://www.jenkins.io/doc/pipeline/steps/junit/) |
| `archiveArtifacts`, `stash`, `unstash`, `input`, `timeout`, `retry` | Pipeline: Basic Steps · Core | [workflow-basic-steps](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/) |
| `cleanWs` | Workspace Cleanup | [ws-cleanup](https://plugins.jenkins.io/ws-cleanup/) |
| `sh` | Pipeline: Nodes and Processes | [workflow-durable-task-step](https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/) |

State the plugin dependency in the pipeline's own documentation. A `Jenkinsfile` that silently assumes four
plugins is portable only to controllers that already happen to have them, and the failure on a fresh
controller reads as a syntax error rather than as a missing install.
