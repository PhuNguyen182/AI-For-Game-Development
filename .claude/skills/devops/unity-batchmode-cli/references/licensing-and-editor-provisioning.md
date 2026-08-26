# Licensing and Editor Provisioning — getting an editor onto an agent

Source: [Managing your Unity licence](https://docs.unity3d.com/Manual/ManagingYourUnityLicense.html), [Unity Editor command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html), [Unity Hub CLI](https://docs.unity3d.com/hub/manual/HubCLI.html).
Covers: SKILL.md §4 — **"Pin the editor version from `ProjectVersion.txt` before writing anything else"**, **"Treat the licence as its own stage that always releases"**.

What an ephemeral agent must obtain before it can build anything, and what it must give back. The failure
this file exists to prevent is silent and cumulative: activations that are never returned exhaust the seat
pool over days, and the first symptom is an unrelated job failing at a step that has always worked.

## Installing the editor the project pins

| Command | Purpose | Source |
|---|---|---|
| `unityhub --headless editors --installed` | Lists what the agent already has, so a warm agent skips the install | [Unity Hub CLI](https://docs.unity3d.com/hub/manual/HubCLI.html) |
| `unityhub --headless install --version <v> --changeset <c>` | Installs an exact editor. The changeset is required for any version that is not the current latest, and comes from `m_EditorVersionWithRevision` in `ProjectVersion.txt` | same |
| `unityhub --headless install-modules --version <v> --module <m> --childModules` | Adds a platform module to an installed editor; `--childModules` pulls its dependencies | same |
| Module ids | `android`, `ios`, `windows-mono`, `mac-mono`, `linux-mono`, `webgl` — an Android build also needs the JDK, SDK and NDK child modules | same |

On Linux the Hub is commonly an AppImage, invoked as `./UnityHub.AppImage --headless …`; the arguments are
identical. Confirm the id list against the Hub on the agent rather than assuming it — module ids change more
often than the command shape does.

## The three ways an agent gets a licence

| Route | How it works | When it is the right one | Source |
|---|---|---|---|
| **Floating / licensing server** | A `services-config.json` on the agent points at the licensing server; the editor leases a licence per run and releases it on exit, with no per-job credentials | A fleet of agents, or any agent that is destroyed after each run — the only route with no activation state to leak | [Managing your Unity licence](https://docs.unity3d.com/Manual/ManagingYourUnityLicense.html) |
| **Seat activation** | `-batchmode -quit -serial <serial> -username <user> -password <pass>`, then `-returnlicense` when finished | A small, fixed number of agents where a licensing server does not exist | [Command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html) |
| **Manual activation file** | `-createManualActivationFile` produces an `.alf`, which is exchanged for a `.ulf` and applied with `-manualLicenseFile <file>.ulf` | An agent with no outbound access to Unity's licensing endpoints | same |

`services-config.json` is read from a platform directory (`/usr/share/unity3d/config/` on Linux,
`/Library/Application Support/Unity/config/` on macOS, `C:\ProgramData\Unity\config\` on Windows). Treat the
exact path as something to confirm on the agent — it is host configuration, not something a job should write
on every run.

## The return is not optional

```groovy
// The shape the pipeline enforces, whatever the build did — see `jenkins-pipeline-authoring`.
post {
    always {
        sh 'unity-editor -batchmode -quit -returnlicense -logFile -'
    }
}
```

A seat activated by a run that crashed, was aborted, or hit its timeout stays consumed. Because the pool is
shared across jobs and people, the cost lands on someone who did nothing wrong and has no way to trace it —
which is why the return belongs in `post { always }` rather than after the build step.

## Secrets discipline

| Rule | Reason |
|---|---|
| The serial, username and password reach the process only through the job's credential binding | A value written into a pipeline file is unrecoverable from history without a rewrite |
| Never echo the activation command line | Some editor versions log their own arguments; a serial printed into a build log is a leaked credential in an artifact the whole team can read |
| Never commit a `.ulf` or a `services-config.json` containing tokens | They are credentials, and `security-reviewer` treats them as such |

## Failure signatures this stage produces

| Log line | Means | Source |
|---|---|---|
| `Failed to activate/update license` | The credentials or the licensing server were wrong or unreachable; no project code ever compiled | [Managing your Unity licence](https://docs.unity3d.com/Manual/ManagingYourUnityLicense.html) |
| `No valid Unity Editor license found` | The editor started with no licence at all — the activation stage did not run, or ran on a different agent | same |
| `License is currently in use` / seat exhaustion | An earlier run never returned its seat | same |

Every one of these means the run stopped before compilation. A failure at this stage is never evidence about
the code under build, and routing it to a feature's author wastes a full cycle — `ci-pipeline-failure-triage`
holds that distinction.