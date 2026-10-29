# Fault-Domain Signals

Sources: [a] vitals/anr, [b] IL2CPP manual, [c] Apple "Diagnosing issues using crash reports and device logs", [d] vitals — paths from the SKILL.md `Docs:` roots.

Assumes the trace is resolved; otherwise `crash-anr-symbolication` owns it.

## Recognising each domain

Check in table order, stop at the first match (outward from what the project controls); no ownable domain -> non-actionable.

| Domain | Resolved frames look like | Complication |
|---|---|---|
| Game code | This project's namespaces, shown as native frames on a shipped build | An IL2CPP frame still carries the original type and method [b] |
| Unity engine | Engine and runtime functions, scripting backend, allocator and job internals | Often faults on input the game gave it: game code's defect [b] |
| Third-party SDK | A vendor library, frequently on its own thread | An SDK crashing on the main thread inside a game-registered callback is still the SDK's frame [d] |
| System library | Platform libraries with no application code above, or main thread blocked in a platform call | Correlates with one manufacturer or OS version: the segmentation signal [a] |

**Caveat:** an unfamiliar engine or platform frame at the top is where a fixable game-code defect is most often misfiled; it reads as the cause when it is the victim.

## Mixed stacks

| Case | Attribution |
|---|---|
| Game code calls SDK, SDK faults | SDK; the call site is context |
| SDK calls back, game code faults | Game code |
| Game hands the engine invalid state, engine faults | Game code; the defect is the state given [b] |
| Deliberate abort with a message | Read the message first; a guard that fired names the precondition, not the location [c] |
| Several threads | Crash: the crashing thread decides. ANR: every thread matters, the blocker may not be main [a] |

## Confidence evidence [d]

| Observation | Supports |
|---|---|
| One manufacturer or OS version | System-library or driver fault, or a device-specific SDK path |
| Every device and version | Code the project or its dependencies ship |
| Starts at a specific app version | Whatever changed in that release; often faster than reading the stack |
| Disappears when a dependency is disabled | SDK attribution confirmed, not just correlated |
| One sample | Insufficient for a verdict; request more |
