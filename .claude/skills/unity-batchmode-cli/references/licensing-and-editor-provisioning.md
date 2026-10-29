# Licensing and editor provisioning

Source: [Managing your Unity licence](https://docs.unity3d.com/Manual/ManagingYourUnityLicense.html), [Command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html), [Hub CLI](https://docs.unity3d.com/hub/manual/HubCLI.html).

Unreturned activations exhaust the seat pool over days; the first symptom is an unrelated job failing.

## Install the pinned editor
- `unityhub --headless editors --installed`: list, so a warm agent skips the install.
- `unityhub --headless install --version <v> --changeset <c>`: changeset (from `m_EditorVersionWithRevision`) is required for any non-latest version.
- `unityhub --headless install-modules --version <v> --module <m> --childModules`: add a platform module and its dependencies.
- Module ids: `android`, `ios`, `windows-mono`, `mac-mono`, `linux-mono`, `webgl`; Android also needs JDK, SDK and NDK child modules. Confirm ids against the Hub on the agent; they change more than the command shape.
- Linux AppImage: `./UnityHub.AppImage --headless …`, same arguments.

## Licence routes
| Route | How | Right when |
|---|---|---|
| Floating / licensing server | `services-config.json` on the agent; editor leases per run and releases on exit | Fleets or ephemeral agents; no activation state to leak |
| Seat activation | `-batchmode -quit -serial <serial> -username <user> -password <pass>`, then `-returnlicense` | Few fixed agents, no licensing server |
| Manual file | `-createManualActivationFile` gives `.alf`, exchanged for `.ulf`, applied with `-manualLicenseFile` | No outbound access to Unity licensing |

`services-config.json` lives in host config: `/usr/share/unity3d/config/` (Linux), `/Library/Application Support/Unity/config/` (macOS), `C:\ProgramData\Unity\config\` (Windows). Confirm on the agent; a job must not rewrite it each run.

## Return always
```groovy
post { always { sh 'unity-editor -batchmode -quit -returnlicense -logFile -' } }
```
A seat from a crashed, aborted or timed-out run stays consumed, and the cost lands on someone else.

## Secrets
- Serial, username and password reach the process only through the job's credential binding.
- Never echo the activation command line; some versions log their arguments.
- Never commit a `.ulf` or a token-bearing `services-config.json`.

## Failure signatures
All stop the run before compilation, so they say nothing about the code under build; do not route them to a feature author (`ci-pipeline-failure-triage`).
- `Failed to activate/update license`: bad credentials or unreachable server.
- `No valid Unity Editor license found`: activation stage did not run, or ran on another agent.
- `License is currently in use` / seat exhaustion: an earlier run never returned its seat.
