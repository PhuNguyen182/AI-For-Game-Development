# Root Links — Unity Job System (Unity 6)

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors this folder to the Unity 6 manual's job-system section and the
`Unity.Jobs` scripting reference. Anything this skill cites resolves under one
of these roots; anything that does not is out of scope for the skill, not
merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Manual — job system | Worker threads, job types, dependencies, native containers, safety | [Write multithreaded code with the job system](https://docs.unity3d.com/6000.5/Documentation/Manual/job-system.html) |
| Scripting API — `Unity.Jobs` | `IJob`, `IJobFor`, `JobHandle` and their members | [IJob](https://docs.unity3d.com/ScriptReference/Unity.Jobs.IJob.html) |
| Manual — Burst package | The versioned Burst manual this skill applies but does not tune | [Burst](https://docs.unity3d.com/Manual/com.unity.burst.html) |

**Critical caveat**: the `job-system-*` manual pages are served both
unversioned (`docs.unity3d.com/Manual/…`, resolving to current docs) and
version-pinned (`docs.unity3d.com/6000.5/Documentation/Manual/…`). Sibling
files in this folder use whichever form the page publishes; when wording
matters for a specific Editor version, substitute that version into the pinned
form rather than trusting the unversioned page.
